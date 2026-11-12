"use client";
import React from "react";
import { Activity, AlertTriangle, TrendingUp } from "lucide-react";

export interface DeepProjectionStep {
  step: number;
  projected_state?: string;
  dominant_state?: string;
  confidence?: number;
  burnout_hazard?: number;
}

export interface DeepForecastData {
  status?: string;
  model_type?: string;
  architecture?: string;
  weights_trained?: boolean;
  weight_source?: string;
  sequence_length?: number;
  required_sequence?: number;
  message?: string;
  dominant_forecast?: string;
  state_distribution?: Record<string, number>;
  burnout_hazard_rate?: number;
  burnout_hazard_ci?: [number, number];
  burnout_hazard_level?: string;
  temporal_attention_weights?: number[];
  multi_horizon_projections?: DeepProjectionStep[];
  latent_representation?: number[];
}

interface DeepForecastCardProps {
  deepForecast: DeepForecastData | null;
  compact?: boolean;
}

export default function DeepForecastCard({ deepForecast, compact = false }: DeepForecastCardProps) {
  if (!deepForecast) return null;

  const isInsufficient = deepForecast.status === "insufficient_sequence";
  const hazardRate = typeof deepForecast.burnout_hazard_rate === "number" ? deepForecast.burnout_hazard_rate : null;
  const hazardPct = hazardRate !== null ? Math.round(hazardRate * 100) : null;
  const hazardLevel = deepForecast.burnout_hazard_level || "Nominal";
  const isCritical = hazardLevel === "Critical" || hazardLevel === "High";
  const isElevated = hazardLevel === "Elevated" || hazardLevel === "Moderate";

  const badgeStyle = isCritical
    ? "bg-red-500/20 text-red-400 border-red-500/30"
    : isElevated
    ? "bg-amber-500/20 text-amber-400 border-amber-500/30"
    : "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";

  return (
    <div className={`bg-[#111726]/80 backdrop-blur-md border border-purple-500/30 rounded-2xl shadow-xl relative overflow-hidden ${compact ? "p-5" : "p-6"}`}>
      <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
        <div className="flex items-center space-x-2">
          <Activity size={18} className="text-purple-400" />
          <h3 className="text-sm font-bold text-gray-200 tracking-wide">
            Gated Latent Trajectory Filter
          </h3>
        </div>
        <span className="text-[10px] font-mono bg-purple-950/60 border border-purple-500/30 text-purple-300 px-2.5 py-0.5 rounded-full">
          {deepForecast.weights_trained === false
            ? "Analytic GRU Prior (Untrained)"
            : deepForecast.architecture === "GRU_Latent_Transitions_with_Temporal_Self_Attention"
            ? "Analytic GRU Prior (Untrained)"
            : deepForecast.model_type || "State-Space Filter"}
        </span>
      </div>

      {isInsufficient ? (
        <div className="bg-black/40 border border-gray-800/80 rounded-xl p-4 flex items-start space-x-3">
          <AlertTriangle size={18} className="text-amber-400 shrink-0 mt-0.5" />
          <div>
            <p className="text-xs font-semibold text-gray-200 mb-1">
              Calibrating Sequential Baseline ({deepForecast.sequence_length ?? 0}/{deepForecast.required_sequence ?? 3} logs)
            </p>
            <p className="text-xs text-gray-400 leading-relaxed">
              {deepForecast.message || "Log at least 3 mood check-ins so the recurrent sequence model can compute multi-step state projections and burnout hazard."}
            </p>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="bg-black/40 border border-gray-800/80 rounded-xl p-3">
              <div className="text-[10px] text-gray-400 uppercase tracking-wider mb-1">Dominant Horizon State</div>
              <div className="text-lg font-bold capitalize text-purple-300 flex items-center space-x-2">
                <span>{deepForecast.dominant_forecast || "neutral"}</span>
                <TrendingUp size={15} className="text-purple-400" />
              </div>
              <div className="text-[11px] text-gray-500 mt-0.5">
                From {deepForecast.sequence_length ?? 0}-step emotional history
              </div>
            </div>

            <div className="bg-black/40 border border-gray-800/80 rounded-xl p-3">
              <div className="text-[10px] text-gray-400 uppercase tracking-wider mb-1">Burnout Hazard Rate</div>
              <div className="flex items-center space-x-2">
                <span className="text-lg font-bold font-mono text-gray-100">
                  {hazardPct !== null ? `${hazardPct}%` : "N/A"}
                </span>
                <span className={`text-[10px] px-2 py-0.5 rounded-full border font-semibold ${badgeStyle}`}>
                  {hazardLevel}
                </span>
              </div>
              {Array.isArray(deepForecast.burnout_hazard_ci) && deepForecast.burnout_hazard_ci.length === 2 && (
                <div className="text-[10px] text-gray-500 font-mono mt-0.5">
                  Uncertainty band: {Math.round(deepForecast.burnout_hazard_ci[0] * 100)}%–{Math.round(deepForecast.burnout_hazard_ci[1] * 100)}%
                </div>
              )}
            </div>
          </div>

          {deepForecast.state_distribution && (
            <div className="bg-black/30 border border-gray-800/70 rounded-xl p-3 space-y-2">
              <div className="text-[10px] text-gray-400 uppercase tracking-wider">Projected State Distribution</div>
              {Object.entries(deepForecast.state_distribution)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 4)
                .map(([state, prob]) => (
                  <div key={state} className="flex items-center space-x-2">
                    <div className="text-xs text-gray-400 w-20 capitalize truncate">{state}</div>
                    <div className="flex-1 bg-gray-800 rounded-full h-1.5">
                      <div className="bg-purple-500 h-1.5 rounded-full" style={{ width: `${(prob * 100).toFixed(0)}%` }} />
                    </div>
                    <div className="text-xs text-gray-400 font-mono w-9 text-right">{(prob * 100).toFixed(0)}%</div>
                  </div>
                ))}
            </div>
          )}

          {Array.isArray(deepForecast.multi_horizon_projections) && deepForecast.multi_horizon_projections.length > 0 && (
            <div className="grid grid-cols-3 gap-2">
              {deepForecast.multi_horizon_projections.map((proj) => {
                const stateLabel = proj.projected_state || proj.dominant_state || "neutral";
                const stepHazard =
                  typeof proj.burnout_hazard === "number"
                    ? `${Math.round(proj.burnout_hazard * 100)}% hazard`
                    : typeof proj.confidence === "number"
                    ? `${Math.round(proj.confidence * 100)}% conf`
                    : "projected";
                return (
                  <div key={proj.step} className="bg-black/30 border border-gray-800/70 rounded-lg p-2.5 text-center">
                    <div className="text-[10px] font-mono text-gray-400">Step +{proj.step}</div>
                    <div className="text-xs font-semibold capitalize text-gray-100 mt-0.5">{stateLabel}</div>
                    <div className="text-[10px] font-mono text-purple-300 mt-0.5">{stepHazard}</div>
                  </div>
                );
              })}
            </div>
          )}

          {Array.isArray(deepForecast.temporal_attention_weights) && deepForecast.temporal_attention_weights.length > 0 && (
            <div>
              <div className="flex justify-between text-[10px] text-gray-400 mb-1">
                <span>Recent Temporal Attention Weights</span>
                <span className="font-mono">{deepForecast.temporal_attention_weights.length} steps</span>
              </div>
              <div className="flex items-end space-x-1 h-7">
                {deepForecast.temporal_attention_weights.map((w, idx) => (
                  <div
                    key={idx}
                    title={`t-${deepForecast.temporal_attention_weights!.length - idx}: ${Math.round(w * 100)}%`}
                    className="flex-1 bg-purple-500/70 rounded-t transition-all"
                    style={{ height: `${Math.max(18, Math.min(100, Math.round(w * 200)))}%` }}
                  />
                ))}
              </div>
            </div>
          )}

          {deepForecast.weights_trained !== true && (
            <div className="text-[11px] text-gray-400 bg-black/30 border border-gray-800/80 rounded-lg px-3 py-2">
              Architecture disclosure: Pure-Python GRU gate equations using fixed analytic priors (untrained; no neural training or PyTorch/TF weights). Paired with the fitted Holt-Markov statistical model.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
