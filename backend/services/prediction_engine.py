def predict_next_mood(moods):
    if len(moods) < 5:
        return {"predicted_state": "insufficient_data", "predicted_intensity": 0.0, "trend": "stable", "confidence": 0.0}
    
    alpha = 0.6
    ema = moods[0].intensity
    for mood in moods[1:]:
        ema = alpha * mood.intensity + (1 - alpha) * ema

    if ema > 0.7:
        state = "stressed"
    elif ema < 0.3:
        state = "calm"
    else:
        state = "neutral"

    basis_log = []
    trend = "stable"
    if len(moods) >= 2:
        diff = moods[-1].intensity - moods[0].intensity
        if diff > 0.1:
            trend = "increasing"
            basis_log.append("ema_trend:increasing")
        elif diff < -0.1:
            trend = "decreasing"
            basis_log.append("ema_trend:decreasing")
            
    confidence = min(1.0, len(moods) / 10.0)
    
    tone_modifier = ""
    if confidence < 0.6:
        tone_modifier = " (Suggestive trend)"

    return {
        "insight": f"Predicted State: {state.capitalize()}{tone_modifier}",
        "raw_intensity": round(ema, 2),
        "predicted_state": state,
        "trend": trend,
        "confidence": round(confidence, 2),
        "basis": basis_log,
        "system_version": {"core": "v1.0", "rl": "v1.2", "meta": "v1.1"}
    }

def detect_early_warnings(moods, triggers):
    if not moods: return None
    recent = moods[-5:]
    stress_count = sum(1 for m in recent if m.mood_type in ["stressed", "fatigued"])

    if stress_count >= 3:
        return {
            "type": "burnout_risk",
            "message": "You’ve been in high-stress states repeatedly. Consider slowing down.",
            "severity": "high",
            "confidence": stress_count / len(recent)
        }

    if len(recent) > 0 and recent[-1].mood_type == "stressed":
        for t in triggers:
            if t.emotion == "stressed" and getattr(t, "confidence", 0) > 0.5:
                # Assuming triggers is a list of Trigger DB objects
                return {
                    "type": "trigger_loop",
                    "message": f"You're entering a stress loop linked to '{t.event}' tasks.",
                    "severity": "medium",
                    "confidence": getattr(t, "confidence", 0.5)
                }

    return None

def project_long_term_risk(moods, triggers, policies):
    if len(moods) < 5: 
        return {
           "risk": "Not enough data for reliable insight", 
           "confidence": 0.0, 
           "reason": "Minimum 5 logs required.",
           "basis": [],
           "system_version": {"core": "v1.0", "rl": "v1.2", "meta": "v1.1"}
        }

    recent = moods[-7:]
    stress_ratio = sum(1 for m in recent if m.mood_type in ["stressed", "fatigued"]) / max(len(recent), 1)
    
    basis_log = []
    
    trigger_risk = 0.0
    for t in triggers:
        if t.emotion in ["stressed", "fatigued"] and getattr(t, "confidence", 0) > 0.5:
            trigger_risk += 0.2
            basis_log.append(f"trigger:{t.event}→{t.emotion}")
            
    rl_failures = 0.0
    for p in policies:
        if p.visits > 3 and p.q_score < 0.2:
            rl_failures += 0.15
            basis_log.append(f"rl_fail:{p.action}")
            
    total_risk = stress_ratio * 0.5 + trigger_risk + rl_failures
    
    base_conf = min(total_risk, 0.95)
    
    # Meta Confidence formula
    data_density = min(1.0, len(moods) / 10.0)
    pattern_stability = 0.8 if len(basis_log) > 0 else 0.4
    rl_conf = min(1.0, len(policies) / 5.0)
    meta_conf = (data_density * 0.4 + pattern_stability * 0.3 + rl_conf * 0.3)
    
    final_conf = min(base_conf, meta_conf)
    
    tone_modifier = ""
    if final_conf < 0.6:
        tone_modifier = " (Suggestive trend, pending more data)"
    
    if total_risk > 0.6:
        return {
            "risk": f"High Burnout Vulnerability{tone_modifier}",
            "confidence": round(final_conf, 2),
            "reason": "Repeated stress loops compounded with low RL intervention success.",
            "basis": basis_log,
            "system_version": {"core": "v1.0", "rl": "v1.2", "meta": "v1.1"}
        }
    elif total_risk > 0.35:
         return {
            "risk": f"Moderate Burnout Drift{tone_modifier}",
            "confidence": round(final_conf, 2),
            "reason": "Stress baseline climbing alongside active contextual triggers.",
            "basis": basis_log,
            "system_version": {"core": "v1.0", "rl": "v1.2", "meta": "v1.1"}
        }
    return None
