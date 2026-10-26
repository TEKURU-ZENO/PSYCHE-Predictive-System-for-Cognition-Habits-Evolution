"use client";
import { Compass, Sparkles, UserCheck } from "lucide-react";

interface ArchetypeDriftChartProps {
  distribution?: Record<string, number>;
  dominant?: string;
  secondary?: string;
}

const archetypeDescriptions: Record<string, string> = {
  Wizard: "Analytical, deep-thinking, seeking insight & cognitive mastery.",
  Warrior: "Goal-driven, disciplined, thrives under challenges & execution.",
  Explorer: "Curious, novelty-seeking, values autonomy & discovery.",
  Creator: "Expressive, systems-builder, translating vision to reality.",
  Caregiver: "Supportive, empathetic, values connection & community.",
  Rebel: "Unconventional, disrupts stagnation, challenges orthodoxy.",
  Everyman: "Pragmatic, grounded, seeks balance & authentic stability."
};

export default function ArchetypeDriftChart({
  distribution = {
    Wizard: 0.28,
    Warrior: 0.22,
    Explorer: 0.18,
    Creator: 0.15,
    Caregiver: 0.08,
    Rebel: 0.05,
    Everyman: 0.04
  },
  dominant = "Wizard",
  secondary = "Warrior"
}: ArchetypeDriftChartProps) {
  const sorted = Object.entries(distribution).sort((a, b) => b[1] - a[1]);

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-3xl p-6 md:p-8 shadow-2xl">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest flex items-center gap-2">
            <Compass size={16} className="text-purple-400" />
            <span>Cognitive Archetype Distribution</span>
          </h3>
          <p className="text-xs text-gray-500 mt-1">
            Tracking longitudinal shifts in your psychological operating mode.
          </p>
        </div>
        <div className="flex space-x-2">
          <span className="text-xs bg-purple-900/40 border border-purple-500/40 text-purple-300 px-3 py-1 rounded-xl font-medium flex items-center gap-1">
            <Sparkles size={12} /> Dominant: {dominant}
          </span>
          {secondary && (
            <span className="text-xs bg-indigo-900/30 border border-indigo-500/30 text-indigo-300 px-3 py-1 rounded-xl font-medium">
              Secondary: {secondary}
            </span>
          )}
        </div>
      </div>

      <div className="space-y-3.5">
        {sorted.map(([name, weight]) => {
          const pct = Math.round(weight * 100);
          const isDominant = name === dominant;
          return (
            <div key={name} className="space-y-1">
              <div className="flex justify-between text-xs items-center">
                <span className={`font-medium ${isDominant ? "text-purple-300" : "text-gray-300"}`}>
                  {name}
                  {isDominant && <span className="ml-2 text-[10px] text-purple-400 font-mono">(Dominant)</span>}
                </span>
                <span className="text-gray-400 font-mono text-[11px]">{pct}%</span>
              </div>
              <div className="w-full h-2 bg-[#0B0F1A] rounded-full overflow-hidden border border-gray-800/80">
                <div
                  className={`h-full rounded-full transition-all duration-700 ${
                    isDominant
                      ? "bg-gradient-to-r from-purple-500 to-indigo-500 shadow-[0_0_8px_rgba(168,85,247,0.4)]"
                      : "bg-gray-700"
                  }`}
                  style={{ width: `${Math.max(4, pct)}%` }}
                ></div>
              </div>
              <p className="text-[10px] text-gray-500 italic">
                {archetypeDescriptions[name] || ""}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
