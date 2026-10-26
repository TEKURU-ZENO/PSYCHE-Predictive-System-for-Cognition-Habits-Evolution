import json
from models.event import EventLog
from db.postgres import get_new_session
import statistics

def get_system_effectiveness(user_id: str):
    """
    Scans the DECISION_MEMORY EventLogs to calculate System Effectiveness %.
    """
    db = get_new_session()
    try:
        logs = db.query(EventLog).filter(
            EventLog.user_id == user_id, 
            EventLog.type == "DECISION_MEMORY"
        ).order_by(EventLog.id.desc()).limit(15).all()
        
        if not logs:
            return {"success_rate": 0.50, "status": "Learning", "trend": "→", "anomaly": False, "variance": 0.0}
            
        successes = 0
        total = 0
        score_history = []
        
        for log in logs:
            meta = json.loads(log.metadata_col)
            outcome = meta.get("outcome")
            if outcome and isinstance(outcome, dict):
                total += 1
                val = 1.0 if outcome.get("success") == True else 0.0
                score_history.append(val)
                if val == 1.0:
                    successes += 1
                    
        rate = (successes / total) if total > 0 else 0.50
        
        # 1. Variance tracking & Anomaly detection
        variance = 0.0
        anomaly_detected = False
        if len(score_history) >= 3:
            variance = statistics.variance(score_history) if len(score_history) > 1 else 0.0
            # If the last 3 outcomes completely contradict the running average
            recent_rate = sum(score_history[:3]) / 3
            if abs(recent_rate - rate) > 0.5:
                anomaly_detected = True
        
        status = "Plateau"
        if rate >= 0.65:
            status = "Improving"
        elif rate < 0.40:
            status = "Declining"
            
        # 4. System Bias Correction
        increase_exploration = False
        if rate > 0.80 and total >= 5:
            increase_exploration = True
            
        # 5. Learning Health Metric
        learning_health = "stable"
        if rate > 0.60 and variance < 0.25:
            learning_health = "improving"
        elif rate < 0.35 or variance > 0.25:
            learning_health = "unstable"
            
        return {
            "success_rate": round(rate, 2),
            "status": status,
            "trend": "↑" if status == "Improving" else ("↓" if status == "Declining" else "→"),
            "total_evals": total,
            "increase_exploration": increase_exploration,
            "learning_health": learning_health,
            "variance": round(variance, 3),
            "anomaly_detected": anomaly_detected
        }
    finally:
        db.close()

def get_agent_reliability_scores():
    # In full prod, this sweeps Agent Timeout and Effectiveness ratios per agent from logs.
    # We map deterministic bounds for MVP weighting
    return {
        "prediction": {"reliability_factor": 0.95, "timeout_rate": 0.01},
        "strategy": {"reliability_factor": 0.85, "timeout_rate": 0.02},
        "meta": {"reliability_factor": 0.88, "timeout_rate": 0.01},
        "cognition": {"reliability_factor": 0.90, "timeout_rate": 0.03}
    }
