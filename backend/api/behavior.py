from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from models.user import User
from models.behavior import BehaviorLog
from models.event import EventLog
from schemas.behavior import LogBehaviorRequest
from api.auth import get_db, get_current_user
from services.memory_engine import detect_triggers

router = APIRouter(prefix="/api/v1/behavior", tags=["behavior"])

@router.post("/log")
def log_behavior(data: LogBehaviorRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    behavior = BehaviorLog(
        user_id=user.id,
        type=data.type,
        value=data.value,
        context=data.context
    )
    db.add(behavior)
    
    db.commit()
    event_count = db.query(EventLog).filter(EventLog.user_id == user.id).count()

    if event_count % 5 == 0:
        background_tasks.add_task(detect_triggers, user.id)

    return {"msg": "Behavior logged"}
