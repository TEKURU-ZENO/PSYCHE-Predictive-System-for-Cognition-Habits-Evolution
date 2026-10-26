from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.auth import get_db, get_current_user
from models.user_state import UserState
from models.user import User

router = APIRouter(prefix="/api/v1/state", tags=["state"])

@router.get("/current")
def get_state(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    user_state = db.query(UserState).filter(UserState.user_id == user.id).first()

    if not user_state:
        return {"emotion": "neutral"}

    return {
        "emotion": user_state.current_emotion,
        "intensity": user_state.intensity,
        "traits": {
            "O": 0.6,
            "C": 0.5,
            "E": 0.4,
            "A": 0.5,
            "N": 0.5
        }
    }
