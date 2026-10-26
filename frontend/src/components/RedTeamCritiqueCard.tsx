"use client";
import { ShieldCheck, ShieldAlert, AlertTriangle, CheckCircle2, Flame, UserX } from "lucide-react";

interface RedTeamAudit {
  critique_score: number;
  safety_tier: "Safe" | "Guarded" | "Vetoed" | string;
  veto_triggered: boolean;
  vulnerabilities: string[];
  counter_critique?: string;
  suggested_amendment?: string;
}

interface RedTeamProps {
  audit?: RedTeamAudit;
}

export default function RedTeamCritiqueCard({ audit }: RedTeamProps) {
  if (!audit) return null;

  const isVetoed = audit.veto_triggered || audit.safety_tier === "Vetoed";
  const isGuarded = audit.safety_tier === "Guarded";
  const isSafe = audit.safety_tier === "Safe";

  return (
    <div className={`border rounded-2xl p-5 transition-all ${
      isVetoed
        ? "bg-red-950/20 border-red-500/50 shadow-red-950/20 shadow-xl"
        : isGuarded
        ? "bg-amber-950/15 border-amber-500/40"
        : "bg-emerald-950/15 border-emerald-500/30"
    }`}>
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-2 mb-3">
        <div className="flex items-center space-x-2.5">
          <div className={`p-2 rounded-xl border ${
            isVetoed
              ? "bg-red-500/20 border-red-500/40 text-red-400"
              : isGuarded
              ? "bg-amber-500/20 border-amber-500/40 text-amber-400"
              : "bg-emerald-500/20 border-emerald-500/40 text-emerald-400"
          }`}>
            {isVetoed ? <ShieldAlert size={16} /> : isGuarded ? <AlertTriangle size={16} /> : <ShieldCheck size={16} />}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h4 className="text-xs font-bold text-gray-200 uppercase tracking-widest">
                Adversarial Red-Team Audit
              </h4>
              <span className={`text-[10px] uppercase font-mono px-2 py-0.2 rounded border ${
                isVetoed
                  ? "bg-red-900/60 text-red-300 border-red-500/50"
                  : isGuarded
                  ? "bg-amber-900/60 text-amber-300 border-amber-500/40"
                  : "bg-emerald-900/60 text-emerald-300 border-emerald-500/40"
              }`}>
                {isVetoed ? "VETO APPLIED" : audit.safety_tier}
              </span>
            </div>
            <span className="text-[11px] text-gray-500">
              Probing consensus for sycophancy, toxic positivity, and friction traps.
            </span>
          </div>
        </div>

        <div className="text-right">
          <span className="text-[10px] text-gray-500 uppercase tracking-widest block">Critique Risk Index</span>
          <span className={`font-mono text-sm font-bold ${
            isVetoed ? "text-red-400" : isGuarded ? "text-amber-400" : "text-emerald-400"
          }`}>
            {(audit.critique_score * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      {/* Counter Critique / Explanations */}
      {audit.counter_critique && (
        <div className="mt-3 p-3 bg-[#0B0F1A] rounded-xl border border-gray-800 text-xs text-gray-300 leading-relaxed">
          <span className="text-purple-400 font-semibold block mb-0.5">Adversarial Finding:</span>
          {audit.counter_critique}
        </div>
      )}

      {/* Suggested Amendment (if veto triggered) */}
      {isVetoed && audit.suggested_amendment && (
        <div className="mt-3 p-3 bg-red-950/30 rounded-xl border border-red-500/30 text-xs space-y-1">
          <span className="text-red-300 font-semibold flex items-center gap-1.5">
            <CheckCircle2 size={13} className="text-red-400" />
            Mandatory Paced Amendment Enforced:
          </span>
          <p className="text-gray-300 text-[11px] leading-relaxed">
            {audit.suggested_amendment}
          </p>
        </div>
      )}

      {/* Vulnerabilities Checklist */}
      {audit.vulnerabilities && audit.vulnerabilities.length > 0 && (
        <div className="mt-3 pt-2 border-t border-gray-800/80">
          <span className="text-[10px] text-gray-500 uppercase tracking-widest block mb-1">
            Vulnerabilities Flagged ({audit.vulnerabilities.length})
          </span>
          <ul className="space-y-1">
            {audit.vulnerabilities.map((v, i) => (
              <li key={i} className="text-[11px] text-amber-300/90 font-mono flex items-start gap-1.5">
                <span className="text-amber-500">⚠</span>
                <span>{v}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
