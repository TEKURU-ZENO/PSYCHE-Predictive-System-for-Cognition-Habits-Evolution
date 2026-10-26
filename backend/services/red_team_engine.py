import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from models.post_mortem import RedTeamAuditLog

SYCOPHANCY_KEYWORDS = [
    "you are completely right to avoid",
    "just isolate yourself",
    "give up on them",
    "you can never change",
    "no point in trying"
]

TOXIC_POSITIVITY_KEYWORDS = [
    "just smile",
    "good vibes only",
    "everything happens for a reason",
    "it's all in your head"
]

class RedTeamEngine:
    @staticmethod
    def audit_synthesis(
        db: Optional[Session],
        user_id: int,
        scenario: str,
        synthesis: Dict[str, Any],
        weights: Dict[str, float],
        decision_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Adversarially probes the multi-agent consensus before final dispatch.
        Audits for:
        1. Sycophancy / Enabling
        2. Over-optimistic friction minimization
        3. Toxic positivity / Cognitive bypass
        4. High-friction burnout traps
        """
        decision_text = str(synthesis.get("final_decision", "")).lower()
        reasoning_text = str(synthesis.get("reasoning", "")).lower()
        full_text = f"{decision_text} {reasoning_text}"
        scenario_lower = scenario.lower()

        vulnerabilities = []
        critique_score = 0.1  # Baseline healthy skepticism

        # 1. Check Sycophancy & Enabling
        for phrase in SYCOPHANCY_KEYWORDS:
            if phrase in full_text:
                vulnerabilities.append("Sycophantic Enabling: Decision reinforces avoidance or catastrophic isolation.")
                critique_score += 0.40

        # 2. Check Toxic Positivity / Cognitive Bypass
        for phrase in TOXIC_POSITIVITY_KEYWORDS:
            if phrase in full_text:
                vulnerabilities.append("Cognitive Bypass: Superficial cheerfulness detected without genuine grounding.")
                critique_score += 0.35

        # 3. Check Over-Optimistic Friction Minimization under Severe Distress
        is_high_distress_scenario = any(k in scenario_lower for k in [
            "burnout", "can't take this", "exhausted", "panic", "overwhelmed", "hopeless", "failing"
        ])
        if is_high_distress_scenario:
            if any(k in decision_text for k in ["push", "deep work", "grind", "sprint", "execute harder"]):
                vulnerabilities.append("Over-Optimistic Friction Minimization: Urging high-output execution during acute psychological saturation.")
                critique_score += 0.45

        # 4. Check Strategy Dominance Vulnerability (if strategy agent has > 65% weight)
        if weights.get("strategy", 0.0) > 0.65 and is_high_distress_scenario:
            vulnerabilities.append("Agent Groupthink: StrategyAgent disproportionately dominating without sufficient PredictionAgent risk discounting.")
            critique_score += 0.20

        critique_score = round(min(1.0, critique_score), 2)
        veto_triggered = critique_score >= 0.65

        counter_critique = None
        suggested_amendment = None

        if veto_triggered:
            counter_critique = (
                f"Adversarial Red-Team VETO triggered (Risk Score: {int(critique_score * 100)}%). "
                "The proposed consensus risks accelerating user burnout or validating avoidance loops."
            )
            suggested_amendment = (
                "Paced Micro-Engagement: De-escalate immediate pressure. Initiate a 10-minute grounding reset "
                "followed by one isolated micro-step, preserving psychological safety over raw velocity."
            )
        elif vulnerabilities:
            counter_critique = f"Minor adversarial flags detected: {'; '.join(vulnerabilities)}"

        audit_result = {
            "critique_score": critique_score,
            "safety_tier": "Safe" if critique_score < 0.35 else ("Guarded" if critique_score < 0.65 else "Vetoed"),
            "veto_triggered": veto_triggered,
            "vulnerabilities": vulnerabilities,
            "counter_critique": counter_critique,
            "suggested_amendment": suggested_amendment
        }

        # Persist audit record if db session is provided
        if db:
            try:
                log = RedTeamAuditLog(
                    user_id=user_id,
                    decision_hash=decision_hash,
                    critique_score=critique_score,
                    vulnerabilities_detected=json.dumps(vulnerabilities),
                    veto_triggered=veto_triggered,
                    counter_critique=counter_critique,
                    suggested_amendment=suggested_amendment,
                    created_at=datetime.utcnow()
                )
                db.add(log)
                db.commit()
            except Exception:
                db.rollback()

        return audit_result
