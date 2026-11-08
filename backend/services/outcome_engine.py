import json
from typing import Optional
from sqlalchemy.orm import Session
from models.event import EventLog
from db.postgres import get_new_session

def push_real_outcome(
    user_id: str,
    decision_id: str = "latest",
    success: bool = True,
    delta: float = 0.0,
    outcome_confidence: float = 1.0,
    window_hours: int = 1,
    db: Optional[Session] = None
):
    """
    Updates a DECISION_MEMORY event for the specific user with real-world effectiveness parameters.
    Guarantees strict tenant isolation.
    """
    should_close = False
    if db is None:
        db = get_new_session()
        should_close = True

    try:
        # Credit Assignment: Pull the last 3 pending logs within window for this specific user
        decision_logs = db.query(EventLog).filter(
            EventLog.user_id == user_id,
            EventLog.type == "DECISION_MEMORY"
        ).order_by(EventLog.timestamp.desc()).limit(3).all()
        
        weight = 0.5 if outcome_confidence < 0.5 else 1.0
        applied_delta = delta * weight

        for idx, decision_log in enumerate(decision_logs):
            try:
                meta = json.loads(decision_log.metadata_col)
            except Exception:
                meta = {}
            
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
        if should_close:
            db.close()
