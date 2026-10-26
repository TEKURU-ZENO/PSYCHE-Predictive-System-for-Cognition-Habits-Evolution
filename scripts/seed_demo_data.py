#!/usr/bin/env python3
"""
Psych-AI Platform - Synthetic Demo Data Seeder
Populates realistic longitudinal cognitive twin records, Hebbian links, and memory schemas.
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Include backend directory in path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))

from db.postgres import SessionLocal, Base, engine
from utils.security import hash_password
from models.user import User
from models.agent_metrics import AgentMetrics, TrustTier
from models.memory import EpisodicMemory, AssociativeLink, SchemaConsolidation
from models.proactive import ProactiveAlert
from models.evolution import EvolutionSnapshot
from models.mood import MoodLog
from models.user_state import UserState

def seed_database():
    print("=" * 65)
    print("PSYCH-AI: SEEDING SYNTHETIC COGNITIVE TWIN DATA")
    print("=" * 65)

    try:
        # Verify tables exist
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Warning: Database engine unreachable ({e}). Cannot execute live seed.", file=sys.stderr)
        return False

    db = SessionLocal()
    try:
        # 1. Seed or retrieve demo user
        demo_email = "analyst@psychai.com"
        user = db.query(User).filter_by(email=demo_email).first()
        if not user:
            user = User(
                email=demo_email,
                name="Alex Mercer",
                password_hash=hash_password("password123")
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"  [+] Created demo user: {user.email} (id: {user.id})")
        else:
            print(f"  [*] Demo user exists: {user.email} (id: {user.id})")

        uid = user.id

        # 2. Seed User State & Baseline Moods
        existing_state = db.query(UserState).filter_by(user_id=uid).first()
        if not existing_state:
            state = UserState(
                user_id=uid,
                current_state="focused",
                stress_level=0.38,
                cognitive_load=0.45,
                energy=0.72,
                timestamp=datetime.utcnow()
            )
            db.add(state)
            print("  [+] Initialized baseline UserState (focused, energy: 0.72)")

        # 3. Seed Agent Reliability Metrics
        core_agents = [
            ("PerceptionAgent", 42, 39, 2, 0, 0.93, 1.25, TrustTier.TRUSTED),
            ("CognitionAgent", 38, 35, 3, 0, 0.92, 1.20, TrustTier.TRUSTED),
            ("PredictionAgent", 45, 37, 5, 1, 0.82, 1.05, TrustTier.STABLE),
            ("StrategyAgent", 44, 41, 2, 0, 0.93, 1.30, TrustTier.TRUSTED),
            ("MetaAgent", 48, 46, 1, 0, 0.96, 1.40, TrustTier.TRUSTED)
        ]
        for name, total, succ, over, to, acc, imp, tier in core_agents:
            metric = db.query(AgentMetrics).filter_by(user_id=uid, agent_id=name).first()
            if not metric:
                metric = AgentMetrics(
                    user_id=uid,
                    agent_id=name,
                    total_invocations=total,
                    successful_contributions=succ,
                    overrides=over,
                    timeouts=to,
                    historical_accuracy=acc,
                    contribution_impact_score=imp,
                    trust_tier=tier,
                    last_success_timestamp=datetime.utcnow()
                )
                db.add(metric)
        print("  [+] Configured telemetry for 5 core agents with calibrated trust tiers.")

        # 4. Seed Episodic Memories
        episodes_data = [
            (
                "Sprint deadline approaching with 3 consecutive context shifts",
                "tight_deadline",
                "catastrophizing",
                -0.45,
                0.70,
                "15m refractory break + task segmentation",
                0.40,
                "Refractory pause completely reversed panic spiral and enabled clear execution."
            ),
            (
                "Post-lunch cognitive fatigue during high-density code review",
                "afternoon_dip",
                "None detected",
                -0.20,
                0.50,
                "Brisk walk + deferred analytical tasks",
                0.35,
                "De-escalating immediate velocity preserved end-of-day reserves."
            ),
            (
                "Unscheduled stakeholder meeting created acute context-switching friction",
                "meeting_overload",
                "all_or_nothing",
                -0.55,
                0.80,
                "Drafted async summary instead of immediate escalation",
                0.30,
                "Async boundaries protected focus block."
            )
        ]
        for scenario, trig, dist, val, inten, inter, delta, learn in episodes_data:
            existing = db.query(EpisodicMemory).filter_by(user_id=uid, scenario_text=scenario).first()
            if not existing:
                ep = EpisodicMemory(
                    user_id=uid,
                    episode_type="decision_outcome",
                    scenario_text=scenario,
                    trigger_context=trig,
                    cognitive_distortion=dist,
                    emotional_valence=val,
                    intensity=inten,
                    intervention_applied=inter,
                    outcome_delta=delta,
                    key_learnings=learn,
                    embedding_json=json.dumps(scenario.lower().split()),
                    importance_score=0.75,
                    created_at=datetime.utcnow() - timedelta(days=2)
                )
                db.add(ep)
        print("  [+] Seeded autobiographical episodic memories.")

        # 5. Seed Hebbian Associative Links
        associations = [
            ("trigger:tight_deadline", "distortion:catastrophizing", 0.78, "triggers"),
            ("distortion:catastrophizing", "intervention:15m_refractory_break", 0.88, "mitigated_by"),
            ("trigger:meeting_overload", "intervention:async_boundary", 0.82, "mitigated_by"),
            ("trigger:late_night_grind", "distortion:over_optimism", 0.65, "triggers")
        ]
        for ca, cb, w, lt in associations:
            link = db.query(AssociativeLink).filter_by(user_id=uid, concept_a=ca, concept_b=cb).first()
            if not link:
                db.add(AssociativeLink(
                    user_id=uid,
                    concept_a=ca,
                    concept_b=cb,
                    weight=w,
                    link_type=lt,
                    updated_at=datetime.utcnow()
                ))
        print("  [+] Seeded Hebbian associative concept network.")

        # 6. Seed Consolidated Schemas
        schemas = [
            (
                "Consecutive unscheduled meetings consistently induce cognitive friction",
                "Mandate 15m refractory gaps before high-velocity analytical tasks.",
                5,
                0.91
            ),
            (
                "Acute burnout warnings followed by sprint execution precipitate multi-day fatigue",
                "Apply early pacing when stress velocity exceeds 0.35.",
                4,
                0.87
            )
        ]
        for pattern, rule, count, conf in schemas:
            sc = db.query(SchemaConsolidation).filter_by(user_id=uid, recurring_pattern=pattern).first()
            if not sc:
                db.add(SchemaConsolidation(
                    user_id=uid,
                    recurring_pattern=pattern,
                    generalized_rule=rule,
                    support_count=count,
                    confidence=conf,
                    consolidated_at=datetime.utcnow()
                ))
        print("  [+] Seeded consolidated behavioral schemas.")

        # 7. Seed Evolution Snapshots
        evolution_records = [
            ("Overloaded Sprinter", 0.68, 0.62, "Pushed through all deadlines", datetime.utcnow() - timedelta(days=21)),
            ("Adapting Analyst", 0.54, 0.72, "Introduced structured breaks", datetime.utcnow() - timedelta(days=14)),
            ("Strategic Architect", 0.38, 0.85, "Paced Segmented Workflows", datetime.utcnow() - timedelta(days=7))
        ]
        for arch, stress, adapt, strat, snap_date in evolution_records:
            snap = db.query(EvolutionSnapshot).filter_by(user_id=uid, archetype=arch).first()
            if not snap:
                db.add(EvolutionSnapshot(
                    user_id=uid,
                    archetype=arch,
                    baseline_stress=stress,
                    adaptability_index=adapt,
                    primary_triggers=["tight_deadline", "meeting_overload"],
                    active_strategy=strat,
                    snapshot_date=snap_date
                ))
        print("  [+] Seeded longitudinal evolution trajectory.")

        # 8. Seed Proactive Ambient Alert
        alert = db.query(ProactiveAlert).filter_by(user_id=uid, alert_type="circadian_rhythm").first()
        if not alert:
            db.add(ProactiveAlert(
                user_id=uid,
                alert_type="circadian_rhythm",
                message="Circadian afternoon dip detected. Preemptive cognitive load reduction scheduled.",
                severity="moderate",
                acknowledged=False,
                created_at=datetime.utcnow()
            ))
            print("  [+] Seeded ambient proactive circadian alert.")

        db.commit()
        print("\n" + "=" * 65)
        print("SEEDING COMPLETE: All synthetic twin models initialized.")
        print("=" * 65)
        return True

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}", file=sys.stderr)
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = seed_database()
    sys.exit(0 if success else 1)
