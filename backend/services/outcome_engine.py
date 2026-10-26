import json
from models.event import EventLog
from db.postgres import get_new_session

def push_real_outcome(decision_id: str, success: bool, delta: float = 0.0, outcome_confidence: float = 1.0, window_hours: int = 1):
    """
    Updates a DECISION_MEMORY event with real-world effectiveness parameters.
    """
    db = get_new_session()
    try:
        # Credit Assignment: Pull the last 3 pending logs within window
        decision_logs = db.query(EventLog).filter(EventLog.type == "DECISION_MEMORY").order_by(EventLog.id.desc()).limit(3).all()
        
        weight = 0.5 if outcome_confidence < 0.5 else 1.0
        applied_delta = delta * weight

        for idx, decision_log in enumerate(decision_logs):
            meta = json.loads(decision_log.metadata_col)
            
            # Decay credit backward (most recent gets most credit)
            temporal_discount = 1.0 / (idx + 1)
            
            meta["outcome"] = {
                "success": success,
                "delta": applied_delta * temporal_discount,
                "effectiveness_score": (1.0 if success else -1.0) * weight,
                "tracked_at": "now",
                "window": f"{window_hours}h"
            }
            decision_log.metadata_col = json.dumps(meta)
            
        db.commit()
    finally:
        db.close()
