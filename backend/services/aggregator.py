from services.calibration_service import CalibrationService

def aggregate(user_id: str, agent_outputs):
    state = agent_outputs.get("state", {})
    pred = agent_outputs.get("prediction", {"output": {}, "confidence": 0.0})
    strat = agent_outputs.get("strategy", {"output": "", "confidence": 0.0})
    meta = agent_outputs.get("meta", {"output": {}, "confidence": 0.0})
    cog = agent_outputs.get("cognition", {"output": [], "confidence": 0.0})

    # 3. Agent Reliability Scoring via Dynamic Calibration (Phase 10.1)
    pred_cal = CalibrationService.get_calibrated_weight(user_id, "prediction", pred.get("confidence", 0.0))
    strat_cal = CalibrationService.get_calibrated_weight(user_id, "strategy", strat.get("confidence", 0.0))
    meta_cal = CalibrationService.get_calibrated_weight(user_id, "meta", meta.get("confidence", 0.0))
    cog_cal = CalibrationService.get_calibrated_weight(user_id, "cognition", cog.get("confidence", 0.0))
    
    weights = {
        "prediction": pred_cal["dynamic_weight"],
        "strategy": strat_cal["dynamic_weight"],
        "meta": meta_cal["dynamic_weight"],
        "cognition": cog_cal["dynamic_weight"],
    }
    
    trust_tiers = {
        "prediction": pred_cal["trust_tier"],
        "strategy": strat_cal["trust_tier"],
        "meta": meta_cal["trust_tier"],
        "cognition": cog_cal["trust_tier"]
    }
    
    reasoning_traces = {
        "prediction": pred_cal["reasoning"],
        "strategy": strat_cal["reasoning"],
        "meta": meta_cal["reasoning"],
        "cognition": cog_cal["reasoning"]
    }
    
    effective_accuracies = {
        "prediction": pred_cal["effective_accuracy"],
        "strategy": strat_cal["effective_accuracy"],
        "meta": meta_cal["effective_accuracy"],
        "cognition": cog_cal["effective_accuracy"]
    }

    # Conflict Resolution & Severity
    conflicts = []
    conflict_severity = "Low"
    if pred and isinstance(pred.get("output"), dict):
        if "risk" in pred["output"] and "High" in pred.get("output").get("risk", ""):
            conflict_severity = "Critical"
            if strat and strat.get("output", "") == "push_through":
                strat["output"] = "take_break"
                strat["adjusted"] = True
                strat["conflict_reason"] = "Overridden by PredictionAgent High Risk Alert"
                conflicts.append(strat["conflict_reason"])

    # Cross-Agent Consistency Check (Meta)
    if meta and isinstance(meta.get("output"), dict) and strat:
        dissonance_data = meta["output"].get("dissonance", {})
        if dissonance_data.get("dissonance", 0) > 0.7:
            if conflict_severity != "Critical":
                conflict_severity = "Moderate"
            if strat.get("output", "") == "push_through":
                strat["output"] = "reflect_and_realign"
                strat["adjusted"] = True
                strat["conflict_reason"] = "Overridden by MetaAgent Dissonance Gap"
                conflicts.append(strat["conflict_reason"])

    total = sum(weights.values()) or 1.0
    weights = {k: round(v/total, 3) for k,v in weights.items()}

    # Dominant Agent Calculation
    dominant_agent = max(weights, key=weights.get)

    final_conf = (pred.get("confidence", 0) + strat.get("confidence", 0) + meta.get("confidence", 0) + cog.get("confidence", 0)) / 4.0

    # Aggregator Stability Floor
    mode = "normal"
    if final_conf < 0.25:
        mode = "safe"
    elif final_conf < 0.4:
        mode = "conservative"

    return {
        "state": state,
        "prediction": pred,
        "strategy": strat,
        "meta": meta,
        "cognition": cog,
        "weights": weights,
        "trust_tiers": trust_tiers,
        "reasoning_traces": reasoning_traces,
        "effective_accuracies": effective_accuracies,
        "confidence": final_conf,
        "mode": mode,
        "conflicts": conflicts,
        "conflict_severity": conflict_severity,
        "dominant_agent": dominant_agent
    }
