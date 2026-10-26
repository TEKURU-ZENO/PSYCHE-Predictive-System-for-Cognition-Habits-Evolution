from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.auth import get_db, get_current_user
from models.user import User
from models.goals import Goal
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/goals", tags=["goals"])

class GoalRequest(BaseModel):
    goal: str
    priority: str

@router.post("")
def add_goal(data: GoalRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    g = Goal(user_id=user.id, goal=data.goal, priority=data.priority)
    db.add(g)
    db.commit()
    return {"status": "ok"}

@router.get("")
def get_goals(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    goals = db.query(Goal).filter_by(user_id=user.id).all()
    return goals
