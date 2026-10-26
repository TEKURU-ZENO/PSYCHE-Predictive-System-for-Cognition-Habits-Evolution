from typing import Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from models.user_state import UserState
from models.mood import MoodLog
from models.behavior import BehaviorLog
from models.pattern import Trigger
from models.memory import EpisodicMemory, AssociativeLink, SchemaConsolidation
from models.post_mortem import PostMortemReport, RedTeamAuditLog
from models.proactive import ProactiveAlert, CounterfactualBranch
from models.event import EventLog

class PrivacyVaultService:
    @staticmethod
    def export_full_vault(db: Session, user_id: int) -> Dict[str, Any]:
        """Exports the complete autobiographical and psychological twin data bundle."""
        uid_str = str(user_id)
        
        user_state = db.query(UserState).filter_by(user_id=uid_str).first()
        moods = db.query(MoodLog).filter_by(user_id=uid_str).order_by(MoodLog.timestamp.desc()).limit(100).all()
        behaviors = db.query(BehaviorLog).filter_by(user_id=uid_str).order_by(BehaviorLog.timestamp.desc()).limit(100).all()
        triggers = db.query(Trigger).filter_by(user_id=uid_str).all()
        episodes = db.query(EpisodicMemory).filter_by(user_id=user_id).all()
        graph_links = db.query(AssociativeLink).filter_by(user_id=user_id).all()
        schemas = db.query(SchemaConsolidation).filter_by(user_id=user_id).all()
        post_mortems = db.query(PostMortemReport).filter_by(user_id=user_id).all()
        alerts = db.query(ProactiveAlert).filter_by(user_id=user_id).all()

        return {
            "vault_metadata": {
                "user_id": user_id,
                "exported_at": datetime.utcnow().isoformat(),
                "platform": "Psych-AI Cognitive Twin Platform",
                "format_version": "2.0.0"
            },
            "user_state": {
                "emotion": user_state.emotion if user_state else "neutral",
                "intensity": user_state.intensity if user_state else 0.5,
                "updated_at": user_state.updated_at.isoformat() if user_state and user_state.updated_at else None
            },
            "episodic_memories": [
                {
                    "id": e.id,
                    "type": e.episode_type,
                    "scenario": e.scenario_text,
                    "trigger": e.trigger_context,
                    "intervention": e.intervention_applied,
                    "outcome_delta": e.outcome_delta,
                    "key_learnings": e.key_learnings,
                    "created_at": e.created_at.isoformat() if e.created_at else None
                }
                for e in episodes
            ],
            "associative_graph": [
                {
                    "source": g.source_node,
                    "target": g.target_node,
                    "relation": g.relation_type,
                    "weight": g.weight,
                    "occurrences": g.occurrences
                }
                for g in graph_links
            ],
            "consolidated_schemas": [
                {
                    "theme": s.theme,
                    "insight": s.consolidated_insight,
                    "confidence": s.confidence
                }
                for s in schemas
            ],
            "post_mortem_corrections": [
                {
                    "failed_action": p.failed_action,
                    "responsible_agent": p.responsible_agent,
                    "root_cause": p.root_cause,
                    "adaptation": p.corrective_adaptation
                }
                for p in post_mortems
            ],
            "triggers_detected": [
                {"event": t.event, "emotion": t.emotion, "confidence": t.confidence} for t in triggers
            ],
            "recent_mood_history": [
                {"mood": m.mood_type, "intensity": m.intensity, "timestamp": m.timestamp.isoformat()} for m in moods
            ]
        }

    @staticmethod
    def prune_episode(db: Session, user_id: int, episode_id: int) -> bool:
        """Right to be forgotten: selectively prunes an episodic memory."""
        ep = db.query(EpisodicMemory).filter_by(id=episode_id, user_id=user_id).first()
        if ep:
            db.delete(ep)
            db.commit()
            return True
        return False
