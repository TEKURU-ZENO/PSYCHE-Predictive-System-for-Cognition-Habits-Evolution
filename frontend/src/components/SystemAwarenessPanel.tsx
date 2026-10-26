"use client";
import React from "react";
import { Activity, ShieldAlert, Cpu, Sparkles } from "lucide-react";

interface SystemAwarenessPanelProps {
  learningHealth?: {
    status: string;
    effectiveness: {
      success_rate: number;
      status: string;
      trend: string;
      learning_health: string;
    };
  };
  dominantAgent?: string;
  effectiveAccuracies?: Record<string, number>;
}

export default function SystemAwarenessPanel({
  learningHealth,
  dominantAgent,
  effectiveAccuracies,
}: SystemAwarenessPanelProps) {
  // Default values
  const healthStatus = learningHealth?.status || "healthy";
  const successRate = learningHealth?.effectiveness?.success_rate ?? 0.85;
  const trend = learningHealth?.effectiveness?.trend || "→";
  const learningHealthType = learningHealth?.effectiveness?.learning_health || "stable";

  // Calculate average reliability
  const avgAcc = effectiveAccuracies
    ? Object.values(effectiveAccuracies).reduce((a, b) => a + b, 0) /
      Object.keys(effectiveAccuracies).length
    : 0.88;

  let stabilityState = "Stable";
  let pulseColor = "bg-emerald-500 shadow-emerald-500/50";
  let textColor = "text-emerald-400";
  let borderGlow = "border-emerald-500/20 shadow-[0_0_20px_rgba(16,185,129,0.05)]";

  if (healthStatus === "unstable" || learningHealthType === "unstable") {
    stabilityState = "Unstable";
    pulseColor = "bg-red-500 shadow-red-500/50";
    textColor = "text-red-400";
    borderGlow = "border-red-500/20 shadow-[0_0_20px_rgba(239,68,68,0.05)]";
  } else if (healthStatus === "learning_uncertain" || learningHealthType === "declining") {
    stabilityState = "Adapting";
    pulseColor = "bg-amber-500 shadow-amber-500/50";
    textColor = "text-amber-400";
    borderGlow = "border-amber-500/20 shadow-[0_0_20px_rgba(245,158,11,0.05)]";
  }

  return (
    <div className={`backdrop-blur-md bg-gray-900/60 border ${borderGlow} rounded-2xl p-6 relative overflow-hidden transition-all duration-300 w-full`}>
      {/* Soft pulse behind panel */}
      <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-purple-500/10 to-transparent rounded-full blur-2xl"></div>

      <div className="flex justify-between items-start mb-6">
        <div>
          <span className="text-[10px] text-gray-500 uppercase tracking-widest block font-medium">Cognitive Status</span>
          <h2 className="text-xl font-light text-gray-100 tracking-wide mt-1">System Awareness</h2>
        </div>
        <div className="flex items-center gap-2 bg-gray-800/40 border border-gray-700/50 px-3 py-1 rounded-xl">
          <span className="relative flex h-2 w-2">
            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${pulseColor}`}></span>
            <span className={`relative inline-flex rounded-full h-2 w-2 ${pulseColor}`}></span>
          </span>
          <span className={`text-xs font-mono font-medium ${textColor}`}>{stabilityState}</span>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Metric 1 */}
        <div className="bg-gray-900/40 border border-gray-800/60 rounded-xl p-4 flex flex-col justify-between">
          <span className="text-[10px] text-gray-500 uppercase tracking-widest">Dominant Agent</span>
          <div className="flex items-center gap-2 mt-2">
            <Cpu className="w-4 h-4 text-purple-400" />
            <span className="text-sm font-mono capitalize truncate text-purple-300 font-semibold">
              {dominantAgent || "orchestrator"}
            </span>
          </div>
        </div>

        {/* Metric 2 */}
        <div className="bg-gray-900/40 border border-gray-800/60 rounded-xl p-4 flex flex-col justify-between">
          <span className="text-[10px] text-gray-500 uppercase tracking-widest">System Trust</span>
          <div className="flex items-center gap-2 mt-2">
            <Activity className="w-4 h-4 text-emerald-400" />
            <span className="text-sm font-mono text-emerald-300 font-semibold">
              {(avgAcc * 100).toFixed(0)}% Accuracy
            </span>
          </div>
        </div>

        {/* Metric 3 */}
        <div className="bg-gray-900/40 border border-gray-800/60 rounded-xl p-4 flex flex-col justify-between">
          <span className="text-[10px] text-gray-500 uppercase tracking-widest">Learning Status</span>
          <div className="flex items-center gap-2 mt-2">
            <Sparkles className="w-4 h-4 text-blue-400" />
            <span className="text-sm font-mono text-blue-300 font-semibold capitalize flex items-center gap-1">
              {learningHealthType} <span className="font-sans text-xs">{trend}</span>
            </span>
          </div>
        </div>

        {/* Metric 4 */}
        <div className="bg-gray-900/40 border border-gray-800/60 rounded-xl p-4 flex flex-col justify-between">
          <span className="text-[10px] text-gray-500 uppercase tracking-widest">System Effect</span>
          <div className="flex items-center gap-2 mt-2">
            <ShieldAlert className="w-4 h-4 text-amber-400" />
            <span className="text-sm font-mono text-amber-300 font-semibold">
              +{(successRate * 100 * 0.35).toFixed(1)}% outcome
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
