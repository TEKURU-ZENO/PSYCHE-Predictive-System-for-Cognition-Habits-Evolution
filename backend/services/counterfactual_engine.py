from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from models.proactive import CounterfactualBranch
from models.personalization import UserPolicy
from models.memory import EpisodicMemory
from models.mood import MoodLog

CANDIDATE_PATHS = [
    {
        "name": "Active Cognitive Break",
        "action_key": "take_break",
        "stress_modifier": -0.35,
        "burnout_modifier": -0.40,
        "dissonance_modifier": -0.25,
        "energy_delta": 0.55,
        "tradeoff": "Immediate tension mitigation with rapid cognitive energy restoration; temporarily delays short-term output but prevents systemic exhaustion."
    },
    {
        "name": "Socratic Reframe & Task Chunking",
        "action_key": "reframe_and_chunk",
        "stress_modifier": -0.20,
        "burnout_modifier": -0.20,
        "dissonance_modifier": -0.45,
        "energy_delta": 0.25,
        "tradeoff": "Dismantles cognitive distortions and perfectionist pressure while sustaining moderate execution momentum."
    },
    {
        "name": "Direct Push-Through",
        "action_key": "push_through",
        "stress_modifier": 0.30,
        "burnout_modifier": 0.45,
        "dissonance_modifier": 0.35,
        "energy_delta": -0.50,
        "tradeoff": "Achieves immediate output in the next 2-4 hours, but severely accelerates burnout risk and risks severe emotional crash within 48 hours."
    },
    {
        "name": "Strategic Disengagement & Rest",
        "action_key": "sleep_and_reset",
        "stress_modifier": -0.45,
        "burnout_modifier": -0.50,
        "dissonance_modifier": -0.10,
        "energy_delta": 0.80,
        "tradeoff": "Complete psychological reset and somatic recovery; optimal if late-night vulnerability is elevated or emotional saturation is critical."
    }
]

class CounterfactualEngine:
    @staticmethod
    def simulate_branches(
        db: Session,
        user_id: int,
        scenario: str,
        current_emotion: str = "stressed",
        current_intensity: float = 0.7,
        decision_hash: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        # 1. Fetch relevant user policies to pull empirical Q-values
        policies = db.query(UserPolicy).filter_by(user_id=str(user_id)).all()
        policy_map = {p.action: p.q_score for p in policies} if policies else {}

        # 2. Check autobiographical episodes for past precedent
        past_episodes = db.query(EpisodicMemory).filter_by(user_id=user_id).order_by(EpisodicMemory.created_at.desc()).limit(20).all()
        precedent_outcomes = {}
        for ep in past_episodes:
            if ep.intervention_applied:
                if ep.intervention_applied not in precedent_outcomes:
                    precedent_outcomes[ep.intervention_applied] = []
                precedent_outcomes[ep.intervention_applied].append(ep.outcome_delta)

        branches_output = []

        for candidate in CANDIDATE_PATHS:
            action_key = candidate["action_key"]

            # Base projections derived from current emotional intensity
            proj_stress = max(0.05, min(0.98, current_intensity + candidate["stress_modifier"]))
            proj_burnout = max(0.05, min(0.98, (current_intensity * 0.7) + candidate["burnout_modifier"] + 0.3))
            proj_dissonance = max(0.05, min(0.95, 0.4 + candidate["dissonance_modifier"]))
            energy_delta = candidate["energy_delta"]

            # Pull empirical Q-score or default
            empirical_q = policy_map.get(action_key, 0.5)

            # Historical precedent adjustment
            if action_key in precedent_outcomes:
                avg_delta = sum(precedent_outcomes[action_key]) / len(precedent_outcomes[action_key])
                empirical_q = max(0.1, min(0.99, empirical_q + (avg_delta * 0.2)))

            # Calculate composite Expected Cognitive Payoff
            # Payoff = High Q-score + High Energy Delta - Projected Burnout - Projected Stress
            expected_payoff = round(
                (empirical_q * 0.35) + 
                ((energy_delta + 1.0) / 2.0 * 0.25) + 
                ((1.0 - proj_burnout) * 0.25) + 
                ((1.0 - proj_stress) * 0.15),
                3
            )

            branch = {
                "branch_name": candidate["name"],
                "action_key": action_key,
                "projected_stress_48h": round(proj_stress, 2),
                "projected_burnout_risk": round(proj_burnout, 2),
                "projected_dissonance": round(proj_dissonance, 2),
                "cognitive_energy_delta": round(energy_delta, 2),
                "expected_q_value": round(empirical_q, 2),
                "expected_payoff": expected_payoff,
                "tradeoff_analysis": candidate["tradeoff"]
            }
            branches_output.append(branch)

        # Rank branches based on expected payoff
        branches_output.sort(key=lambda b: b["expected_payoff"], reverse=True)
        for idx, b in enumerate(branches_output, 1):
            b["recommendation_rank"] = idx

        # Persist top branches into DB for auditability
        for b in branches_output:
            record = CounterfactualBranch(
                user_id=user_id,
                scenario=scenario,
                decision_hash=decision_hash,
                branch_name=b["branch_name"],
                projected_stress_48h=b["projected_stress_48h"],
                projected_burnout_risk=b["projected_burnout_risk"],
                projected_dissonance=b["projected_dissonance"],
                cognitive_energy_delta=b["cognitive_energy_delta"],
                expected_q_value=b["expected_q_value"],
                recommendation_rank=b["recommendation_rank"],
                tradeoff_analysis=b["tradeoff_analysis"],
                created_at=datetime.utcnow()
            )
            db.add(record)
        db.commit()

        return branches_output
