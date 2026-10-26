from sqlalchemy.orm import Session
from models.personalization import UserPolicy

def evaluate_strategy_shift(db: Session, user_id: str):
    policies = db.query(UserPolicy).filter(UserPolicy.user_id == user_id, UserPolicy.visits >= 3).all()
    
    messages = []
    for p in policies:
        if p.visits > 5 and p.q_score < 0.3:
            emotion = p.state.split('_')[1] if '_' in p.state else 'you'
            messages.append(f"{p.action.replace('_', ' ').capitalize()} is becoming less effective for {emotion}.")
            
    if not messages:
        return "Your strategies are currently stable and effective."
        
    return " | ".join(messages[:2])
