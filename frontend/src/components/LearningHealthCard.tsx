"use client";
import React from "react";
import { Zap, Activity, RefreshCw } from "lucide-react";

interface LearningHealthCardProps {
  learningHealth?: {
    status: string;
    effectiveness?: {
      variance?: number;
      learning_health?: string;
    };
  };
  policyEntropy?: number;
  recoveryModeActive?: boolean;
}

export default function LearningHealthCard({
  learningHealth,
  policyEntropy = 0.82,
  recoveryModeActive = false,
}: LearningHealthCardProps) {
  const healthStatus = learningHealth?.status || "healthy";
  const learningHealthType = learningHealth?.effectiveness?.learning_health || "stable";
  const variance = learningHealth?.effectiveness?.variance ?? 0.05;

  const isUnstable = healthStatus === "unstable" || learningHealthType === "unstable";
  const isAdapting = healthStatus === "learning_uncertain" || learningHealthType === "declining";

  // Calculate dynamic stability score (0 to 100)
  const stabilityScore = Math.max(
    10,
    Math.min(100, Math.round(100 - variance * 200 - (isUnstable ? 40 : isAdapting ? 15 : 0)))
  );

  return (
    <div className="backdrop-blur-md bg-gray-900/40 border border-gray-800/60 rounded-2xl p-6 w-full space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <span className="text-[10px] text-gray-500 uppercase tracking-widest block font-medium">Policy Quality</span>
          <h3 className="text-lg font-light text-gray-100 mt-1">Learning Health</h3>
        </div>

        {recoveryModeActive && (
          <div className="flex items-center gap-1 bg-red-950/40 border border-red-500/30 text-red-400 px-2 py-0.5 rounded text-[10px] uppercase font-mono animate-pulse">
            <RefreshCw className="w-3 h-3 animate-spin" />
            Recovery Mode Active
          </div>
        )}
      </div>

      <div className="flex flex-col md:flex-row gap-6 items-center justify-between">
        {/* Animated State Ring */}
        <div className="relative w-32 h-32 flex items-center justify-center">
          <svg className="w-full h-full transform -rotate-90">
            {/* Background Track */}
            <circle
              cx="64"
              cy="64"
              r="52"
              fill="none"
              stroke="#1f2937"
              strokeWidth="6"
            />
            {/* Health Path */}
            <circle
              cx="64"
              cy="64"
              r="52"
              fill="none"
              stroke={isUnstable ? "#ef4444" : isAdapting ? "#f59e0b" : "#8b5cf6"}
              strokeWidth="6"
              strokeDasharray={`${2 * Math.PI * 52}`}
              strokeDashoffset={`${2 * Math.PI * 52 * (1 - stabilityScore / 100)}`}
              strokeLinecap="round"
              className="transition-all duration-1000 ease-out"
            />
          </svg>

          {/* Central Percentage */}
          <div className={`absolute flex flex-col items-center justify-center text-center ${
            isUnstable ? "animate-bounce" : ""
          }`}>
            <span className="text-2xl font-mono font-light text-gray-100">{stabilityScore}%</span>
            <span className="text-[9px] text-gray-500 uppercase tracking-wider font-semibold">Stability</span>
          </div>
        </div>

        {/* Learning Metrics */}
        <div className="flex-1 w-full space-y-4">
          {/* Entropy */}
          <div className="flex justify-between items-center bg-gray-900/20 border border-gray-800/40 p-3 rounded-xl">
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-purple-400" />
              <span className="text-xs text-gray-400">Policy Entropy</span>
            </div>
            <span className="text-xs font-mono font-medium text-gray-200">{policyEntropy.toFixed(3)}</span>
          </div>

          {/* Exploration Drift */}
          <div className="flex justify-between items-center bg-gray-900/20 border border-gray-800/40 p-3 rounded-xl">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-emerald-400" />
              <span className="text-xs text-gray-400">Variance Drift</span>
            </div>
            <span className="text-xs font-mono font-medium text-gray-200">{variance.toFixed(4)}</span>
          </div>

          {/* Status Indicator */}
          <div className="text-[10px] text-gray-500 italic pl-1">
            {isUnstable
              ? "Critical variance detected. RL updates locked to prevent collapse."
              : isAdapting
              ? "Exploring options actively. Stability threshold nominal."
              : "Policy consolidated. High confidence execution mode."}
          </div>
        </div>
      </div>
    </div>
  );
}
