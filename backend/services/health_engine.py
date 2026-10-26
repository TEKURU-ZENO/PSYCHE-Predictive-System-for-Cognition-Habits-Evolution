import math
import json
from typing import List
from models.system_state import SystemState
from models.personalization import UserPolicy
from sqlalchemy.orm import Session

class HealthEngine:
    @staticmethod
    def calculate_entropy(q_values: List[float]) -> float:
        if not q_values:
            return 0.0
            
        max_q = max(q_values)
        exp_q = [math.exp(q - max_q) for q in q_values]
        sum_exp = sum(exp_q)
        probs = [eq / sum_exp for eq in exp_q]
        
        entropy = -sum(p * math.log(p) for p in probs if p > 0)
        return entropy

    @staticmethod
    def track_exploration_drift(epsilon_history: List[float]) -> bool:
        if not epsilon_history or len(epsilon_history) < 5:
            return False
        high_eps_count = sum(1 for e in epsilon_history[-10:] if e > 0.35)
        return high_eps_count >= 3

    @staticmethod
    def check_learning_health(db: Session, user_id: str) -> str:
        state_cfg = db.query(SystemState).filter_by(user_id=user_id).first()
        if not state_cfg:
            return "healthy"
            
        eps_history = json.loads(state_cfg.epsilon_history)
        if HealthEngine.track_exploration_drift(eps_history):
            return "learning_uncertain"
            
        # Entropy check
        if state_cfg.policy_entropy < 0.1:
            return "stagnation"
        elif state_cfg.policy_entropy > 2.0:
            return "unstable"
            
        return "healthy"
        
    @staticmethod
    def execute_recovery_mode(db: Session, user_id: str):
        state_cfg = db.query(SystemState).filter_by(user_id=user_id).first()
        if state_cfg:
            state_cfg.recovery_mode_active = True
            
        # Rollback to last stable policy
        policies = db.query(UserPolicy).filter_by(user_id=user_id).all()
        for p in policies:
            p.q_score = p.stable_q_score
            
        db.commit()
