import re
import json
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from db.postgres import SessionLocal
from models.behavior import BehaviorLog
from models.mood import MoodLog
from models.pattern import Trigger
from models.memory import EpisodicMemory, AssociativeLink, SchemaConsolidation

# --- Legacy Trigger Detection (Phase 2 Compat) ---

def context_normalization(context: str):
    context = context.lower().strip()
    context_map = {
        "coding": ["dev", "programming", "software", "code"],
        "meeting": ["call", "zoom", "sync"],
        "study": ["reading", "learning", "class"]
    }
    for normalized, aliases in context_map.items():
        if context in aliases or context == normalized:
            return normalized
    return context

def detect_triggers_db(db: Session, user_id: str):
    now = datetime.utcnow()
    behaviors = db.query(BehaviorLog).filter(BehaviorLog.user_id == user_id).all()
    moods = db.query(MoodLog).filter(MoodLog.user_id == user_id).all()

    trigger_map = {}
    total_events_map = {}
    time_window_days = 7.0

    for b in behaviors:
        norm_ctx = context_normalization(b.context)
        days_since_event = max((now - b.timestamp).days, 0)
        decay_factor = 0.9 ** days_since_event
        
        total_events_map[norm_ctx] = total_events_map.get(norm_ctx, 0.0) + decay_factor
        
        for m in moods:
            if abs((b.timestamp - m.timestamp).total_seconds()) < 3600:
                key = (norm_ctx, m.mood_type)
                trigger_map[key] = trigger_map.get(key, 0.0) + decay_factor

    db.query(Trigger).filter(Trigger.user_id == user_id).delete()
    
    for (event, emotion), decayed_freq in trigger_map.items():
        if decayed_freq >= 1.0:
            total_occurrences = total_events_map.get(event, decayed_freq)
            confidence = decayed_freq / max(total_occurrences, 1.0)
            stability = decayed_freq / time_window_days
            trigger = Trigger(
                user_id=user_id,
                event=event,
                emotion=emotion,
                frequency=decayed_freq,
                confidence=confidence,
                stability=stability
            )
            db.add(trigger)
    db.commit()

def detect_triggers(user_id: str):
    """Fires trigger detection in the background."""
    def background_task(uid):
        db = SessionLocal()
        try:
            detect_triggers_db(db, uid)
        finally:
            db.close()
    
    threading.Thread(target=background_task, args=(user_id,)).start()


# --- Phase 11: Long-Term Episodic & Associative Memory Engine ---

STOPWORDS = {
    "i", "me", "my", "myself", "we", "our", "you", "your", "he", "she", "it",
    "the", "a", "an", "and", "or", "but", "if", "because", "as", "what", "which",
    "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "have",
    "has", "had", "do", "does", "did", "to", "at", "by", "for", "with", "about",
    "in", "out", "on", "off", "again", "then", "once", "here", "there", "when"
}

def extract_keywords(text: str) -> List[str]:
    tokens = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    return [t for t in tokens if t not in STOPWORDS]

def compute_similarity(query_tokens: set, episode_tokens: set, q_valence: float, e_valence: float) -> float:
    if not query_tokens or not episode_tokens:
        jaccard = 0.0
    else:
        intersection = len(query_tokens.intersection(episode_tokens))
        union = len(query_tokens.union(episode_tokens))
        jaccard = intersection / max(union, 1)

    valence_proximity = max(0.0, 1.0 - abs(q_valence - e_valence))
    return round((0.6 * jaccard) + (0.4 * valence_proximity), 3)


class CognitiveMemoryEngine:
    @staticmethod
    def store_episode(
        db: Session,
        user_id: int,
        scenario_text: str,
        episode_type: str = "decision_outcome",
        trigger_context: Optional[str] = None,
        cognitive_distortion: Optional[str] = None,
        emotional_valence: float = 0.0,
        intensity: float = 0.5,
        intervention_applied: Optional[str] = None,
        outcome_delta: float = 0.0,
        key_learnings: Optional[str] = None
    ) -> EpisodicMemory:
        keywords = extract_keywords(scenario_text)
        
        # Calculate salience / importance score based on emotion intensity and outcome magnitude
        salience = min(1.0, max(0.2, (intensity * 0.5) + (abs(outcome_delta) * 0.5)))
        
        episode = EpisodicMemory(
            user_id=user_id,
            episode_type=episode_type,
            scenario_text=scenario_text,
            trigger_context=trigger_context or "general_reflection",
            cognitive_distortion=cognitive_distortion or "None detected",
            emotional_valence=round(emotional_valence, 2),
            intensity=round(intensity, 2),
            intervention_applied=intervention_applied or "self_observation",
            outcome_delta=round(outcome_delta, 2),
            key_learnings=key_learnings or f"Observed pattern in context: {trigger_context or 'general'}.",
            embedding_json=json.dumps(keywords),
            importance_score=round(salience, 3),
            created_at=datetime.utcnow(),
            last_accessed_at=datetime.utcnow()
        )
        db.add(episode)
        db.commit()
        db.refresh(episode)

        # Update Associative Graph edges based on episode attributes
        CognitiveMemoryEngine.reinforce_associations(
            db=db,
            user_id=user_id,
            trigger_context=trigger_context,
            cognitive_distortion=cognitive_distortion,
            intervention_applied=intervention_applied,
            outcome_delta=outcome_delta
        )

        return episode

    @staticmethod
    def reinforce_associations(
        db: Session,
        user_id: int,
        trigger_context: Optional[str],
        cognitive_distortion: Optional[str],
        intervention_applied: Optional[str],
        outcome_delta: float
    ):
        """Reinforces or creates Hebbian-style links between psychological concepts."""
        links_to_update = []
        
        # 1. Trigger -> Distortion link
        if trigger_context and cognitive_distortion and cognitive_distortion != "None detected":
            links_to_update.append((
                f"trigger:{trigger_context.lower()}",
                f"distortion:{cognitive_distortion.lower()}",
                "triggers",
                0.15
            ))

        # 2. Distortion / Trigger -> Intervention link
        target_concept = f"distortion:{cognitive_distortion.lower()}" if (cognitive_distortion and cognitive_distortion != "None detected") else f"trigger:{trigger_context.lower() if trigger_context else 'stress'}"
        if intervention_applied:
            relation = "mitigated_by" if outcome_delta >= 0 else "escalates_to"
            delta_weight = 0.2 if outcome_delta >= 0 else -0.15
            links_to_update.append((
                target_concept,
                f"intervention:{intervention_applied.lower()}",
                relation,
                delta_weight
            ))

        for source, target, rel, delta in links_to_update:
            existing = db.query(AssociativeLink).filter_by(
                user_id=user_id,
                source_node=source,
                target_node=target,
                relation_type=rel
            ).first()

            if existing:
                existing.occurrences += 1
                existing.weight = min(1.0, max(0.05, round(existing.weight + delta, 3)))
                existing.updated_at = datetime.utcnow()
            else:
                new_link = AssociativeLink(
                    user_id=user_id,
                    source_node=source,
                    target_node=target,
                    relation_type=rel,
                    weight=max(0.1, min(1.0, 0.5 + delta)),
                    occurrences=1,
                    updated_at=datetime.utcnow()
                )
                db.add(new_link)

        db.commit()

    @staticmethod
    def retrieve_relevant_episodes(
        db: Session,
        user_id: int,
        query_text: str,
        q_valence: float = -0.3,
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """Retrieves semantically and psychologically relevant historical episodes."""
        episodes = db.query(EpisodicMemory).filter_by(user_id=user_id).order_by(EpisodicMemory.created_at.desc()).limit(100).all()
        if not episodes:
            return []

        query_tokens = set(extract_keywords(query_text))
        scored = []

        for ep in episodes:
            try:
                ep_tokens = set(json.loads(ep.embedding_json)) if ep.embedding_json else set(extract_keywords(ep.scenario_text))
            except Exception:
                ep_tokens = set(extract_keywords(ep.scenario_text))

            sim = compute_similarity(query_tokens, ep_tokens, q_valence, ep.emotional_valence)
            
            # Combine similarity with episode salience/importance
            composite_score = round((sim * 0.7) + (ep.importance_score * 0.3), 3)
            scored.append((composite_score, ep))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:top_k]

        # Update access count on retrieved memories
        for _, ep in top:
            ep.access_count += 1
            ep.last_accessed_at = datetime.utcnow()
        db.commit()

        results = []
        for score, ep in top:
            results.append({
                "id": ep.id,
                "episode_type": ep.episode_type,
                "scenario": ep.scenario_text,
                "trigger_context": ep.trigger_context,
                "cognitive_distortion": ep.cognitive_distortion,
                "intervention_applied": ep.intervention_applied,
                "outcome_delta": ep.outcome_delta,
                "key_learnings": ep.key_learnings,
                "similarity": score,
                "created_at": ep.created_at.isoformat() if ep.created_at else None
            })
        return results

    @staticmethod
    def get_associative_graph(db: Session, user_id: int) -> Dict[str, Any]:
        """Returns nodes and edges of the user's psychological associative graph."""
        links = db.query(AssociativeLink).filter_by(user_id=user_id).order_by(AssociativeLink.weight.desc()).limit(50).all()
        
        nodes = set()
        edges = []
        for link in links:
            nodes.add(link.source_node)
            nodes.add(link.target_node)
            edges.append({
                "source": link.source_node,
                "target": link.target_node,
                "relation": link.relation_type,
                "weight": link.weight,
                "occurrences": link.occurrences
            })

        formatted_nodes = []
        for n in nodes:
            category = "concept"
            if n.startswith("trigger:"): category = "trigger"
            elif n.startswith("distortion:"): category = "distortion"
            elif n.startswith("intervention:"): category = "intervention"
            elif n.startswith("state:"): category = "state"
            
            formatted_nodes.append({
                "id": n,
                "label": n.split(":", 1)[-1].replace("_", " ").title(),
                "category": category
            })

        return {
            "nodes": formatted_nodes,
            "edges": edges,
            "total_links": len(edges)
        }

    @staticmethod
    def consolidate_memories(db: Session, user_id: int) -> List[Dict[str, Any]]:
        """Sleep-like consolidation process: clusters past episodes into higher-order mental schemas."""
        episodes = db.query(EpisodicMemory).filter_by(user_id=user_id).all()
        if len(episodes) < 3:
            # Seed foundational schema if data is sparse
            schemas = db.query(SchemaConsolidation).filter_by(user_id=user_id).all()
            if not schemas:
                initial_schema = SchemaConsolidation(
                    user_id=user_id,
                    theme="Cognitive Calibration Baseline",
                    consolidated_insight="Initial psychological baseline established: active deliberate breaks mitigate fatigue spikes effectively.",
                    evidence_count=1,
                    confidence=0.85
                )
                db.add(initial_schema)
                db.commit()
                schemas = [initial_schema]
            return [{"theme": s.theme, "insight": s.consolidated_insight, "confidence": s.confidence} for s in schemas]

        # Aggregate intervention outcomes across contexts
        context_success = {}
        for ep in episodes:
            ctx = ep.trigger_context or "general"
            act = ep.intervention_applied or "rest"
            key = (ctx, act)
            if key not in context_success:
                context_success[key] = {"positive": 0, "negative": 0, "total": 0}
            context_success[key]["total"] += 1
            if ep.outcome_delta > 0:
                context_success[key]["positive"] += 1
            else:
                context_success[key]["negative"] += 1

        consolidations = []
        for (ctx, act), data in context_success.items():
            if data["total"] >= 2:
                win_rate = round(data["positive"] / data["total"] * 100, 0)
                theme = f"Response Pattern in {ctx.replace('_', ' ').title()}"
                insight = (
                    f"In '{ctx}', intervention '{act.replace('_', ' ')}' demonstrated a {win_rate:.0f}% success rate "
                    f"across {data['total']} logged episodes."
                )
                
                existing = db.query(SchemaConsolidation).filter_by(user_id=user_id, theme=theme).first()
                if existing:
                    existing.consolidated_insight = insight
                    existing.evidence_count = data["total"]
                    existing.confidence = min(0.95, 0.6 + (data["total"] * 0.05))
                    existing.updated_at = datetime.utcnow()
                else:
                    new_sc = SchemaConsolidation(
                        user_id=user_id,
                        theme=theme,
                        consolidated_insight=insight,
                        evidence_count=data["total"],
                        confidence=min(0.95, 0.6 + (data["total"] * 0.05))
                    )
                    db.add(new_sc)
                consolidations.append({"theme": theme, "insight": insight, "confidence": 0.85})

        db.commit()
        return consolidations

    @staticmethod
    def retrospective_query(db: Session, user_id: int, question: str) -> Dict[str, Any]:
        """Provides grounded answers to 'When did I feel like this before and what worked?'."""
        relevant = CognitiveMemoryEngine.retrieve_relevant_episodes(db, user_id, question, top_k=3)
        schemas = db.query(SchemaConsolidation).filter_by(user_id=user_id).order_by(SchemaConsolidation.updated_at.desc()).limit(3).all()

        if not relevant:
            return {
                "answer": "No directly matching past episodes found in autobiographical memory yet. As you log scenarios and outcomes, your cognitive twin will establish precedent patterns.",
                "matched_episodes": [],
                "active_schemas": [s.consolidated_insight for s in schemas],
                "confidence": 0.3
            }

        successful_past_interventions = [ep["intervention_applied"] for ep in relevant if ep["outcome_delta"] > 0]
        dominant_intervention = max(set(successful_past_interventions), key=successful_past_interventions.count) if successful_past_interventions else "mindful_pacing"

        answer = (
            f"Based on {len(relevant)} similar past episode(s), you previously encountered this tension in context '{relevant[0]['trigger_context']}'. "
            f"Historically, deploying '{dominant_intervention.replace('_', ' ')}' yielded positive cognitive delta, while passive rumination increased friction."
        )

        return {
            "answer": answer,
            "recommended_strategy": dominant_intervention,
            "matched_episodes": relevant,
            "active_schemas": [s.consolidated_insight for s in schemas],
            "confidence": 0.85
        }
