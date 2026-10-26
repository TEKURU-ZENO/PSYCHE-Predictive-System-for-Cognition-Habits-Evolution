from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.auth import get_db, get_current_user
from models.user import User
from models.mood import MoodLog
from models.pattern import Trigger
from models.user_state import UserState
from services.prediction_engine import predict_next_mood, detect_early_warnings
from services.simulation_engine import simulate_scenario
from services.llm_service import generate_grounded_text
from services.prompt_engine import build_context
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/predict", tags=["prediction"])

@router.get("/mood")
def get_mood_prediction(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    moods = db.query(MoodLog).filter(MoodLog.user_id == user.id).order_by(MoodLog.timestamp.asc()).limit(10).all()
    # compute EMA sequentially
    return predict_next_mood(moods)

@router.get("/risk")
def get_risk(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    moods = db.query(MoodLog).filter(MoodLog.user_id == user.id).order_by(MoodLog.timestamp.asc()).limit(10).all()
    triggers = db.query(Trigger).filter(Trigger.user_id == user.id).all()
    warning = detect_early_warnings(moods, triggers)
    if not warning:
        return {}
        
    context = build_context(
        user_state={"emotion": moods[-1].mood_type if moods else "neutral"},
        signals=warning,
        basis=[f"risk:{warning.get('type')}"]
    )
    llm = generate_grounded_text(context, "Explain this psychological risk clearly and calmly in 2 sentences.")
    
    return {
        **warning,
        "explanation": llm.get("text", warning.get("message", "High risk detected.")),
        "system_version": {"core": "v1.0", "rl": "v1.2", "meta": "v1.1", "llm": "v1.0"}
    }

class SimulateRequest(BaseModel):
    scenario: str

@router.post("/simulate")
def simulate(data: SimulateRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    user_state = db.query(UserState).filter(UserState.user_id == user.id).first()
    emotion = user_state.current_emotion if user_state else "neutral"
    triggers = db.query(Trigger).filter(Trigger.user_id == user.id).all()
    
    formatted_triggers = [{"event": t.event, "emotion": t.emotion} for t in triggers]
    
    return simulate_scenario(data.scenario, {
        "emotion": emotion,
        "triggers": formatted_triggers
    })
