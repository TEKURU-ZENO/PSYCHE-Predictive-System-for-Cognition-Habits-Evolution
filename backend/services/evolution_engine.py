from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models.evolution import EvolutionSnapshot
from models.mood import MoodLog
from models.personalization import UserPolicy
from services.meta_engine import generate_meta_profile

def generate_snapshot_if_needed(db: Session, user_id: str):
    last_snap = db.query(EvolutionSnapshot).filter_by(user_id=user_id).order_by(EvolutionSnapshot.created_at.desc()).first()
    now = datetime.utcnow()
    
    if last_snap:
        days_since = (now - last_snap.created_at).days
        if days_since < 7:
            return None # Not ready yet
            
    recent_moods = db.query(MoodLog).filter(MoodLog.user_id == user_id, MoodLog.timestamp >= now - timedelta(days=7)).all()
    if len(recent_moods) < 3:
        return None # Not enough data
        
    stress_moods = [m.intensity for m in recent_moods if m.mood_type in ["stressed", "fatigued"]]
    stress_avg = sum(stress_moods) / max(len(stress_moods), 1) if stress_moods else 0.0
    
    meta = generate_meta_profile(db, user_id)
    
    top_policy = db.query(UserPolicy).filter(UserPolicy.user_id == user_id, UserPolicy.visits >= 3).order_by(UserPolicy.q_score.desc()).first()
    top_strategy = top_policy.action if top_policy else "none"
    
    week_str = f"{now.year}-W{now.isocalendar()[1]}"
    
    snap = EvolutionSnapshot(
        user_id=user_id,
        week=week_str,
        archetype=meta["archetype"]["dominant"],
        stress_avg=stress_avg,
        dissonance=meta["dissonance"]["dissonance"],
        top_strategy=top_strategy,
        created_at=now
    )
    db.add(snap)
    db.commit()
    db.refresh(snap)
    return snap
