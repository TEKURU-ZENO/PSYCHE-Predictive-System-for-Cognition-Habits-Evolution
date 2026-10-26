from sqlalchemy.orm import Session
from models.system_state import SystemState

def adjust_learning_rates(db: Session, user_id: str, prediction_error: float, nudge_ignored_rate: float):
    state = db.query(SystemState).filter_by(user_id=user_id).first()
    if not state:
        state = SystemState(user_id=user_id)
        db.add(state)
        
    old_alpha = state.alpha
    old_epsilon = state.epsilon
    
    if prediction_error > 0.4:
        state.alpha += 0.1
        
    if nudge_ignored_rate > 0.5:
        state.epsilon += 0.1
        
    state.alpha = min(0.6, max(0.2, state.alpha))
    state.epsilon = min(0.4, max(0.1, state.epsilon))
    
    if abs(state.alpha - old_alpha) < 0.05:
        state.alpha = old_alpha 
        
    db.commit()
    return state
