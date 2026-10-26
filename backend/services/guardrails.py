import json
from models.event import EventLog
from db.postgres import get_new_session

def run_ethical_guardrails(user_id: str, proposed_action: str) -> dict:
    db = get_new_session()
    try:
        # Prevent Harmful Action Loops: Check if the exact proposed action failed in the last 3 cycles
        logs = db.query(EventLog).filter(
            EventLog.user_id == user_id, 
            EventLog.type == "DECISION_MEMORY"
        ).order_by(EventLog.id.desc()).limit(3).all()
        
        failure_loop_count = 0
        for log in logs:
            meta = json.loads(log.metadata_col)
            if meta.get("decision") == proposed_action and meta.get("outcome", {}).get("success") == False:
                failure_loop_count += 1
                
        # If the same action was repeatedly prescribed and failed...
        if failure_loop_count >= 2:
            return {
                "blocked": True,
                "reason": f"System Guardrail: The action '{proposed_action}' caused repeated failures. Forcing fallback trajectory.",
                "intervention_intensity": "Low"
            }
            
        # 1. Escalation Protocol
        # In a real impl, we'd check current user_state distress level. We approximate by recent events here.
        distress_logs = db.query(EventLog).filter(
            EventLog.user_id == user_id,
            EventLog.type == "MOOD_LOGGED"
        ).order_by(EventLog.id.desc()).limit(2).all()
        
        if len(distress_logs) == 2:
            high_distress = all(json.loads(l.metadata_col).get("intensity", 0) > 0.8 for l in distress_logs)
            negative_emotion = all(json.loads(l.metadata_col).get("emotion", "") in ["anxious", "depressed", "panicked"] for l in distress_logs)
            if high_distress and negative_emotion:
                return {
                    "blocked": True,
                    "reason": "Escalation Protocol: Extreme distress detected. DO NOT simulate therapist. Returning grounding suggestions and human support links.",
                    "intervention_intensity": "Critical",
                    "override_action": "grounding_and_support_links"
                }

        # 2. Dependency & Analysis Fatigue Detection
        recent_queries = db.query(EventLog).filter(
            EventLog.user_id == user_id,
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
