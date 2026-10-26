"use client";
import React from "react";
import { ShieldCheck, ShieldAlert, Shield, HelpCircle } from "lucide-react";

interface AgentTrustTableProps {
  weights?: Record<string, number>;
  trustTiers?: Record<string, string>;
  effectiveAccuracies?: Record<string, number>;
}

export default function AgentTrustTable({
  weights = {},
  trustTiers = {},
  effectiveAccuracies = {},
}: AgentTrustTableProps) {
  const agentsList = [
    { id: "prediction", name: "Prediction Agent", desc: "Forecasts user emotional drift" },
    { id: "strategy", name: "Strategy Agent", desc: "Formulates behavioral nudges" },
    { id: "meta", name: "Meta Agent", desc: "Resolves architectural dissonance" },
    { id: "cognition", name: "Cognition Agent", desc: "Maps cognitive load dynamics" },
  ];

  const getTierIcon = (tier: string) => {
    switch (tier?.toLowerCase()) {
      case "trusted":
        return <ShieldCheck className="w-4 h-4 text-emerald-400" />;
      case "stable":
        return <Shield className="w-4 h-4 text-blue-400" />;
      case "uncertain":
        return <HelpCircle className="w-4 h-4 text-amber-400" />;
      case "degraded":
        return <ShieldAlert className="w-4 h-4 text-red-400" />;
      default:
        return <Shield className="w-4 h-4 text-gray-400" />;
    }
  };

  const getTierBadgeClass = (tier: string) => {
    switch (tier?.toLowerCase()) {
      case "trusted":
        return "bg-emerald-950/40 text-emerald-400 border-emerald-500/30";
      case "stable":
        return "bg-blue-950/40 text-blue-400 border-blue-500/30";
      case "uncertain":
        return "bg-amber-950/40 text-amber-400 border-amber-500/30";
      case "degraded":
        return "bg-red-950/40 text-red-400 border-red-500/30";
      default:
        return "bg-gray-800/40 text-gray-400 border-gray-700/30";
    }
  };

  return (
    <div className="backdrop-blur-md bg-gray-900/40 border border-gray-800/60 rounded-2xl p-6 w-full overflow-hidden">
      <div className="flex justify-between items-center mb-6">
        <div>
          <span className="text-[10px] text-gray-500 uppercase tracking-widest block font-medium">Orchestrated Trust Matrix</span>
          <h3 className="text-lg font-light text-gray-100 mt-1">Agent Status & Trust Tiers</h3>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-gray-800/80 text-[10px] uppercase text-gray-500 tracking-wider">
              <th className="pb-3 font-semibold">Agent</th>
              <th className="pb-3 font-semibold text-center">Trust Tier</th>
              <th className="pb-3 font-semibold text-right">Reliability (Weight)</th>
              <th className="pb-3 font-semibold text-right">Effective Accuracy</th>
              <th className="pb-3 font-semibold text-center hidden md:table-cell">Health Trend</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/40">
            {agentsList.map((agent) => {
              const weight = weights[agent.id] ?? 0.25;
              const tier = trustTiers[agent.id] || "Stable";
              const accuracy = effectiveAccuracies[agent.id] ?? 0.85;

              // Generate simple SVG path for static visual sparkline
              const points =
                agent.id === "prediction"
                  ? "0,15 15,10 30,12 45,5"
                  : agent.id === "strategy"
                  ? "0,5 15,12 30,8 45,15"
                  : agent.id === "meta"
                  ? "0,10 15,8 30,12 45,10"
                  : "0,15 15,18 30,10 45,2";

              const trendColor =
                tier.toLowerCase() === "degraded"
                  ? "#ef4444"
                  : tier.toLowerCase() === "uncertain"
                  ? "#f59e0b"
                  : "#10b981";

              return (
                <tr key={agent.id} className="hover:bg-gray-800/20 transition-all group">
                  <td className="py-4">
                    <div className="flex flex-col">
                      <span className="text-xs font-semibold text-gray-200 group-hover:text-purple-400 transition-colors">
                        {agent.name}
                      </span>
                      <span className="text-[10px] text-gray-500 mt-0.5">{agent.desc}</span>
                    </div>
                  </td>
                  <td className="py-4 text-center">
                    <div className={`${getTierBadgeClass(tier)} inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-mono border capitalize font-semibold shadow-sm leading-none`}>
                      {getTierIcon(tier)}
                      {tier}
                    </div>
                  </td>
                  <td className="py-4 text-right font-mono text-xs text-gray-300">
                    {(weight * 100).toFixed(1)}%
                  </td>
                  <td className="py-4 text-right font-mono text-xs text-gray-300">
                    {(accuracy * 100).toFixed(0)}%
                  </td>
                  <td className="py-4 text-center hidden md:table-cell">
                    <div className="flex justify-center">
                      <svg className="w-12 h-6" viewBox="0 0 45 20">
                        <path
                          d={`M ${points}`}
                          fill="none"
                          stroke={trendColor}
                          strokeWidth="2"
                          strokeLinecap="round"
                        />
                      </svg>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
