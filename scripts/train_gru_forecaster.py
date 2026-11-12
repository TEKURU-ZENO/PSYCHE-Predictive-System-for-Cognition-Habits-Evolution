#!/usr/bin/env python3
"""
Psych-AI: Train & Benchmark the Pure-Python GRU Forecaster via Exact BPTT + Adam
Uses aligned real Ecological Momentary Assessment (EMA) trajectories in
`backend/data/ema_mood_sequences.json` (27 participants, 5,465 time-ordered check-ins)
and evaluates strictly out-of-sample against the Holt + Markov baseline.
"""

import json
import math
import os
import sys
from datetime import datetime
from types import SimpleNamespace
from typing import Any, Dict, List, Tuple

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from services.deep_forecasting_engine import (
    DEFAULT_WEIGHTS_PATH,
    EMOTIONS,
    EMOTION_TO_IDX,
    DeepForecastingEngine,
)
from services.prediction_engine import predict_next_mood

DATA_PATH = os.path.join(BACKEND_DIR, "data", "ema_mood_sequences.json")


def map_ema_to_state(mood: float, valence: float, arousal: float) -> Tuple[str, float, float]:
    """
    Maps real EMA self-reports (mood 1..10, valence -2..+2, arousal -2..+2)
    into Psych-AI's Russell Circumplex affective classes, normalized distress
    intensity [0.05, 0.98], and binary high-strain target {0.0, 1.0}.
    """
    # Normalized strain intensity: mood=10 -> 0.05, mood=1 -> 0.98
    intensity = round(max(0.05, min(0.98, 0.05 + 0.93 * (10.0 - mood) / 9.0)), 3)
    is_strain = 1.0 if (mood <= 5.5 or valence < 0.0) else 0.0

    if valence < 0.0 or mood <= 5.5:
        if arousal < 0.0:
            state = "fatigued"
        elif arousal >= 1.0 or mood <= 4.5:
            state = "stressed"
        else:
            state = "anxious"
    elif valence == 0.0:
        state = "neutral"
    else:
        if arousal <= 0.0:
            state = "calm"
        elif mood >= 7.5 or arousal >= 1.0:
            state = "motivated"
        else:
            state = "focused"

    return state, intensity, is_strain


def build_participant_windows(
    raw_data: Dict[str, Any], window_len: int = 8
) -> Tuple[List[Tuple[List[Any], int, float, float]], List[Tuple[List[Any], int, float, float]]]:
    """
    Builds participant-disjoint train (first 19 participants) and held-out test
    (last 8 participants) sliding windows `(history_window -> next_state, next_intensity, next_strain)`.
    """
    sequences = raw_data["sequences"]
    participant_ids = sorted(sequences.keys())
    split_idx = int(len(participant_ids) * 0.7)  # 19 train users, 8 strictly unseen test users
    train_ids = set(participant_ids[:split_idx])

    train_windows = []
    test_windows = []

    for pid in participant_ids:
        items = []
        targets = []
        for entry in sequences[pid]:
            state, intensity, is_strain = map_ema_to_state(
                entry["mood"], entry["valence"], entry["arousal"]
            )
            ts = datetime.fromisoformat(entry["time"])
            items.append(SimpleNamespace(mood_type=state, intensity=intensity, timestamp=ts))
            targets.append((EMOTION_TO_IDX[state], intensity, is_strain))

        bucket = train_windows if pid in train_ids else test_windows
        for i in range(window_len, len(items)):
            hist = items[i - window_len : i]
            y_cls, y_int, y_haz = targets[i]
            bucket.append((hist, y_cls, y_int, y_haz))

    return train_windows, test_windows


def run_gradient_check(sample: Tuple[List[Any], int, float, float]) -> float:
    """
    Verifies exact BPTT analytic gradients against central finite differences
    across representative recurrent and head weights.
    """
    engine = DeepForecastingEngine(auto_load_trained=False)
    window, y_cls, y_int, y_haz = sample
    _, grads = engine.compute_sample_loss_and_grads(window, y_cls, y_int, y_haz)

    eps = 1e-5
    max_abs_err = 0.0
    probes = [
        ("gru.W_z[0][0]", engine.gru.W_z, 0, 0, grads["gru"]["W_z"][0][0]),
        ("gru.U_z[2][3]", engine.gru.U_z, 2, 3, grads["gru"]["U_z"][2][3]),
        ("gru.W_r[1][2]", engine.gru.W_r, 1, 2, grads["gru"]["W_r"][1][2]),
        ("gru.U_r[3][1]", engine.gru.U_r, 3, 1, grads["gru"]["U_r"][3][1]),
        ("gru.W_n[2][4]", engine.gru.W_n, 2, 4, grads["gru"]["W_n"][2][4]),
        ("gru.U_n[4][2]", engine.gru.U_n, 4, 2, grads["gru"]["U_n"][4][2]),
        ("W_out[1][3]", engine.W_out, 1, 3, grads["W_out"][1][3]),
    ]
    for name, mat, r, c, analytic in probes:
        orig = mat[r][c]
        mat[r][c] = orig + eps
        loss_plus, _ = engine.compute_sample_loss_and_grads(window, y_cls, y_int, y_haz)
        mat[r][c] = orig - eps
        loss_minus, _ = engine.compute_sample_loss_and_grads(window, y_cls, y_int, y_haz)
        mat[r][c] = orig
        num = (loss_plus - loss_minus) / (2.0 * eps)
        err = abs(num - analytic)
        max_abs_err = max(max_abs_err, err)
        if err > 1e-5:
            raise AssertionError(f"Gradient check failed for {name}: num={num}, analytic={analytic}, err={err}")
    return max_abs_err


def evaluate_models(
    test_windows: List[Tuple[List[Any], int, float, float]],
    trained_engine: DeepForecastingEngine,
    untrained_engine: DeepForecastingEngine,
) -> Dict[str, Dict[str, float]]:
    n = len(test_windows)
    stats = {
        "holt_markov": {"cls_correct": 0, "nll": 0.0, "mae": 0.0, "sq_err": 0.0},
        "untrained_gru": {"cls_correct": 0, "nll": 0.0, "mae": 0.0, "sq_err": 0.0, "haz_brier": 0.0},
        "trained_gru": {"cls_correct": 0, "nll": 0.0, "mae": 0.0, "sq_err": 0.0, "haz_brier": 0.0},
    }

    for hist, y_cls, y_int, y_haz in test_windows:
        true_state = EMOTIONS[y_cls]

        # 1. Holt + Markov baseline
        hm = predict_next_mood(hist)
        hm_probs = hm.get("state_probabilities", {})
        hm_pred_state = hm.get("predicted_state", "neutral")
        if hm_pred_state == true_state:
            stats["holt_markov"]["cls_correct"] += 1
        p_true_hm = max(1e-6, float(hm_probs.get(true_state, 0.01)))
        stats["holt_markov"]["nll"] += -math.log(p_true_hm)
        hm_int = float(hm.get("predicted_intensity", 0.5))
        stats["holt_markov"]["mae"] += abs(hm_int - y_int)
        stats["holt_markov"]["sq_err"] += (hm_int - y_int) ** 2

        # 2. Untrained GRU Prior & 3. Trained GRU
        for key, eng in (("untrained_gru", untrained_engine), ("trained_gru", trained_engine)):
            res = eng.forecast_trajectory(hist, horizon_steps=1)
            if res["dominant_forecast"] == true_state:
                stats[key]["cls_correct"] += 1
            p_true = max(1e-6, float(res["state_distribution"].get(true_state, 0.001)))
            stats[key]["nll"] += -math.log(p_true)
            pred_int = float(res["predicted_intensity"])
            stats[key]["mae"] += abs(pred_int - y_int)
            stats[key]["sq_err"] += (pred_int - y_int) ** 2
            stats[key]["haz_brier"] += (float(res["burnout_hazard_rate"]) - y_haz) ** 2

    results: Dict[str, Dict[str, float]] = {}
    for model_name, s in stats.items():
        results[model_name] = {
            "state_accuracy": round(s["cls_correct"] / n, 4),
            "cross_entropy_nll": round(s["nll"] / n, 4),
            "intensity_mae": round(s["mae"] / n, 4),
            "intensity_rmse": round(math.sqrt(s["sq_err"] / n), 4),
        }
        if "haz_brier" in s:
            results[model_name]["hazard_brier"] = round(s["haz_brier"] / n, 4)
    return results


def main() -> None:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    train_windows, test_windows = build_participant_windows(raw_data, window_len=8)
    print(f"Loaded {raw_data['total_points']} EMA points across {raw_data['participants']} participants")
    print(f"Participant-disjoint split -> Train windows: {len(train_windows)} | Held-out test windows: {len(test_windows)}")

    grad_err = run_gradient_check(train_windows[0])
    print(f"BPTT Finite-Difference Gradient Check PASSED (max abs error = {grad_err:.2e})")

    untrained = DeepForecastingEngine(auto_load_trained=False)
    trained = DeepForecastingEngine(auto_load_trained=False)

    losses = trained.train_on_windows(
        train_windows,
        epochs=18,
        batch_size=32,
        lr=0.012,
        weight_decay=1e-4,
        seed=42,
        weight_source="bptt_ema_smartphone_v1",
    )
    print(f"Training losses (epoch 1 -> {len(losses)}): {losses[0]:.4f} -> {losses[-1]:.4f}")

    metrics = evaluate_models(test_windows, trained, untrained)
    print("\nHeld-Out Benchmark (8 Unseen Participants):")
    print(json.dumps(metrics, indent=2))

    trained.benchmark_metrics = {
        "dataset": raw_data["source"],
        "split": "participant_disjoint_19_train_8_test",
        "train_windows": len(train_windows),
        "test_windows": len(test_windows),
        "epochs": len(losses),
        "train_loss_start": losses[0],
        "train_loss_end": losses[-1],
        "held_out_results": metrics,
    }
    trained.save_weights(DEFAULT_WEIGHTS_PATH)
    print(f"\nSaved trained GRU weights to {DEFAULT_WEIGHTS_PATH}")


if __name__ == "__main__":
    main()
