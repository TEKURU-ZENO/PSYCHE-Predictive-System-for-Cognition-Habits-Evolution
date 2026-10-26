from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from api.auth import get_db, get_current_user
from models.user import User
from models.proactive import ProactiveAlert, CounterfactualBranch
from services.proactive_monitor import ProactiveMonitor
from services.counterfactual_engine import CounterfactualEngine

router = APIRouter(prefix="/api/v1/proactive", tags=["proactive"])
cf_router = APIRouter(prefix="/api/v1/counterfactual", tags=["counterfactual"])

class CounterfactualInput(BaseModel):
    scenario: str
    current_emotion: Optional[str] = "stressed"
    current_intensity: Optional[float] = 0.7
    decision_hash: Optional[str] = None

@router.get("/status")
def get_ambient_status(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ProactiveMonitor.run_ambient_scan(db, user.id)

@router.post("/scan")
def trigger_ambient_scan(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ProactiveMonitor.run_ambient_scan(db, user.id)

@router.post("/acknowledge/{alert_id}")
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    alert = db.query(ProactiveAlert).filter_by(id=alert_id, user_id=user.id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.is_acknowledged = True
    db.commit()
    return {"status": "acknowledged", "alert_id": alert_id}

@cf_router.post("/simulate")
def simulate_counterfactual(data: CounterfactualInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    branches = CounterfactualEngine.simulate_branches(
        db=db,
        user_id=user.id,
        scenario=data.scenario,
        current_emotion=data.current_emotion or "stressed",
        current_intensity=data.current_intensity if data.current_intensity is not None else 0.7,
        decision_hash=data.decision_hash
    )
    return {
        "scenario": data.scenario,
        "branches": branches,
        "recommended_branch": branches[0] if branches else None
    }

@cf_router.get("/history")
def get_counterfactual_history(limit: int = 10, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    records = db.query(CounterfactualBranch).filter_by(user_id=user.id).order_by(CounterfactualBranch.created_at.desc()).limit(limit).all()
    return [
        {
            "id": r.id,
            "scenario": r.scenario,
            "branch_name": r.branch_name,
            "projected_stress_48h": r.projected_stress_48h,
            "projected_burnout_risk": r.projected_burnout_risk,
            "projected_dissonance": r.projected_dissonance,
            "cognitive_energy_delta": r.cognitive_energy_delta,
            "expected_q_value": r.expected_q_value,
            "recommendation_rank": r.recommendation_rank,
            "tradeoff_analysis": r.tradeoff_analysis,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in records
    ]
