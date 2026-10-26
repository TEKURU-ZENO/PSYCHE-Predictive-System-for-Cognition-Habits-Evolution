from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.auth import get_db, get_current_user
from models.user import User
from services.learning_engine import process_explicit_feedback
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/intervention", tags=["intervention"])

class FeedbackRequest(BaseModel):
    state_key: str
    action: str
    rating: float # 1.0 for thumbs up, -1.0 for thumbs down

from models.event import EventLog

@router.post("/feedback")
def submit_feedback(data: FeedbackRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    process_explicit_feedback(db, user.id, data.state_key, data.action, data.rating)
    event = EventLog(user_id=user.id, type="explicit_feedback", metadata_col=f'{{"state": "{data.state_key}", "action": "{data.action}", "rating": {data.rating}}}')
    db.add(event)
    db.commit()
    return {"msg": "Feedback integrated"}

from models.personalization import UserPolicy

@router.get("/playbook")
def get_playbook(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    policies = db.query(UserPolicy).filter(UserPolicy.user_id == user.id, UserPolicy.visits >= 1).order_by(UserPolicy.q_score.desc()).limit(5).all()
    
    strategies = []
    for p in policies:
        # Extract target emotion
        parts = p.state.split("_")
        emotion = parts[1] if len(parts) > 1 else "general"
        
        strategies.append({
           "action": p.action.replace("_", " ").title(),
           "emotion": emotion,
           "score": p.q_score,
           "visits": p.visits,
           "confidence": p.visits / (p.visits + 5)
        })
    return strategies
