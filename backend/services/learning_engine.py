from models.personalization import UserPolicy, PendingReward
from models.mood import MoodLog
from models.system_state import SystemState
from sqlalchemy.orm import Session
from datetime import datetime
from services.meta_learning import adjust_learning_rates

def get_bucket(intensity: float):
    if intensity < 0.3: return "low"
    elif intensity < 0.7: return "medium"
    return "high"

def compute_state(context: str, emotion: str, intensity: float):
    return f"{context}_{emotion}_{get_bucket(intensity)}"

def update_q_value(db: Session, user_id: str, state: str, action: str, reward: float):
    # Reward Clipping
    reward = max(-1.0, min(1.0, reward))
    
    state_cfg = db.query(SystemState).filter_by(user_id=user_id).first()
    alpha = state_cfg.alpha if state_cfg else 0.3
    
    policy = db.query(UserPolicy).filter_by(user_id=user_id, state=state, action=action).first()
    if not policy:
        policy = UserPolicy(user_id=user_id, state=state, action=action, q_score=reward, visits=1)
        db.add(policy)
    else:
        smoothed_reward = (policy.q_score + reward) / 2.0
        delta = smoothed_reward - policy.q_score
        
        # Oscillation Freeze detection
        if abs(delta) > 0.8:
            freeze_updates = True
            from services.health_engine import HealthEngine
            health_status = HealthEngine.check_learning_health(db, user_id)
            if health_status in ["learning_uncertain", "unstable"]:
                HealthEngine.execute_recovery_mode(db, user_id)
                return # Stop processing and rollback
        else:
            policy.q_score = policy.q_score + alpha * delta
            policy.visits += 1
            
            # If stable, update stable_q_score baseline (Phase 10.2)
            if abs(delta) < 0.1:
                policy.stable_q_score = policy.q_score
                
        # Update Entropy (Phase 10.2)
        from services.health_engine import HealthEngine
        all_policies = db.query(UserPolicy).filter_by(user_id=user_id, state=state).all()
        q_values = [p.q_score for p in all_policies]
        if state_cfg:
            state_cfg.policy_entropy = HealthEngine.calculate_entropy(q_values)
    db.commit()

def process_implicit_feedback(db: Session, user_id: str):
    pending = db.query(PendingReward).filter_by(user_id=user_id, resolved=False).all()
    if not pending: return

    for p in pending:
        recent_moods = db.query(MoodLog).filter(
            MoodLog.user_id == user_id, 
            MoodLog.timestamp >= p.timestamp
        ).order_by(MoodLog.timestamp.asc()).limit(2).all()
        
        if len(recent_moods) > 0:
            avg_intensity = sum(m.intensity for m in recent_moods) / len(recent_moods)
            
            # Simple R logic: High intensity drop is positive reward for stressed states
            if "stressed" in p.state or "fatigued" in p.state:
                r_implicit = p.intensity_before - avg_intensity
            else:
                # If they were motivated, keeping intensity high is good
                r_implicit = avg_intensity - p.intensity_before
            
            update_q_value(db, user_id, p.state, p.action, r_implicit * 0.7) # 70% weight for implicit
            
            # Hook Meta-Learning tuning
            pred_error = abs(r_implicit)
            adjust_learning_rates(db, user_id, pred_error, nudge_ignored_rate=0.0)
            
            if len(recent_moods) >= 2 or (datetime.utcnow() - p.timestamp).total_seconds() > 3600:
                p.resolved = True
    db.commit()

def process_explicit_feedback(db: Session, user_id: str, state: str, action: str, rating: float):
    # rating 1 for thumb-up, -1 for thumb-down
    r_explicit = rating * 0.5 
    update_q_value(db, user_id, state, action, r_explicit * 0.3) # 30% weight explicit boost
