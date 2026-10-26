from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.auth import get_db, get_current_user
from models.user import User
from models.evolution import EvolutionSnapshot
from services.evolution_engine import generate_snapshot_if_needed
from services.trajectory_engine import compute_trajectory
from services.strategy_engine import evaluate_strategy_shift
from services.reflection_engine import generate_reflection

router = APIRouter(prefix="/api/v1/evolution", tags=["evolution"])

@router.get("/dashboard")
def get_evolution_dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # 1. Trigger Lazy Eval
    generate_snapshot_if_needed(db, user.id)
    
    # 2. Get Snapshots for Timeline & Trajectory
    snapshots = db.query(EvolutionSnapshot).filter_by(user_id=user.id).order_by(EvolutionSnapshot.created_at.asc()).all()
    trajectory = compute_trajectory(db, user.id)
    
    # 3. Strategy shift
    strategy_shift = evaluate_strategy_shift(db, user.id)
    
    # 4. Final reflection
    last_snap = snapshots[-1] if snapshots else None
    reflection = generate_reflection(last_snap, trajectory, strategy_shift) if last_snap else "Start logging to generate your cognitive reflection."
    
    snaps_out = []
    for s in snapshots:
        snaps_out.append({
           "week": s.week,
           "stress_avg": s.stress_avg,
           "archetype": s.archetype,
           "top_strategy": s.top_strategy,
           "dissonance": s.dissonance
        })
        
    return {
        "trajectory": trajectory,
        "timeline": snaps_out,
        "strategy_shift": strategy_shift,
        "reflection": reflection
    }
