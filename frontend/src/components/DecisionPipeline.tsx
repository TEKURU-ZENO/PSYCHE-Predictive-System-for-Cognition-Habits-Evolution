"use client";
import React from "react";
import { ArrowRight, Brain, Cpu, Sparkles, UserCheck, ShieldAlert, Award } from "lucide-react";

interface DecisionPipelineProps {
  weights?: Record<string, number>;
  conflicts?: string[];
  synthesizedPayload?: {
    confidence?: number;
    final_decision?: string;
  };
}

export default function DecisionPipeline({
  weights = {},
  conflicts = [],
  synthesizedPayload = {},
}: DecisionPipelineProps) {
  const confidence = synthesizedPayload.confidence ?? 0.85;
  const decision = synthesizedPayload.final_decision || "take_break";

  const pipelineStages = [
    {
      id: "perception",
      name: "Perception",
      icon: <Brain className="w-4 h-4 text-blue-400" />,
      desc: "Distress mapped",
      color: "border-blue-500/20 bg-blue-950/10 text-blue-400",
    },
    {
      id: "agents",
      name: "Agent Layers",
      icon: <Cpu className="w-4 h-4 text-purple-400" />,
      desc: `${Object.keys(weights).length} Parallel Engines`,
      color: "border-purple-500/20 bg-purple-950/10 text-purple-400",
    },
    {
      id: "aggregator",
      name: "Consolidation",
      icon: <Sparkles className="w-4 h-4 text-emerald-400" />,
      desc: conflicts.length > 0 ? "Override Applied" : "Calibrated Weights",
      color: conflicts.length > 0 
        ? "border-amber-500/30 bg-amber-950/15 text-amber-400" 
        : "border-emerald-500/20 bg-emerald-950/10 text-emerald-400",
    },
    {
      id: "debate",
      name: "LLM Debate",
      icon: <ShieldAlert className="w-4 h-4 text-indigo-400" />,
      desc: `${(confidence * 100).toFixed(0)}% Consensus`,
      color: "border-indigo-500/20 bg-indigo-950/10 text-indigo-400",
    },
    {
      id: "output",
      name: "Final Output",
      icon: <Award className="w-4 h-4 text-pink-400" />,
      desc: decision,
      color: "border-pink-500/30 bg-pink-950/15 text-pink-400 font-semibold uppercase",
    },
  ];

  return (
    <div className="backdrop-blur-md bg-gray-900/40 border border-gray-800/60 rounded-2xl p-6 w-full space-y-6">
      <div>
        <span className="text-[10px] text-gray-500 uppercase tracking-widest block font-medium">Pipeline Execution</span>
        <h3 className="text-lg font-light text-gray-100 mt-1">Decision Trace Flow</h3>
      </div>

      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4 relative">
        {pipelineStages.map((stage, idx) => (
          <React.Fragment key={stage.id}>
            {/* Stage Box */}
            <div className={`flex-1 border rounded-xl p-4 flex flex-col items-center text-center transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg ${stage.color}`}>
              <div className="p-2 bg-gray-900/60 rounded-lg mb-2">
                {stage.icon}
              </div>
              <span className="text-[11px] font-semibold tracking-wider uppercase">{stage.name}</span>
              <span className="text-[10px] text-gray-400 mt-1 truncate max-w-full px-1">{stage.desc}</span>
            </div>

            {/* Connecting Arrow */}
            {idx < pipelineStages.length - 1 && (
              <div className="hidden md:flex items-center text-gray-700">
                <ArrowRight className="w-4 h-4" />
              </div>
            )}
          </React.Fragment>
        ))}
      </div>

      {conflicts.length > 0 && (
        <div className="mt-4 p-3 bg-amber-950/20 border border-amber-500/20 rounded-xl flex items-start gap-2.5">
          <ShieldAlert className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
          <div className="text-xs text-amber-400/90 leading-normal">
            <span className="font-semibold block mb-0.5">Override Detected in Pipeline</span>
            {conflicts.join(", ")}
          </div>
        </div>
      )}
    </div>
  );
}
