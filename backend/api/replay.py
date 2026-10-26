from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.auth import get_db, get_current_user
from models.user import User
from services.replay_engine import ForensicReplayEngine

router = APIRouter(prefix="/api/v1/replay", tags=["replay"])

@router.get("/timeline")
def get_replay_timeline(limit: int = 15, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ForensicReplayEngine.get_timeline(db, user.id, limit=limit)

@router.get("/decision/{decision_hash}")
def replay_decision(decision_hash: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    result = ForensicReplayEngine.verify_and_replay_decision(db, user.id, decision_hash)
    if not result:
        raise HTTPException(status_code=404, detail="Decision hash not found in forensic event memory")
    return result
