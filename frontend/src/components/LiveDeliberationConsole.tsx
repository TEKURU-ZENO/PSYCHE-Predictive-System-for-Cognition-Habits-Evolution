"use client";
import { useState, useEffect } from "react";
import { Brain, Cpu, ShieldCheck, Sparkles, CheckCircle2, Flame, Layers } from "lucide-react";

interface StreamFrame {
  stage: string;
  step: number;
  message: string;
  data?: any;
}

interface LiveDeliberationConsoleProps {
  currentStage?: string;
  currentStep?: number;
  isStreaming: boolean;
}

const STAGES = [
  { key: "perception", label: "Perception & Memory", desc: "Extracting state & autobiographical precedent" },
  { key: "agents_deliberating", label: "Parallel Agents", desc: "Competing role-lens formulations" },
  { key: "calibration", label: "Dynamic Calibration", desc: "Recency decay & trust weighting" },
  { key: "synthesis", label: "Debate Synthesis", desc: "Reconciling conflicting perspectives" },
  { key: "red_team_audit", label: "Adversarial Audit", desc: "Testing sycophancy & veto flags" },
  { key: "completed", label: "Decision Locked", desc: "Tamper-evident SHA-256 stamping" }
];

export default function LiveDeliberationConsole({ currentStage = "perception", currentStep = 1, isStreaming }: LiveDeliberationConsoleProps) {
  if (!isStreaming) return null;

  return (
    <div className="bg-[#0B0F1A] border border-purple-500/40 rounded-3xl p-6 md:p-8 shadow-2xl space-y-6 animate-in fade-in duration-300 relative overflow-hidden">
      <div className="absolute top-0 right-0 p-8 opacity-5 pointer-events-none">
        <Brain size={140} />
      </div>

      <div className="flex justify-between items-center relative z-10">
        <div>
          <h3 className="text-sm font-bold text-gray-200 uppercase tracking-widest flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-500 animate-ping"></span>
            <span>Real-Time Deliberation Stream</span>
          </h3>
          <p className="text-xs text-gray-400 mt-0.5">
            Progressively streaming cognitive deliberation across 5 autonomous agents.
          </p>
        </div>
        <span className="text-[10px] bg-purple-900/40 text-purple-300 font-mono px-3 py-1 rounded-full border border-purple-500/30">
          Step {currentStep} of 6
        </span>
      </div>

      {/* Progress Steps */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-2 relative z-10">
        {STAGES.map((s, idx) => {
          const stepNumber = idx + 1;
          const isDone = currentStep > stepNumber;
          const isCurrent = currentStep === stepNumber;

          return (
            <div
              key={s.key}
              className={`p-3 rounded-2xl border text-left transition-all ${
                isDone
                  ? "bg-purple-950/30 border-purple-500/40 text-purple-300"
                  : isCurrent
                  ? "bg-[#111827] border-purple-500 shadow-[0_0_15px_rgba(168,85,247,0.2)] text-white"
                  : "bg-gray-900/30 border-gray-800 text-gray-600"
              }`}
            >
              <div className="flex justify-between items-center mb-1">
                <span className="text-[10px] font-mono">0{stepNumber}</span>
                {isDone ? (
                  <CheckCircle2 size={12} className="text-emerald-400" />
                ) : isCurrent ? (
                  <span className="w-2 h-2 rounded-full bg-purple-400 animate-pulse"></span>
                ) : null}
              </div>
              <h5 className="text-xs font-semibold truncate">{s.label}</h5>
              <p className="text-[9px] text-gray-400 line-clamp-1 mt-0.5">{s.desc}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
