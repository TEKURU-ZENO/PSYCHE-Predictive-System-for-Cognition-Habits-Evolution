"use client";
import { useState } from "react";
import { acknowledgeAlert } from "@/lib/api";
import { Sun, Moon, Clock, ShieldAlert, Sparkles, Check, BellRing } from "lucide-react";

interface AmbientMonitorProps {
  ambientData?: {
    status: string;
    circadian_phase: string;
    circadian_info?: {
      title: string;
      description: string;
      mode: string;
    };
    active_alerts: Array<{
      id: number;
      type: string;
      severity: string;
      title: string;
      message: string;
      preemptive_action?: string;
      circadian_phase?: string;
    }>;
  };
}

export default function AmbientMonitorBanner({ ambientData }: AmbientMonitorProps) {
  const [alerts, setAlerts] = useState<any[]>(ambientData?.active_alerts || []);
  const [dismissed, setDismissed] = useState<Record<number, boolean>>({});

  if (!ambientData) return null;

  const { circadian_phase, circadian_info } = ambientData;

  const handleDismiss = async (alertId: number) => {
    setDismissed((prev) => ({ ...prev, [alertId]: true }));
    try {
      await acknowledgeAlert(alertId);
    } catch (e) {
      console.error(e);
    }
  };

  const isNight = circadian_phase === "late_night_vulnerability";
  const isAfternoon = circadian_phase === "afternoon_dip";

  const visibleAlerts = alerts.filter((a) => !dismissed[a.id]);

  return (
    <div className="w-full space-y-3 mb-8">
      {/* Ambient Status Pill */}
      <div className="bg-[#111827]/90 border border-gray-800 rounded-2xl p-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-3 backdrop-blur-md shadow-xl">
        <div className="flex items-center space-x-3">
          <div className={`p-2.5 rounded-xl border ${
            isNight ? "bg-indigo-950/50 border-indigo-500/40 text-indigo-400" :
            isAfternoon ? "bg-amber-950/50 border-amber-500/40 text-amber-400" :
            "bg-purple-950/50 border-purple-500/40 text-purple-400"
          }`}>
            {isNight ? <Moon size={18} /> : isAfternoon ? <Clock size={18} /> : <Sun size={18} />}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-gray-200">
                {circadian_info?.title || "Circadian Rhythm Active"}
              </span>
              <span className="text-[10px] bg-purple-900/30 text-purple-300 font-mono px-2 py-0.5 rounded-full border border-purple-500/20">
                Phase 12 Proactive Monitor
              </span>
            </div>
            <p className="text-[11px] text-gray-400 mt-0.5">
              {circadian_info?.description || "Ambient background monitor tracking stress velocity and circadian friction curves."}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3 text-xs">
          <div className="flex items-center space-x-1.5 text-gray-400 bg-gray-900/60 px-3 py-1.5 rounded-xl border border-gray-800">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-[11px] font-mono text-gray-300">Ambient Daemon: Active</span>
          </div>
        </div>
      </div>

      {/* Active Proactive Alerts */}
      {visibleAlerts.map((alert) => {
        const isCritical = alert.severity === "critical";
        return (
          <div
            key={alert.id}
            className={`border rounded-2xl p-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-3 transition-all animate-in fade-in duration-300 ${
              isCritical
                ? "bg-gradient-to-r from-red-950/70 to-orange-950/60 border-red-500/40 shadow-red-950/20 shadow-xl"
                : "bg-gradient-to-r from-indigo-950/60 to-purple-950/50 border-indigo-500/30 shadow-xl"
            }`}
          >
            <div className="flex items-start space-x-3">
              <div className={`p-2 rounded-xl mt-0.5 ${isCritical ? "bg-red-500/20 text-red-400" : "bg-indigo-500/20 text-indigo-400"}`}>
                <ShieldAlert size={18} />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="text-xs font-bold text-gray-100 uppercase tracking-wide">
                    {alert.title}
                  </h4>
                  <span className={`text-[10px] uppercase font-mono px-1.5 py-0.2 rounded border ${
                    isCritical ? "bg-red-900/40 text-red-300 border-red-500/40" : "bg-indigo-900/40 text-indigo-300 border-indigo-500/30"
                  }`}>
                    {alert.severity}
                  </span>
                </div>
                <p className="text-xs text-gray-300 mt-1 max-w-3xl leading-relaxed">
                  {alert.message}
                </p>
                {alert.preemptive_action && (
                  <div className="mt-2 text-[11px] text-purple-300 flex items-center gap-1.5">
                    <Sparkles size={12} className="text-purple-400" />
                    <span>Recommended Safeguard: <strong className="font-mono text-gray-200">{alert.preemptive_action.replace(/_/g, " ").toUpperCase()}</strong></span>
                  </div>
                )}
              </div>
            </div>

            <button
              onClick={() => handleDismiss(alert.id)}
              className="text-xs px-3 py-1.5 bg-gray-900/60 hover:bg-gray-800 text-gray-300 hover:text-white rounded-xl border border-gray-700/50 transition flex items-center space-x-1 shrink-0 self-end md:self-center"
            >
              <Check size={12} />
              <span>Acknowledge</span>
            </button>
          </div>
        );
      })}
    </div>
  );
}
