"use client";
import { useState } from "react";
import { GitBranch, Flame, BatteryCharging, ShieldAlert, Award, ArrowRight } from "lucide-react";

interface Branch {
  branch_name: string;
  action_key: string;
  projected_stress_48h: number;
  projected_burnout_risk: number;
  projected_dissonance: number;
  cognitive_energy_delta: number;
  expected_q_value: number;
  expected_payoff: number;
  recommendation_rank: number;
  tradeoff_analysis: string;
}

interface CounterfactualProps {
  branches?: Branch[];
}

export default function CounterfactualBranchingView({ branches = [] }: CounterfactualProps) {
  const [selectedBranch, setSelectedBranch] = useState<number>(0);

  if (!branches || branches.length === 0) return null;

  const active = branches[selectedBranch] || branches[0];

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-3xl p-6 md:p-8 shadow-2xl relative overflow-hidden">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-2">
        <div>
          <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest flex items-center gap-2">
            <GitBranch size={16} className="text-purple-400" />
            <span>Counterfactual Shadow Simulation (What-If Branching)</span>
          </h3>
          <p className="text-xs text-gray-500 mt-1">
            Simulating divergent decision paths, 48-hour burnout trajectories, and expected cognitive payoffs.
          </p>
        </div>
        <span className="text-[10px] bg-purple-900/40 text-purple-300 font-mono px-2.5 py-1 rounded-full border border-purple-500/30">
          Phase 12 Shadow Engine
        </span>
      </div>

      {/* Branch Selector Tabs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-6">
        {branches.map((b, idx) => {
          const isSelected = selectedBranch === idx;
          const isRank1 = b.recommendation_rank === 1;
          const isPush = b.action_key === "push_through";

          return (
            <button
              key={idx}
              onClick={() => setSelectedBranch(idx)}
              className={`p-3 rounded-2xl border text-left transition-all relative flex flex-col justify-between ${
                isSelected
                  ? "bg-purple-950/40 border-purple-500/70 shadow-[0_0_15px_rgba(168,85,247,0.15)]"
                  : "bg-[#0B0F1A] border-gray-800 hover:border-gray-700 text-gray-400"
              }`}
            >
              <div>
                <div className="flex justify-between items-center mb-1">
                  <span className="text-[10px] font-mono text-gray-500">Path #{idx + 1}</span>
                  {isRank1 && (
                    <span className="text-[9px] bg-emerald-950/60 text-emerald-400 border border-emerald-500/40 px-1.5 py-0.2 rounded font-mono flex items-center gap-0.5">
                      <Award size={9} /> Top Choice
                    </span>
                  )}
                  {isPush && (
                    <span className="text-[9px] bg-red-950/60 text-red-400 border border-red-500/40 px-1.5 py-0.2 rounded font-mono">
                      High Friction
                    </span>
                  )}
                </div>
                <h4 className={`text-xs font-semibold ${isSelected ? "text-white" : "text-gray-300"}`}>
                  {b.branch_name}
                </h4>
              </div>

              <div className="mt-2 text-[10px] font-mono flex justify-between text-gray-500 pt-2 border-t border-gray-800/80">
                <span>Payoff:</span>
                <span className={b.expected_payoff >= 0.7 ? "text-emerald-400 font-bold" : "text-amber-400"}>
                  {(b.expected_payoff * 100).toFixed(0)}%
                </span>
              </div>
            </button>
          );
        })}
      </div>

      {/* Selected Branch Deep Dive Matrix */}
      <div className="bg-[#0B0F1A] border border-gray-800/90 rounded-2xl p-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 pb-4 border-b border-gray-800 gap-3">
          <div>
            <div className="flex items-center gap-2">
              <h4 className="text-base font-semibold text-gray-100">{active.branch_name}</h4>
              <span className="text-xs font-mono text-purple-400 bg-purple-950/50 px-2 py-0.5 rounded border border-purple-500/20">
                Action: {active.action_key}
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-1 max-w-2xl leading-relaxed">
              {active.tradeoff_analysis}
            </p>
          </div>

          <div className="text-right shrink-0">
            <span className="text-[10px] text-gray-500 uppercase tracking-widest block mb-0.5">Expected Cognitive Payoff</span>
            <span className={`text-2xl font-bold font-mono ${
              active.expected_payoff >= 0.7 ? "text-emerald-400" : active.expected_payoff >= 0.5 ? "text-amber-400" : "text-red-400"
            }`}>
              {(active.expected_payoff * 100).toFixed(0)}%
            </span>
          </div>
        </div>

        {/* Projections Comparative Meters */}
        <div className="grid md:grid-cols-4 gap-4">
          {/* 1. 48h Projected Stress */}
          <div className="bg-[#111827] p-4 rounded-xl border border-gray-800 space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="text-gray-400 flex items-center gap-1.5">
                <Flame size={13} className="text-orange-400" /> 48h Stress
              </span>
              <span className={`font-mono text-xs ${active.projected_stress_48h > 0.6 ? "text-red-400 font-bold" : "text-emerald-400"}`}>
                {(active.projected_stress_48h * 100).toFixed(0)}%
              </span>
            </div>
            <div className="w-full h-1.5 bg-gray-900 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${active.projected_stress_48h > 0.6 ? "bg-red-500" : "bg-emerald-500"}`}
                style={{ width: `${active.projected_stress_48h * 100}%` }}
              ></div>
            </div>
            <span className="text-[9px] text-gray-500 block">Sustained tension trajectory</span>
          </div>

          {/* 2. Burnout Risk */}
          <div className="bg-[#111827] p-4 rounded-xl border border-gray-800 space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="text-gray-400 flex items-center gap-1.5">
                <ShieldAlert size={13} className="text-red-400" /> Burnout Risk
              </span>
              <span className={`font-mono text-xs ${active.projected_burnout_risk > 0.6 ? "text-red-400 font-bold" : "text-emerald-400"}`}>
                {(active.projected_burnout_risk * 100).toFixed(0)}%
              </span>
            </div>
            <div className="w-full h-1.5 bg-gray-900 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${active.projected_burnout_risk > 0.6 ? "bg-red-500" : "bg-emerald-500"}`}
                style={{ width: `${active.projected_burnout_risk * 100}%` }}
              ></div>
            </div>
            <span className="text-[9px] text-gray-500 block">Systemic exhaustion forecast</span>
          </div>

          {/* 3. Energy Delta */}
          <div className="bg-[#111827] p-4 rounded-xl border border-gray-800 space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="text-gray-400 flex items-center gap-1.5">
                <BatteryCharging size={13} className="text-purple-400" /> Energy Delta
              </span>
              <span className={`font-mono text-xs ${active.cognitive_energy_delta >= 0 ? "text-emerald-400 font-bold" : "text-red-400"}`}>
                {active.cognitive_energy_delta >= 0 ? `+${(active.cognitive_energy_delta * 100).toFixed(0)}%` : `${(active.cognitive_energy_delta * 100).toFixed(0)}%`}
              </span>
            </div>
            <div className="w-full h-1.5 bg-gray-900 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${active.cognitive_energy_delta >= 0 ? "bg-purple-500" : "bg-red-500"}`}
                style={{ width: `${Math.abs(active.cognitive_energy_delta) * 100}%` }}
              ></div>
            </div>
            <span className="text-[9px] text-gray-500 block">Dopaminergic recovery velocity</span>
          </div>

          {/* 4. Empirical Q-Policy Value */}
          <div className="bg-[#111827] p-4 rounded-xl border border-gray-800 space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="text-gray-400 flex items-center gap-1.5">
                <Award size={13} className="text-indigo-400" /> Policy Value (Q)
              </span>
              <span className="font-mono text-xs text-indigo-300">
                {(active.expected_q_value * 100).toFixed(0)}%
              </span>
            </div>
            <div className="w-full h-1.5 bg-gray-900 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full bg-indigo-500 transition-all duration-500"
                style={{ width: `${active.expected_q_value * 100}%` }}
              ></div>
            </div>
            <span className="text-[9px] text-gray-500 block">Empirical reinforcement score</span>
          </div>
        </div>
      </div>
    </div>
  );
}
