from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from models.post_mortem import PostMortemReport
from models.agent_metrics import AgentMetrics

class PostMortemEngine:
    @staticmethod
    def conduct_post_mortem(
        db: Session,
        user_id: int,
        failed_action: str,
        decision_hash: Optional[str] = None,
        weights_at_decision: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Executes a forensic post-mortem when an intervention fails.
        Identifies agent culpability, attributes failure root cause,
        penalizes responsible agent reliability, and stores corrective adaptations.
        """
        weights = weights_at_decision or {"strategy": 0.35, "prediction": 0.25, "meta": 0.20, "cognition": 0.20}
        failed_lower = failed_action.lower()

        # 1. Attribute primary and secondary culpable agents
        if any(k in failed_lower for k in ["push", "deep_work", "sprint", "execute", "grind"]):
            responsible_agent = "strategy"
            secondary_agent = "prediction"
            root_cause = "Over-aggressive intervention recommended during saturated cognitive state."
            adaptation = "Reduced StrategyAgent dynamic weight in high-strain states; increased PredictionAgent risk sensitivity."
            primary_penalty = 0.12
            secondary_penalty = 0.05
        elif any(k in failed_lower for k in ["isolate", "avoid", "stop", "give_up"]):
            responsible_agent = "cognition"
            secondary_agent = "meta"
            root_cause = "Failure to detect and challenge avoidance rationalization."
            adaptation = "Strengthened CognitionAgent cognitive distortion thresholds; enforced Socratic reality-testing."
            primary_penalty = 0.10
            secondary_penalty = 0.04
        else:
            # Default attribution based on dominant agent at time of decision
            dominant = max(weights, key=weights.get) if weights else "strategy"
            responsible_agent = dominant
            secondary_agent = "prediction" if dominant != "prediction" else "strategy"
            root_cause = f"Intervention '{failed_action}' produced negative cognitive delta despite high consensus."
            adaptation = f"Attenuated dominant influence of {responsible_agent}; boosted exploration decay."
            primary_penalty = 0.08
            secondary_penalty = 0.03

        # 2. Apply reliability metric penalties in DB
        agents_to_penalize = [(responsible_agent, primary_penalty), (secondary_agent, secondary_penalty)]
        for agent_name, penalty in agents_to_penalize:
            metric = db.query(AgentMetrics).filter_by(user_id=str(user_id), agent_id=agent_name).first()
            if metric:
                metric.overrides += 1
                metric.historical_accuracy = max(0.1, round(metric.historical_accuracy - penalty, 3))
                metric.updated_at = datetime.utcnow()

        # 3. Create persistent Post-Mortem Report
        report = PostMortemReport(
            user_id=user_id,
            decision_hash=decision_hash,
            failed_action=failed_action,
            responsible_agent=responsible_agent,
            root_cause=root_cause,
            penalty_applied=primary_penalty,
            corrective_adaptation=adaptation,
            created_at=datetime.utcnow()
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        return {
            "report_id": report.id,
            "failed_action": failed_action,
            "responsible_agent": responsible_agent,
            "secondary_agent": secondary_agent,
            "root_cause": root_cause,
            "penalty_applied": primary_penalty,
            "corrective_adaptation": adaptation,
            "created_at": report.created_at.isoformat()
        }
