from sqlalchemy.orm import Session
from models.evolution import EvolutionSnapshot

def moving_average(data_list, window=3):
    if not data_list: return 0
    return sum(data_list[-window:]) / min(len(data_list), window)

def compute_trajectory(db: Session, user_id: str):
    snapshots = db.query(EvolutionSnapshot).filter_by(user_id=user_id).order_by(EvolutionSnapshot.created_at.asc()).all()
    
    if len(snapshots) < 2:
        return {"direction": "stable", "confidence": 0.0, "slope": 0.0, "consistency": 0.0}
        
    stress_points = [s.stress_avg for s in snapshots]
    
    recent_avg = moving_average(stress_points, 3)
    past_avg = moving_average(stress_points[:-1], 3)
    
    slope = recent_avg - past_avg
    
    direction = "improving" if slope < -0.05 else ("declining" if slope > 0.05 else "stable")
    consistency = sum(1 for i in range(1, len(stress_points)) if (stress_points[i] - stress_points[i-1]) <= 0) / max(len(stress_points)-1, 1)
    confidence = min(0.95, len(snapshots) / 10.0 + consistency * 0.3)
    
    return {
        "direction": direction,
        "slope": round(slope, 3),
        "confidence": round(confidence, 2),
        "consistency": round(consistency, 2)
    }
