"use client";
import React, { useState } from "react";
import { Eye, EyeOff, Brain, AlertCircle, Sparkles, TrendingUp } from "lucide-react";

interface ReasoningTraceProps {
  agents?: {
    prediction?: { output?: any; confidence?: number };
    strategy?: { output?: string; confidence?: number };
    meta?: { output?: any; confidence?: number };
    cognition?: { output?: any; confidence?: number };
  };
  synthesizedPayload?: {
    final_decision?: string;
    reasoning?: string;
    conflicts_detected?: string[];
  };
  confidenceTrace?: Record<string, string[]>;
}

export default function ReasoningTrace({
  agents = {},
  synthesizedPayload = {},
  confidenceTrace = {},
}: ReasoningTraceProps) {
  const [showTrace, setShowTrace] = useState(false);

  const predOutput = agents.prediction?.output || {};
  const stratOutput = agents.strategy?.output || "unknown";
  const conflicts = synthesizedPayload.conflicts_detected || [];

  return (
    <div className="backdrop-blur-md bg-gray-900/40 border border-gray-800/60 rounded-2xl p-6 w-full space-y-6">
      <div>
        <span className="text-[10px] text-gray-500 uppercase tracking-widest block font-medium">Cognitive Trace</span>
        <h3 className="text-lg font-light text-gray-100 mt-1">Reasoning Trace</h3>
      </div>

      <div className="space-y-4">
        {/* Prediction Layer */}
        <div className="flex gap-4 items-start p-4 bg-gray-900/20 border border-gray-800/40 rounded-xl">
          <div className="p-2 bg-blue-500/10 rounded-lg text-blue-400">
            <TrendingUp className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-semibold text-gray-300">🔮 Prediction Projection</h4>
            <p className="text-xs text-gray-400 mt-1 leading-relaxed">
              Stress Trajectory is forecast to change by{" "}
              <span className="text-blue-400 font-mono">
                {predOutput.stress_delta ? `${(predOutput.stress_delta * 100).toFixed(0)}%` : "N/A"}
              </span>{" "}
              based on recent mood indicators. Risk Category:{" "}
              <span className="text-blue-400 capitalize">{predOutput.risk || "None"}</span>.
            </p>
          </div>
        </div>

        {/* Strategy Layer */}
        <div className="flex gap-4 items-start p-4 bg-gray-900/20 border border-gray-800/40 rounded-xl">
          <div className="p-2 bg-emerald-500/10 rounded-lg text-emerald-400">
            <Brain className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-semibold text-gray-300">🎯 Strategy Formulation</h4>
            <p className="text-xs text-gray-400 mt-1 leading-relaxed">
              Selected behavioral option: <span className="text-emerald-400 font-mono capitalize">{stratOutput}</span>. 
              Historically stable nudge effectiveness is tracked at{" "}
              <span className="text-emerald-400 font-mono">
                {agents.strategy?.confidence ? `${(agents.strategy.confidence * 100).toFixed(0)}%` : "75%"}
              </span>.
            </p>
          </div>
        </div>

        {/* Conflict Resolution */}
        <div className="flex gap-4 items-start p-4 bg-gray-900/20 border border-gray-800/40 rounded-xl">
          <div className="p-2 bg-amber-500/10 rounded-lg text-amber-400">
            <AlertCircle className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-semibold text-gray-300">⚖️ Conflict Resolution</h4>
            <p className="text-xs text-gray-400 mt-1 leading-relaxed">
              {conflicts.length > 0 ? (
                <span className="text-amber-400">
                  Override applied: {conflicts.join(", ")}
                </span>
              ) : (
                "Total Agent Alignment. No hard overrides required during cognitive consolidation."
              )}
            </p>
          </div>
        </div>

        {/* Synthesis */}
        <div className="flex gap-4 items-start p-4 bg-purple-500/5 border border-purple-500/20 rounded-xl">
          <div className="p-2 bg-purple-500/10 rounded-lg text-purple-400">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-semibold text-purple-300">🧠 Cognitive Synthesis</h4>
            <p className="text-xs text-gray-300 mt-1 leading-relaxed">
              {synthesizedPayload.reasoning || "Consolidating agent recommendations..."}
            </p>
          </div>
        </div>
      </div>

      {/* Expandable Why Confidence Changed */}
      {Object.keys(confidenceTrace).length > 0 && (
        <div className="border-t border-gray-800/60 pt-4">
          <button
            onClick={() => setShowTrace(!showTrace)}
            className="flex items-center gap-2 text-xs font-semibold text-purple-400 hover:text-purple-300 transition-colors"
          >
            {showTrace ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            {showTrace ? "Hide Calibration Analysis" : "Why Confidence Calibrated?"}
          </button>

          {showTrace && (
            <div className="mt-4 bg-gray-950/40 border border-gray-800 rounded-xl p-4 space-y-3">
              {Object.entries(confidenceTrace).map(([agent, traces]) => (
                <div key={agent} className="text-xs">
                  <span className="font-mono text-purple-400 uppercase text-[10px] block font-semibold">
                    {agent}
                  </span>
                  {traces.length > 0 ? (
                    <ul className="list-disc list-inside mt-1 space-y-1 text-gray-400 pl-1">
                      {traces.map((trace, idx) => (
                        <li key={idx} className="text-[11px] leading-relaxed">{trace}</li>
                      ))}
                    </ul>
                  ) : (
                    <span className="text-[11px] text-gray-600 block mt-0.5 pl-1">No calibration adjustments applied (stable).</span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
