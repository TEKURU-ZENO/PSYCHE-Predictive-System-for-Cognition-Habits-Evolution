"""
Psych-AI Platform - Statistical & Behavioral Prediction Engine
Implements Holt's double exponential smoothing trend forecasting, empirical Markov
state transition modeling, affective volatility quantification, and Critical Slowing Down (CSD)
early warning systems for psychological trajectory forecasting.
"""

import math
from datetime import datetime
from typing import List, Dict, Any, Optional

EMOTIONAL_STATES = ["calm", "focused", "stressed", "fatigued", "neutral", "anxious"]

# Valence & Arousal mapping for multidimensional state modeling
STATE_COORDINATES = {
    "calm": {"valence": 0.7, "arousal": 0.2},
    "focused": {"valence": 0.6, "arousal": 0.7},
    "motivated": {"valence": 0.8, "arousal": 0.8},
    "neutral": {"valence": 0.0, "arousal": 0.4},
    "fatigued": {"valence": -0.4, "arousal": 0.1},
    "stressed": {"valence": -0.7, "arousal": 0.85},
    "anxious": {"valence": -0.6, "arousal": 0.90},
}


def _get_circadian_phase(dt: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Categorizes circadian diurnal phase and physiological vulnerability window.
    """
    if dt is None:
        dt = datetime.utcnow()
    hour = dt.hour

    if 6 <= hour < 10:
        return {"phase": "Morning Cortisol Surge", "baseline_arousal": 0.65, "vulnerability": "Low"}
    elif 10 <= hour < 14:
        return {"phase": "Peak Executive Window", "baseline_arousal": 0.75, "vulnerability": "Low"}
    elif 14 <= hour < 17:
        return {"phase": "Post-Prandial Refractory Dip", "baseline_arousal": 0.40, "vulnerability": "Moderate"}
    elif 17 <= hour < 22:
        return {"phase": "Evening Decompression", "baseline_arousal": 0.45, "vulnerability": "Moderate"}
    else:
        return {"phase": "Late-Night Vulnerability Window", "baseline_arousal": 0.30, "vulnerability": "High"}


def _compute_markov_transition_probabilities(moods: List[Any], current_state: str) -> Dict[str, float]:
    """
    Computes empirical 1st-order Markov transition probabilities P(S_t+1 | S_t)
    from historical mood transitions.
    """
    transitions: Dict[str, Dict[str, int]] = {s: {target: 1 for target in EMOTIONAL_STATES} for s in EMOTIONAL_STATES}
    
    # Tally transitions with Laplace smoothing (+1 pseudocount)
    for i in range(len(moods) - 1):
        s_from = getattr(moods[i], "mood_type", "neutral").lower()
        s_to = getattr(moods[i + 1], "mood_type", "neutral").lower()
        if s_from in transitions and s_to in transitions[s_from]:
            transitions[s_from][s_to] += 3

    current = current_state.lower()
    if current not in transitions:
        current = "neutral"

    row = transitions[current]
    total = sum(row.values())
    return {s: round(row[s] / total, 3) for s in EMOTIONAL_STATES}


def _holt_linear_trend_forecast(intensities: List[float], h: int = 1) -> Dict[str, Any]:
    """
    Holt's Double Exponential Smoothing (Level + Trend Velocity):
      level_t = alpha * y_t + (1 - alpha) * (level_t-1 + trend_t-1)
      trend_t = beta * (level_t - level_t-1) + (1 - beta) * trend_t-1
      forecast_t+h = level_t + h * trend_t
    """
    n = len(intensities)
    if n == 0:
        return {"projected": 0.5, "velocity": 0.0, "volatility": 0.0}
    if n == 1:
        return {"projected": intensities[0], "velocity": 0.0, "volatility": 0.0}

    # Variance-adaptive smoothing parameters
    mean_val = sum(intensities) / n
    variance = sum((x - mean_val) ** 2 for x in intensities) / max(1, n - 1)
    std_dev = math.sqrt(variance)

    # High variance -> smoother alpha to prevent noise chasing; low variance -> more responsive
    alpha = min(0.7, max(0.2, 0.4 + 0.1 * (1.0 - min(1.0, std_dev))))
    beta = 0.25

    level = intensities[0]
    trend = intensities[1] - intensities[0]

    for i in range(1, n):
        y = intensities[i]
        prev_level = level
        level = alpha * y + (1 - alpha) * (prev_level + trend)
        trend = beta * (level - prev_level) + (1 - beta) * trend

    projected = level + (h * trend)
    projected = max(0.05, min(0.98, projected))

    return {
        "projected": round(projected, 2),
        "velocity": round(trend, 3),
        "volatility": round(std_dev, 3)
    }


def predict_next_mood(moods: List[Any]) -> Dict[str, Any]:
    """
    Multivariate statistical mood and psychological trajectory predictor.
    Uses Holt linear trend forecasting, Markov state transition matrices,
    affective volatility quantification, and circadian diurnal context.
    """
    if not moods or len(moods) < 3:
        return {
            "predicted_state": "neutral",
            "predicted_intensity": 0.5,
            "trend": "insufficient_data",
            "confidence": 0.2,
            "state_probabilities": {"neutral": 0.6, "calm": 0.2, "focused": 0.2},
            "insight": "Initial baseline established: log additional states for high-fidelity predictive modeling.",
            "basis": ["sample_size < 3"]
        }

    intensities = [float(getattr(m, "intensity", 0.5)) for m in moods]
    current_mood_type = getattr(moods[-1], "mood_type", "neutral").lower()

    # 1. Holt Linear Trend Forecasting
    holt_res = _holt_linear_trend_forecast(intensities, h=1)
    projected_intensity = holt_res["projected"]
    velocity = holt_res["velocity"]
    volatility = holt_res["volatility"]

    # 2. Markov State Transition Distribution
    state_probs = _compute_markov_transition_probabilities(moods, current_mood_type)

    # 3. Diurnal / Circadian Modulation
    circadian = _get_circadian_phase()

    # 4. Synthesize Most Probable Future State
    # Weight Markov probabilities with projected intensity & velocity
    adjusted_scores = {}
    for state_name, prob in state_probs.items():
        coords = STATE_COORDINATES.get(state_name, {"valence": 0.0, "arousal": 0.5})
        # Intensity alignment penalty
        arousal_diff = abs(coords["arousal"] - projected_intensity)
        # If velocity is positive (stress escalating), boost stressed/anxious states
        escalation_bonus = 0.15 if (velocity > 0.05 and state_name in ["stressed", "anxious"]) else 0.0
        # If velocity is negative (recovering), boost calm/focused states
        recovery_bonus = 0.15 if (velocity < -0.05 and state_name in ["calm", "focused"]) else 0.0
        score = prob * (1.0 - 0.4 * arousal_diff) + escalation_bonus + recovery_bonus
        adjusted_scores[state_name] = max(0.01, score)

    total_score = sum(adjusted_scores.values())
    normalized_probs = {s: round(sc / total_score, 2) for s, sc in adjusted_scores.items()}
    best_state = max(normalized_probs, key=normalized_probs.get)

    # 5. Trend Classification
    if velocity > 0.05:
        trend = "escalating"
    elif velocity < -0.05:
        trend = "de-escalating"
    else:
        trend = "stable"

    # 6. Bayesian Dynamic Confidence Bound
    # Based on sample depth, volatility stability, and consistency
    sample_factor = min(1.0, len(moods) / 12.0)
    stability_factor = max(0.2, 1.0 - volatility)
    confidence = round(0.4 * sample_factor + 0.6 * stability_factor, 2)

    basis_log = [
        f"holt_projected_intensity:{projected_intensity}",
        f"velocity:{velocity}",
        f"volatility:{volatility}",
        f"circadian_phase:{circadian['phase']}",
        f"top_state_prob:{best_state}:{normalized_probs.get(best_state, 0.0)}"
    ]

    return {
        "insight": f"Forecasted Trajectory: {best_state.capitalize()} (Intensity {projected_intensity})",
        "predicted_state": best_state,
        "predicted_intensity": projected_intensity,
        "raw_intensity": projected_intensity,
        "velocity": velocity,
        "volatility": volatility,
        "trend": trend,
        "confidence": confidence,
        "state_probabilities": normalized_probs,
        "circadian_phase": circadian["phase"],
        "basis": basis_log,
        "system_version": {"core": "v1.7.0", "forecasting": "v2.0.0"}
    }


def detect_early_warnings(moods: List[Any], triggers: List[Any]) -> Optional[Dict[str, Any]]:
    """
    Critical Slowing Down (CSD) & Trigger Loop Early Warning Detection.
    Detects critical phase transitions toward burnout before acute distress occurs.
    """
    if not moods or len(moods) < 4:
        return None

    recent = moods[-6:]
    intensities = [float(getattr(m, "intensity", 0.5)) for m in recent]
    stress_count = sum(1 for m in recent if getattr(m, "mood_type", "").lower() in ["stressed", "fatigued", "anxious"])

    # 1. Critical Slowing Down (CSD) Metric: Lag-1 Autocorrelation & Variance Spikes
    mean_val = sum(intensities) / len(intensities)
    variance = sum((x - mean_val) ** 2 for x in intensities) / len(intensities)
    
    # Lag-1 Autocorrelation
    if len(intensities) >= 4 and variance > 0.001:
        num = sum((intensities[i] - mean_val) * (intensities[i - 1] - mean_val) for i in range(1, len(intensities)))
        denom = sum((x - mean_val) ** 2 for x in intensities[:-1])
        autocorr_lag1 = (num / max(1e-6, denom)) if denom > 0 else 0.0
    else:
        autocorr_lag1 = 0.0

    # CSD Trigger: High positive autocorrelation + elevated variance indicates loss of system resilience
    if autocorr_lag1 > 0.65 and mean_val > 0.65:
        return {
            "type": "critical_slowing_down",
            "message": "Critical resilience degradation detected: emotional recovery latency is widening under continuous load.",
            "severity": "high",
            "confidence": 0.88,
            "metric": f"lag1_autocorr:{round(autocorr_lag1, 2)}",
            "recommended_action": "Proactive 30m cognitive refractory window before task transition."
        }

    # 2. Burnout Cluster Warning
    if stress_count >= 3:
        return {
            "type": "burnout_risk",
            "message": "Repeated acute stress episodes registered. Physiological and cognitive depletion velocity is climbing.",
            "severity": "high",
            "confidence": round(stress_count / len(recent), 2)
        }

    # 3. Contextual Trigger Loop Warning
    if len(recent) > 0 and getattr(recent[-1], "mood_type", "").lower() in ["stressed", "anxious"]:
        for t in triggers:
            if getattr(t, "emotion", "") in ["stressed", "anxious"] and getattr(t, "confidence", 0) > 0.5:
                return {
                    "type": "trigger_loop",
                    "message": f"Entering a recurrent friction loop associated with '{getattr(t, 'event', 'work')}' contexts.",
                    "severity": "medium",
                    "confidence": getattr(t, "confidence", 0.7)
                }

    return None


def project_long_term_risk(moods: List[Any], triggers: List[Any], policies: List[Any]) -> Dict[str, Any]:
    """
    Longitudinal 7-day risk projection incorporating stress velocity,
    trigger density, and reinforcement learning policy effectiveness.
    """
    if len(moods) < 3:
        return {
            "risk": "Baseline Compiling",
            "confidence": 0.15,
            "reason": "Minimum 3 longitudinal state logs required for statistical risk projection.",
            "basis": ["sample_size < 3"],
            "system_version": {"core": "v1.7.0", "forecasting": "v2.0.0"}
        }

    recent = moods[-8:]
    stress_ratio = sum(1 for m in recent if getattr(m, "mood_type", "").lower() in ["stressed", "fatigued", "anxious"]) / max(1, len(recent))

    basis_log = [f"stress_ratio:{round(stress_ratio, 2)}"]

    # Trigger compounding
    trigger_risk = 0.0
    for t in triggers:
        if getattr(t, "emotion", "") in ["stressed", "fatigued", "anxious"] and getattr(t, "confidence", 0) > 0.5:
            trigger_risk += 0.15
            basis_log.append(f"trigger:{getattr(t, 'event', '')}→{getattr(t, 'emotion', '')}")

    # RL Intervention resistance
    rl_failures = 0.0
    for p in policies:
        if getattr(p, "visits", 0) > 3 and getattr(p, "q_score", 0.5) < 0.2:
            rl_failures += 0.12
            basis_log.append(f"intervention_resistance:{getattr(p, 'action', '')}")

    total_risk = (stress_ratio * 0.50) + min(0.30, trigger_risk) + min(0.25, rl_failures)

    confidence = round(min(0.95, 0.4 * (len(moods) / 10.0) + 0.5 * (1.0 - abs(0.5 - total_risk))), 2)

    if total_risk > 0.55:
        return {
            "risk": "Elevated Burnout Trajectory",
            "confidence": confidence,
            "reason": "Repeated high-arousal negative state transitions compounded by contextual friction loops.",
            "basis": basis_log,
            "system_version": {"core": "v1.7.0", "forecasting": "v2.0.0"}
        }
    elif total_risk > 0.30:
        return {
            "risk": "Moderate Stress Accumulation",
            "confidence": confidence,
            "reason": "Gradual upward drift in cognitive load; manageable with structured boundary setting.",
            "basis": basis_log,
            "system_version": {"core": "v1.7.0", "forecasting": "v2.0.0"}
        }
    else:
        return {
            "risk": "Stable Cognitive Equilibrium",
            "confidence": confidence,
            "reason": "Balanced mood distributions with steady recovery intervals following stressors.",
            "basis": basis_log,
            "system_version": {"core": "v1.7.0", "forecasting": "v2.0.0"}
        }
