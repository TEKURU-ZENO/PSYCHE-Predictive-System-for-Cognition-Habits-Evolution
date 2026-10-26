from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
from db.postgres import SessionLocal
from models.user import User
from models.mood import MoodLog
from models.event import EventLog, EventType
from models.user_state import UserState
from schemas.mood import LogMoodRequest
from api.auth import get_db, get_current_user
from services.intervention_engine import select_nudge
from services.learning_engine import process_implicit_feedback

router = APIRouter(prefix="/api/v1/mood", tags=["mood"])

def get_smoothed_mood(db: Session, user_id: str, new_intensity: float):
    recent = db.query(MoodLog).filter(MoodLog.user_id == user_id).order_by(MoodLog.timestamp.desc()).limit(2).all()
    moods = [new_intensity] + [m.intensity for m in recent]
    weights = [0.5, 0.3, 0.2]
    score = 0
    for i, intensity in enumerate(moods[:3]):
        # if there are fewer than 3, weights sum might not be 1. Normalize if needed, but for MVP keep it simple
        try:
            score += intensity * weights[i]
        except IndexError:
            break
    return score

@router.post("/log")
def log_mood(data: LogMoodRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # 1. Log the mood itself
    mood = MoodLog(user_id=user.id, mood_type=data.mood_type, intensity=data.intensity)
    db.add(mood)

    # 2. Log event
    event = EventLog(user_id=user.id, type=EventType.MOOD_LOGGED, metadata_col=json.dumps({"mood": data.mood_type, "intensity": data.intensity}))
    db.add(event)
    
    # 3. Calculate smoothed intensity
    smoothed_intensity = get_smoothed_mood(db, user.id, data.intensity)
    
    # 4. Update Derived UserState
    user_state = db.query(UserState).filter(UserState.user_id == user.id).first()
    if not user_state:
        user_state = UserState(user_id=user.id)
        db.add(user_state)
    user_state.current_emotion = data.mood_type
    user_state.intensity = smoothed_intensity
    user_state.updated_at = datetime.utcnow()
    db.commit()

    # 4.1 Process Implicit Feedback Asynchronously
    def background_learning(uid):
        db_bg = SessionLocal()
        try:
           process_implicit_feedback(db_bg, uid)
        finally:
           db_bg.close()
    
    background_tasks.add_task(background_learning, user.id)

    # 5. Cooldown Check 
    ten_mins_ago = datetime.utcnow() - timedelta(minutes=10)
    recent_nudge = db.query(EventLog).filter(EventLog.user_id == user.id, EventLog.type == EventType.NUDGE_SHOWN, EventLog.timestamp >= ten_mins_ago).first()

    nudge = None
    if not recent_nudge:
        nudge = select_nudge(db, user.id, data.mood_type, smoothed_intensity, context="general")
        if nudge:
            db.add(EventLog(user_id=user.id, type=EventType.NUDGE_SHOWN, metadata_col=json.dumps(nudge)))

    db.commit()

    return {
        "msg": "Logged",
        "nudge": nudge
    }
