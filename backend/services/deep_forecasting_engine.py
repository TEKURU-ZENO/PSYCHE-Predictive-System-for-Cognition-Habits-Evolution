"""
Psych-AI Platform - Gated Recurrent Unit (GRU) Sequence Forecasting Engine
Implements Gated Recurrent Unit (GRU) state-space transitions, scaled dot-product
temporal self-attention, and non-linear multi-head forecasting (emotion distribution,
next-step intensity, and burnout hazard) in pure Python stdlib (`math`).

Supports both:
- Trained mode (`weights_trained=True`): loads or fits parameters via exact
  Backpropagation Through Time (BPTT) + Adam optimization on longitudinal sequences.
- Untrained fallback mode (`weights_trained=False`): uses deterministic analytic priors
  when no trained weights file is present or when explicitly reset.
"""

import json
import math
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

EMOTIONS = ["calm", "focused", "motivated", "neutral", "fatigued", "stressed", "anxious"]
EMOTION_TO_IDX = {name: idx for idx, name in enumerate(EMOTIONS)}
LATENT_DIM = 8
FEATURE_DIM = 6  # [valence, arousal, intensity_velocity, circadian_phase, trigger_density, compliance]

DEFAULT_WEIGHTS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "trained_gru_weights.json",
)


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-max(-15.0, min(15.0, x))))


def _softmax(vec: List[float]) -> List[float]:
    max_v = max(vec) if vec else 0.0
    exps = [math.exp(max(-20.0, v - max_v)) for v in vec]
    s = sum(exps) or 1.0
    return [e / s for e in exps]


def _mat_vec_mul(W: List[List[float]], v: List[float]) -> List[float]:
    return [sum(W[i][j] * v[j] for j in range(len(v))) for i in range(len(W))]


def _mat_t_vec_mul(W: List[List[float]], v: List[float]) -> List[float]:
    cols = len(W[0]) if W else 0
    return [sum(W[i][j] * v[i] for i in range(len(W))) for j in range(cols)]


def _vec_add(a: List[float], b: List[float]) -> List[float]:
    return [x + y for x, y in zip(a, b)]


def _zeros_mat(rows: int, cols: int) -> List[List[float]]:
    return [[0.0] * cols for _ in range(rows)]


def _accum_outer(grad_mat: List[List[float]], dy: List[float], x: List[float]) -> None:
    for i, d in enumerate(dy):
        row = grad_mat[i]
        for j, xv in enumerate(x):
            row[j] += d * xv


def _clip_grad(val: float, limit: float = 5.0) -> float:
    if val > limit:
        return limit
    if val < -limit:
        return -limit
    return val


class DeepGRUCell:
    """
    Pure-Python Gated Recurrent Unit (GRU) Cell for Continuous Latent Transitions:
      r_t = sigmoid(W_r x_t + U_r h_{t-1} + b_r)          (Reset Gate)
      z_t = sigmoid(W_z x_t + U_z h_{t-1} + b_z)          (Update Gate)
      n_t = tanh(W_n x_t + U_n (r_t * h_{t-1}) + b_n)     (Candidate State)
      h_t = (1 - z_t) * n_t + z_t * h_{t-1}               (Hidden State)
    """

    def __init__(self, in_dim: int = FEATURE_DIM, hidden_dim: int = LATENT_DIM):
        self.in_dim = in_dim
        self.hidden_dim = hidden_dim
        self.init_analytic_prior()

    def init_analytic_prior(self) -> None:
        in_d, h_d = self.in_dim, self.hidden_dim
        self.W_z = [[0.15 * math.cos(i * 0.7 + j) for j in range(in_d)] for i in range(h_d)]
        self.U_z = [[0.65 if i == j else 0.05 * math.sin(i - j) for j in range(h_d)] for i in range(h_d)]
        self.b_z = [0.2] * h_d

        self.W_r = [[0.20 * math.sin(i * 0.5 + j) for j in range(in_d)] for i in range(h_d)]
        self.U_r = [[0.50 if i == j else 0.03 * math.cos(i + j) for j in range(h_d)] for i in range(h_d)]
        self.b_r = [0.0] * h_d

        self.W_n = [[0.35 * math.sin(i * 0.3 + j * 0.4) for j in range(in_d)] for i in range(h_d)]
        self.U_n = [[0.45 if i == j else 0.10 * math.sin(i * j) for j in range(h_d)] for i in range(h_d)]
        self.b_n = [0.0] * h_d

    def forward_with_cache(
        self, x: List[float], h_prev: List[float]
    ) -> Tuple[List[float], Dict[str, List[float]]]:
        r_pre = _vec_add(_mat_vec_mul(self.W_r, x), _vec_add(_mat_vec_mul(self.U_r, h_prev), self.b_r))
        r = [_sigmoid(v) for v in r_pre]

        z_pre = _vec_add(_mat_vec_mul(self.W_z, x), _vec_add(_mat_vec_mul(self.U_z, h_prev), self.b_z))
        z = [_sigmoid(v) for v in z_pre]

        g = [r[i] * h_prev[i] for i in range(self.hidden_dim)]
        n_pre = _vec_add(_mat_vec_mul(self.W_n, x), _vec_add(_mat_vec_mul(self.U_n, g), self.b_n))
        n = [math.tanh(v) for v in n_pre]

        h = [(1.0 - z[i]) * n[i] + z[i] * h_prev[i] for i in range(self.hidden_dim)]
        cache = {"x": x, "h_prev": h_prev, "r": r, "z": z, "g": g, "n": n}
        return h, cache

    def forward(self, x: List[float], h_prev: List[float]) -> List[float]:
        h, _ = self.forward_with_cache(x, h_prev)
        return h

    def zero_grads(self) -> Dict[str, Any]:
        in_d, h_d = self.in_dim, self.hidden_dim
        return {
            "W_z": _zeros_mat(h_d, in_d), "U_z": _zeros_mat(h_d, h_d), "b_z": [0.0] * h_d,
            "W_r": _zeros_mat(h_d, in_d), "U_r": _zeros_mat(h_d, h_d), "b_r": [0.0] * h_d,
            "W_n": _zeros_mat(h_d, in_d), "U_n": _zeros_mat(h_d, h_d), "b_n": [0.0] * h_d,
        }

    def backward_step(
        self, dh: List[float], cache: Dict[str, List[float]], grads: Dict[str, Any]
    ) -> List[float]:
        x = cache["x"]
        h_prev = cache["h_prev"]
        r = cache["r"]
        z = cache["z"]
        g = cache["g"]
        n = cache["n"]

        dn = [dh[i] * (1.0 - z[i]) for i in range(self.hidden_dim)]
        dz = [dh[i] * (h_prev[i] - n[i]) for i in range(self.hidden_dim)]
        dh_prev = [dh[i] * z[i] for i in range(self.hidden_dim)]

        da_n = [dn[i] * (1.0 - n[i] * n[i]) for i in range(self.hidden_dim)]
        _accum_outer(grads["W_n"], da_n, x)
        _accum_outer(grads["U_n"], da_n, g)
        for i in range(self.hidden_dim):
            grads["b_n"][i] += da_n[i]

        dg = _mat_t_vec_mul(self.U_n, da_n)
        dr = [dg[i] * h_prev[i] for i in range(self.hidden_dim)]
        for i in range(self.hidden_dim):
            dh_prev[i] += dg[i] * r[i]

        da_r = [dr[i] * r[i] * (1.0 - r[i]) for i in range(self.hidden_dim)]
        _accum_outer(grads["W_r"], da_r, x)
        _accum_outer(grads["U_r"], da_r, h_prev)
        for i in range(self.hidden_dim):
            grads["b_r"][i] += da_r[i]

        da_z = [dz[i] * z[i] * (1.0 - z[i]) for i in range(self.hidden_dim)]
        _accum_outer(grads["W_z"], da_z, x)
        _accum_outer(grads["U_z"], da_z, h_prev)
        for i in range(self.hidden_dim):
            grads["b_z"][i] += da_z[i]

        dh_from_r = _mat_t_vec_mul(self.U_r, da_r)
        dh_from_z = _mat_t_vec_mul(self.U_z, da_z)
        return [dh_prev[i] + dh_from_r[i] + dh_from_z[i] for i in range(self.hidden_dim)]


class TemporalSelfAttention:
    """
    Scaled Dot-Product Temporal Self-Attention over longitudinal hidden states.
    """

    def __init__(self, hidden_dim: int = LATENT_DIM):
        self.hidden_dim = hidden_dim
        self.scale = math.sqrt(hidden_dim)

    def compute(self, hidden_seq: List[List[float]]) -> Tuple[List[float], List[float]]:
        if not hidden_seq:
            return [0.0] * self.hidden_dim, []

        query = hidden_seq[-1]
        scores = [sum(q * k for q, k in zip(query, h)) / self.scale for h in hidden_seq]
        attn_weights = _softmax(scores)

        context = [0.0] * self.hidden_dim
        for w, h in zip(attn_weights, hidden_seq):
            for i in range(self.hidden_dim):
                context[i] += w * h[i]
        return context, attn_weights

    def backward(
        self,
        d_context: List[float],
        hidden_seq: List[List[float]],
        attn_weights: List[float],
    ) -> List[List[float]]:
        T = len(hidden_seq)
        d_alpha = [sum(d_context[i] * hidden_seq[t][i] for i in range(self.hidden_dim)) for t in range(T)]
        dot_da = sum(attn_weights[t] * d_alpha[t] for t in range(T))
        d_scores = [attn_weights[t] * (d_alpha[t] - dot_da) for t in range(T)]

        query = hidden_seq[-1]
        d_hidden = [[attn_weights[t] * d_context[i] for i in range(self.hidden_dim)] for t in range(T)]
        for t in range(T):
            coef = d_scores[t] / self.scale
            for i in range(self.hidden_dim):
                d_hidden[t][i] += coef * query[i]
                d_hidden[-1][i] += coef * hidden_seq[t][i]
        return d_hidden


class DeepForecastingEngine:
    """
    GRU + Temporal Self-Attention Sequence Forecaster for Psychological Trajectories.
    Automatically loads BPTT-trained weights when `DEFAULT_WEIGHTS_PATH` exists;
    otherwise initializes deterministic analytic priors (`weights_trained=False`).
    """

    def __init__(self, weights_path: Optional[str] = DEFAULT_WEIGHTS_PATH, auto_load_trained: bool = True):
        self.gru = DeepGRUCell()
        self.attn = TemporalSelfAttention()
        self.reset_to_analytic_prior()
        if auto_load_trained and weights_path and os.path.exists(weights_path):
            self.load_weights(weights_path)

    def reset_to_analytic_prior(self) -> None:
        self.gru.init_analytic_prior()
        self.W_out = [
            [0.3 * math.sin(c * 0.4 + d) for d in range(LATENT_DIM)]
            for c in range(len(EMOTIONS))
        ]
        self.b_out = [-0.1] * len(EMOTIONS)
        self.W_hazard = [0.4, 0.5, -0.3, -0.1, 0.6, 0.8, 0.7]
        self.b_hazard = 0.0
        self.W_intensity = [0.2 * math.cos(d * 0.6) for d in range(LATENT_DIM)]
        self.b_intensity = 0.0
        self.weights_trained = False
        self.weight_source = "deterministic_analytic_prior"
        self.benchmark_metrics: Optional[Dict[str, Any]] = None

    def export_state_dict(self) -> Dict[str, Any]:
        return {
            "weights_trained": self.weights_trained,
            "weight_source": self.weight_source,
            "benchmark_metrics": self.benchmark_metrics,
            "gru": {
                "W_z": self.gru.W_z, "U_z": self.gru.U_z, "b_z": self.gru.b_z,
                "W_r": self.gru.W_r, "U_r": self.gru.U_r, "b_r": self.gru.b_r,
                "W_n": self.gru.W_n, "U_n": self.gru.U_n, "b_n": self.gru.b_n,
            },
            "W_out": self.W_out,
            "b_out": self.b_out,
            "W_hazard": self.W_hazard,
            "b_hazard": self.b_hazard,
            "W_intensity": self.W_intensity,
            "b_intensity": self.b_intensity,
        }

    def save_weights(self, path: str = DEFAULT_WEIGHTS_PATH) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.export_state_dict(), f, indent=2)

    def load_weights(self, path: str = DEFAULT_WEIGHTS_PATH) -> bool:
        if not os.path.exists(path):
            return False
        with open(path, "r", encoding="utf-8") as f:
            state = json.load(f)
        gru_state = state["gru"]
        self.gru.W_z = gru_state["W_z"]
        self.gru.U_z = gru_state["U_z"]
        self.gru.b_z = gru_state["b_z"]
        self.gru.W_r = gru_state["W_r"]
        self.gru.U_r = gru_state["U_r"]
        self.gru.b_r = gru_state["b_r"]
        self.gru.W_n = gru_state["W_n"]
        self.gru.U_n = gru_state["U_n"]
        self.gru.b_n = gru_state["b_n"]
        self.W_out = state["W_out"]
        self.b_out = state["b_out"]
        self.W_hazard = state["W_hazard"]
        self.b_hazard = float(state.get("b_hazard", 0.0))
        self.W_intensity = state["W_intensity"]
        self.b_intensity = float(state.get("b_intensity", 0.0))
        self.weights_trained = bool(state.get("weights_trained", True))
        self.weight_source = str(state.get("weight_source", "bptt_ema_smartphone_v1"))
        self.benchmark_metrics = state.get("benchmark_metrics")
        return True

    @staticmethod
    def extract_features(m: Any, prev_intensity: float = 0.5) -> List[float]:
        """
        Maps a discrete MoodLog into a continuous 6-D input vector:
        [valence, arousal, delta_intensity, circadian_window, trigger_density, compliance]
        """
        m_type = getattr(m, "mood_type", "neutral").lower()
        intensity = float(getattr(m, "intensity", 0.5))

        valence_map = {
            "calm": 0.7, "focused": 0.6, "motivated": 0.8,
            "neutral": 0.0, "fatigued": -0.4, "stressed": -0.7, "anxious": -0.6,
        }
        arousal_map = {
            "calm": 0.2, "focused": 0.7, "motivated": 0.8,
            "neutral": 0.4, "fatigued": 0.1, "stressed": 0.85, "anxious": 0.90,
        }

        val = valence_map.get(m_type, 0.0)
        arousal = arousal_map.get(m_type, 0.5) * intensity
        delta = intensity - prev_intensity

        created_at = getattr(m, "timestamp", None) or datetime.now(timezone.utc)
        hour = getattr(created_at, "hour", 12)
        circadian = math.sin(2.0 * math.pi * (hour / 24.0))

        trigger_proxy = 0.6 if m_type in ["stressed", "anxious"] else 0.1
        compliance_proxy = 0.8 if m_type in ["focused", "motivated", "calm"] else 0.4
        return [val, arousal, delta, circadian, trigger_proxy, compliance_proxy]

    def _forward_sequence(self, moods: List[Any]) -> Dict[str, Any]:
        hidden = [0.0] * LATENT_DIM
        hidden_history: List[List[float]] = []
        caches: List[Dict[str, List[float]]] = []
        prev_intensity = float(getattr(moods[0], "intensity", 0.5))

        for m in moods:
            x_t = self.extract_features(m, prev_intensity)
            prev_intensity = float(getattr(m, "intensity", 0.5))
            hidden, cache = self.gru.forward_with_cache(x_t, hidden)
            hidden_history.append(hidden)
            caches.append(cache)

        context_vector, attn_weights = self.attn.compute(hidden_history)
        logits = _vec_add(_mat_vec_mul(self.W_out, context_vector), self.b_out)
        probs = _softmax(logits)

        raw_hazard = sum(p * w for p, w in zip(probs, self.W_hazard)) + self.b_hazard
        hazard_prob = _sigmoid(raw_hazard * 1.5)

        raw_intensity = sum(w * c for w, c in zip(self.W_intensity, context_vector)) + self.b_intensity
        pred_intensity = 0.05 + 0.93 * _sigmoid(raw_intensity)

        return {
            "hidden_history": hidden_history,
            "caches": caches,
            "context_vector": context_vector,
            "attn_weights": attn_weights,
            "probs": probs,
            "hazard_prob": hazard_prob,
            "pred_intensity": pred_intensity,
        }

    def compute_sample_loss_and_grads(
        self,
        moods: List[Any],
        target_state_idx: int,
        target_intensity: float,
        target_hazard: float,
        class_weight: float = 1.0,
        intensity_weight: float = 1.0,
        hazard_weight: float = 0.5,
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Computes combined multi-task loss and exact analytic gradients via BPTT
        for one sequence window `(moods -> next_state, next_intensity, next_hazard)`.
        """
        fwd = self._forward_sequence(moods)
        probs = fwd["probs"]
        pred_int = fwd["pred_intensity"]
        haz_prob = fwd["hazard_prob"]
        context = fwd["context_vector"]
        hidden_hist = fwd["hidden_history"]
        caches = fwd["caches"]
        attn_w = fwd["attn_weights"]

        eps = 1e-9
        ce_loss = -math.log(max(eps, probs[target_state_idx]))
        int_err = pred_int - target_intensity
        int_loss = int_err * int_err
        haz_loss = -(
            target_hazard * math.log(max(eps, haz_prob))
            + (1.0 - target_hazard) * math.log(max(eps, 1.0 - haz_prob))
        )
        total_loss = class_weight * ce_loss + intensity_weight * int_loss + hazard_weight * haz_loss

        # Gradients wrt softmax logits from cross-entropy and hazard readout
        d_probs_haz = [hazard_weight * 1.5 * (haz_prob - target_hazard) * w for w in self.W_hazard]
        dot_p_dhaz = sum(probs[k] * d_probs_haz[k] for k in range(len(EMOTIONS)))
        d_logits = [
            class_weight * (probs[k] - (1.0 if k == target_state_idx else 0.0))
            + probs[k] * (d_probs_haz[k] - dot_p_dhaz)
            for k in range(len(EMOTIONS))
        ]

        dW_out = _zeros_mat(len(EMOTIONS), LATENT_DIM)
        _accum_outer(dW_out, d_logits, context)
        db_out = list(d_logits)

        dW_hazard = [hazard_weight * 1.5 * (haz_prob - target_hazard) * p for p in probs]
        db_hazard = hazard_weight * 1.5 * (haz_prob - target_hazard)

        # Intensity sigmoid readout derivative: y = 0.05 + 0.93 * sigmoid(raw)
        sig_int = (pred_int - 0.05) / 0.93
        d_raw_int = intensity_weight * 2.0 * int_err * 0.93 * sig_int * (1.0 - sig_int)
        dW_intensity = [d_raw_int * c for c in context]
        db_intensity = d_raw_int

        d_context_cls = _mat_t_vec_mul(self.W_out, d_logits)
        d_context = [d_context_cls[i] + d_raw_int * self.W_intensity[i] for i in range(LATENT_DIM)]

        d_hidden_attn = self.attn.backward(d_context, hidden_hist, attn_w)
        gru_grads = self.gru.zero_grads()
        dh_rec = [0.0] * LATENT_DIM
        for t in range(len(caches) - 1, -1, -1):
            dh_total = [dh_rec[i] + d_hidden_attn[t][i] for i in range(LATENT_DIM)]
            dh_rec = self.gru.backward_step(dh_total, caches[t], gru_grads)

        grads = {
            "gru": gru_grads,
            "W_out": dW_out,
            "b_out": db_out,
            "W_hazard": dW_hazard,
            "b_hazard": db_hazard,
            "W_intensity": dW_intensity,
            "b_intensity": db_intensity,
        }
        return total_loss, grads

    def _iter_param_grad_pairs(self, grads: Dict[str, Any]):
        for key in ("W_z", "U_z", "W_r", "U_r", "W_n", "U_n"):
            yield ("gru." + key, getattr(self.gru, key), grads["gru"][key], True)
        for key in ("b_z", "b_r", "b_n"):
            yield ("gru." + key, getattr(self.gru, key), grads["gru"][key], False)
        yield ("W_out", self.W_out, grads["W_out"], True)
        yield ("b_out", self.b_out, grads["b_out"], False)
        yield ("W_hazard", self.W_hazard, grads["W_hazard"], False)
        yield ("W_intensity", self.W_intensity, grads["W_intensity"], False)

    def train_on_windows(
        self,
        samples: List[Tuple[List[Any], int, float, float]],
        epochs: int = 12,
        batch_size: int = 32,
        lr: float = 0.015,
        weight_decay: float = 1e-4,
        seed: int = 42,
        weight_source: str = "bptt_ema_smartphone_v1",
    ) -> List[float]:
        """
        Trains GRU, Temporal Attention projection, classification head, intensity head,
        and hazard head end-to-end via mini-batch BPTT + Adam optimization.
        """
        import random

        rng = random.Random(seed)
        adam_m: Dict[str, Any] = {}
        adam_v: Dict[str, Any] = {}
        beta1, beta2, eps = 0.9, 0.999, 1e-8
        step_t = 0
        epoch_losses: List[float] = []

        idx_order = list(range(len(samples)))
        for _ in range(epochs):
            rng.shuffle(idx_order)
            total_loss = 0.0
            for start in range(0, len(idx_order), batch_size):
                batch_ids = idx_order[start : start + batch_size]
                inv_b = 1.0 / max(1, len(batch_ids))
                accum: Optional[Dict[str, Any]] = None

                for idx in batch_ids:
                    window, y_cls, y_int, y_haz = samples[idx]
                    loss, g = self.compute_sample_loss_and_grads(window, y_cls, y_int, y_haz)
                    total_loss += loss
                    if accum is None:
                        accum = g
                    else:
                        for k in ("W_z", "U_z", "W_r", "U_r", "W_n", "U_n"):
                            dst = accum["gru"][k]
                            src = g["gru"][k]
                            for r_i in range(len(dst)):
                                for c_i in range(len(dst[r_i])):
                                    dst[r_i][c_i] += src[r_i][c_i]
                        for k in ("b_z", "b_r", "b_n"):
                            for i in range(len(accum["gru"][k])):
                                accum["gru"][k][i] += g["gru"][k][i]
                        for r_i in range(len(accum["W_out"])):
                            for c_i in range(len(accum["W_out"][r_i])):
                                accum["W_out"][r_i][c_i] += g["W_out"][r_i][c_i]
                        for k in ("b_out", "W_hazard", "W_intensity"):
                            for i in range(len(accum[k])):
                                accum[k][i] += g[k][i]
                        accum["b_hazard"] += g["b_hazard"]
                        accum["b_intensity"] += g["b_intensity"]

                if accum is None:
                    continue

                step_t += 1
                bc1 = 1.0 - (beta1 ** step_t)
                bc2 = 1.0 - (beta2 ** step_t)

                for name, param, grad, is_mat in self._iter_param_grad_pairs(accum):
                    if name not in adam_m:
                        if is_mat:
                            adam_m[name] = _zeros_mat(len(param), len(param[0]))
                            adam_v[name] = _zeros_mat(len(param), len(param[0]))
                        else:
                            adam_m[name] = [0.0] * len(param)
                            adam_v[name] = [0.0] * len(param)
                    m_buf = adam_m[name]
                    v_buf = adam_v[name]
                    if is_mat:
                        for r_i in range(len(param)):
                            for c_i in range(len(param[r_i])):
                                g_val = _clip_grad(grad[r_i][c_i] * inv_b + weight_decay * param[r_i][c_i])
                                m_buf[r_i][c_i] = beta1 * m_buf[r_i][c_i] + (1.0 - beta1) * g_val
                                v_buf[r_i][c_i] = beta2 * v_buf[r_i][c_i] + (1.0 - beta2) * (g_val * g_val)
                                m_hat = m_buf[r_i][c_i] / bc1
                                v_hat = v_buf[r_i][c_i] / bc2
                                param[r_i][c_i] -= lr * m_hat / (math.sqrt(v_hat) + eps)
                    else:
                        for i in range(len(param)):
                            g_val = _clip_grad(grad[i] * inv_b)
                            m_buf[i] = beta1 * m_buf[i] + (1.0 - beta1) * g_val
                            v_buf[i] = beta2 * v_buf[i] + (1.0 - beta2) * (g_val * g_val)
                            m_hat = m_buf[i] / bc1
                            v_hat = v_buf[i] / bc2
                            param[i] -= lr * m_hat / (math.sqrt(v_hat) + eps)

                for scalar_name, attr in (("b_hazard", "b_hazard"), ("b_intensity", "b_intensity")):
                    if scalar_name not in adam_m:
                        adam_m[scalar_name] = 0.0
                        adam_v[scalar_name] = 0.0
                    g_val = _clip_grad(accum[scalar_name] * inv_b)
                    adam_m[scalar_name] = beta1 * adam_m[scalar_name] + (1.0 - beta1) * g_val
                    adam_v[scalar_name] = beta2 * adam_v[scalar_name] + (1.0 - beta2) * (g_val * g_val)
                    m_hat = adam_m[scalar_name] / bc1
                    v_hat = adam_v[scalar_name] / bc2
                    setattr(self, attr, getattr(self, attr) - lr * m_hat / (math.sqrt(v_hat) + eps))

            epoch_losses.append(round(total_loss / max(1, len(samples)), 5))

        self.weights_trained = True
        self.weight_source = weight_source
        return epoch_losses

    def forecast_trajectory(self, moods: List[Any], horizon_steps: int = 3) -> Dict[str, Any]:
        """
        Executes forward recurrent pass through GRU sequence + temporal attention,
        producing emotion probabilities, predicted intensity, burnout hazard, and multi-horizon steps.
        """
        if not moods or len(moods) < 3:
            curr_len = len(moods) if moods else 0
            return {
                "model_type": "deep_neural_sequence",
                "architecture": "GRU_Latent_Transitions_with_Temporal_Self_Attention",
                "weights_trained": self.weights_trained,
                "weight_source": self.weight_source,
                "status": "insufficient_sequence",
                "min_required": 3,
                "required_sequence": 3,
                "current_length": curr_len,
                "sequence_length": curr_len,
            }

        fwd = self._forward_sequence(moods)
        context_vector = fwd["context_vector"]
        attn_weights = fwd["attn_weights"]
        state_distribution = fwd["probs"]
        burnout_hazard_rate = round(fwd["hazard_prob"], 3)
        predicted_intensity = round(max(0.05, min(0.98, fwd["pred_intensity"])), 3)

        distribution_dict = {
            EMOTIONS[i]: round(state_distribution[i], 3)
            for i in range(len(EMOTIONS))
        }
        dominant_predicted_emotion = max(distribution_dict, key=distribution_dict.get)

        seq_uncertainty = round(min(0.28, 0.08 + 0.35 / math.sqrt(max(1, len(moods)))), 3)
        burnout_hazard_ci = [
            round(max(0.0, burnout_hazard_rate - seq_uncertainty), 3),
            round(min(1.0, burnout_hazard_rate + seq_uncertainty), 3),
        ]

        projections = []
        proj_h = list(context_vector)
        for step in range(1, horizon_steps + 1):
            mock_x = [
                distribution_dict.get("calm", 0.2) - distribution_dict.get("stressed", 0.2),
                burnout_hazard_rate,
                0.05 * step,
                math.sin(2.0 * math.pi * ((12 + step * 4) % 24) / 24.0),
                0.3,
                0.7,
            ]
            proj_h = self.gru.forward(mock_x, proj_h)
            step_logits = _vec_add(_mat_vec_mul(self.W_out, proj_h), self.b_out)
            step_probs = _softmax(step_logits)
            step_dom = EMOTIONS[step_probs.index(max(step_probs))]
            step_hazard = round(
                _sigmoid((sum(p * w for p, w in zip(step_probs, self.W_hazard)) + self.b_hazard) * 1.5),
                3,
            )
            projections.append({
                "step": step,
                "projected_state": step_dom,
                "dominant_state": step_dom,
                "confidence": round(max(step_probs), 2),
                "burnout_hazard": step_hazard,
            })

        return {
            "model_type": "deep_neural_sequence",
            "architecture": "GRU_Latent_Transitions_with_Temporal_Self_Attention",
            "weights_trained": self.weights_trained,
            "weight_source": self.weight_source,
            "benchmark_metrics": self.benchmark_metrics,
            "calibrated_statistical_companion": "holt_double_exponential_markov",
            "sequence_length": len(moods),
            "dominant_forecast": dominant_predicted_emotion,
            "predicted_intensity": predicted_intensity,
            "state_distribution": distribution_dict,
            "burnout_hazard_rate": burnout_hazard_rate,
            "burnout_hazard_ci": burnout_hazard_ci,
            "burnout_hazard_level": "Critical" if burnout_hazard_rate > 0.65 else ("Elevated" if burnout_hazard_rate > 0.45 else "Nominal"),
            "temporal_attention_weights": [round(w, 3) for w in attn_weights[-5:]],
            "multi_horizon_projections": projections,
            "latent_representation": [round(v, 3) for v in context_vector],
            "system_version": {"core": "v1.7.0", "deep_forecasting": "v3.0.0"},
        }


deep_forecasting_engine = DeepForecastingEngine()
