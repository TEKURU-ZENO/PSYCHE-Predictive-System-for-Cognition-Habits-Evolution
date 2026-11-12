import json
from models.event import EventLog
from db.postgres import get_new_session
from services.crisis_service import CrisisService

HIGH_DISTRESS_MOODS = {"anxious", "depressed", "panicked", "stressed", "fatigued"}


def run_ethical_guardrails(user_id: str, proposed_action: str) -> dict:
    # 0. Crisis & Self-Harm Immediate Check on proposed action
    crisis_check = CrisisService.evaluate(proposed_action)
    if crisis_check["is_crisis"]:
        return {
            "blocked": True,
            "reason": "Escalation Protocol: Acute self-harm or crisis marker detected in proposed action.",
            "intervention_intensity": "Critical",
            "override_action": "crisis_helpline_intervention",
            "crisis_response": crisis_check["response"]
        }

    uid_str = str(user_id)
    db = get_new_session()
    try:
        # Prevent Harmful Action Loops: Check if the exact proposed action failed in the last 3 cycles
        logs = db.query(EventLog).filter(
            EventLog.user_id == uid_str,
            EventLog.type == "DECISION_MEMORY"
        ).order_by(EventLog.id.desc()).limit(3).all()

        failure_loop_count = 0
        for log in logs:
            meta = json.loads(log.metadata_col)
            if meta.get("decision") == proposed_action and isinstance(meta.get("outcome"), dict) and meta.get("outcome", {}).get("success") is False:
                failure_loop_count += 1

        # If the same action was repeatedly prescribed and failed...
        if failure_loop_count >= 2:
            return {
                "blocked": True,
                "reason": f"System Guardrail: The action '{proposed_action}' caused repeated failures. Forcing fallback trajectory.",
                "intervention_intensity": "Low"
            }

        # 1. Escalation Protocol: inspect both "mood" (logged by mood API) and "emotion"
        distress_logs = db.query(EventLog).filter(
            EventLog.user_id == uid_str,
            EventLog.type == "MOOD_LOGGED"
        ).order_by(EventLog.id.desc()).limit(2).all()

        if len(distress_logs) == 2:
            parsed_logs = [json.loads(l.metadata_col) for l in distress_logs]
            high_distress = all(float(m.get("intensity", 0)) > 0.8 for m in parsed_logs)
            negative_emotion = all(
                str(m.get("mood") or m.get("emotion") or "").lower() in HIGH_DISTRESS_MOODS
                for m in parsed_logs
            )
            if high_distress and negative_emotion:
                return {
                    "blocked": True,
                    "reason": "Escalation Protocol: Extreme distress detected. DO NOT simulate therapist. Returning grounding suggestions and human support links.",
                    "intervention_intensity": "Critical",
                    "override_action": "grounding_and_support_links",
                    "crisis_response": CrisisService.generate_crisis_response(severity="critical")
                }

        # 2. Dependency & Analysis Fatigue Detection
        recent_queries = db.query(EventLog).filter(
            EventLog.user_id == uid_str,
            EventLog.type == "DECISION_MEMORY"
        ).order_by(EventLog.id.desc()).limit(10).all()

        if len(recent_queries) >= 8:
            return {
                "blocked": False,
                "reason": "Dependency Guardrail: High interaction frequency detected. Reducing directiveness and increasing Socratic reflection.",
                "intervention_intensity": "Low",
                "override_action": "socratic_reflection"
            }

        return {"blocked": False, "intervention_intensity": "Moderate"}
    finally:
        db.close()
