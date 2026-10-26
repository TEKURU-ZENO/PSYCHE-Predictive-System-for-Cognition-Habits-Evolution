from services.reliability_service import ReliabilityService

class CalibrationService:
    @staticmethod
    def get_calibrated_weight(user_id: str, agent_id: str, raw_confidence: float) -> dict:
        metrics = ReliabilityService.get_agent_metrics(user_id, agent_id)
        
        effective_accuracy = metrics["effective_accuracy"]
        impact = metrics["contribution_impact_score"]
        
        dynamic_weight = raw_confidence * effective_accuracy * impact
        
        # Explainability for UI ("Why confidence changed")
        reasoning = []
        if effective_accuracy < metrics["historical_accuracy"] * 0.95: # Noticeable decay
            reasoning.append("Confidence decayed due to prolonged inactivity.")
            
        if impact > 1.1:
            reasoning.append("Weight boosted by high historical contribution impact.")
        elif impact < 0.9:
            reasoning.append("Weight penalized due to recent poor impact or overrides.")
            
        trust_tier = metrics["trust_tier"]
        if trust_tier == "Trusted":
            reasoning.append("Trusted agent bonus applied.")
            dynamic_weight *= 1.1
        elif trust_tier == "Degraded":
            reasoning.append("Degraded agent penalty applied.")
            dynamic_weight *= 0.5
            
        # Floor and ceiling
        dynamic_weight = max(0.01, min(2.0, dynamic_weight))
            
        return {
            "dynamic_weight": dynamic_weight,
            "trust_tier": trust_tier,
            "reasoning": reasoning,
            "effective_accuracy": effective_accuracy
        }
