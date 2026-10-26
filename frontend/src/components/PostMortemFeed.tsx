"use client";
import { useState, useEffect } from "react";
import { getPostMortemReports } from "@/lib/api";
import { AlertOctagon, RotateCcw, Wrench, ShieldX, Check } from "lucide-react";

export default function PostMortemFeed() {
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchReports();
  }, []);

  async function fetchReports() {
    try {
      const res = await getPostMortemReports();
      if (res.ok) {
        setReports(await res.json());
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-3xl p-6 md:p-8 shadow-2xl">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest flex items-center gap-2">
            <AlertOctagon size={16} className="text-red-400" />
            <span>Forensic Post-Mortems & Self-Correction</span>
          </h3>
          <p className="text-xs text-gray-500 mt-1">
            Tracking agent accountability, failure root-causes, and automated reliability recalibrations.
          </p>
        </div>
        <span className="text-[10px] bg-red-950/50 text-red-300 font-mono px-2.5 py-1 rounded-full border border-red-500/30">
          Phase 13 Self-Correction
        </span>
      </div>

      {loading ? (
        <div className="h-32 flex items-center justify-center text-gray-500 italic animate-pulse">
          Retrieving post-mortem logs...
        </div>
      ) : reports.length === 0 ? (
        <div className="h-28 flex flex-col items-center justify-center text-gray-500 text-xs text-center border border-dashed border-gray-800 rounded-2xl p-4">
          <RotateCcw size={20} className="text-gray-600 mb-1.5" />
          <span>Zero intervention failures recorded.</span>
          <span className="text-gray-600 text-[11px] mt-0.5">When an intervention is marked ineffective, root-cause forensic post-mortems will populate here.</span>
        </div>
      ) : (
        <div className="space-y-3">
          {reports.map((report) => (
            <div
              key={report.id}
              className="bg-[#0B0F1A] border border-gray-800/90 rounded-2xl p-4 text-xs space-y-2 hover:border-red-500/30 transition-all"
            >
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono text-gray-500">Case #{report.id}</span>
                  <span className="text-gray-200 font-medium font-mono text-[11px]">
                    Failed: "{report.failed_action}"
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-red-950/60 text-red-300 border border-red-500/30">
                    Culpable: {report.responsible_agent} (-{int(report.penalty_applied * 100)}%)
                  </span>
                </div>
              </div>

              <div className="text-gray-400 text-[11px] leading-relaxed">
                <strong className="text-gray-300">Root Cause: </strong>
                {report.root_cause}
              </div>

              <div className="p-2.5 rounded-xl bg-gray-900/60 border border-gray-800 text-[11px] text-purple-300 flex items-start gap-1.5">
                <Wrench size={13} className="text-purple-400 shrink-0 mt-0.5" />
                <span>
                  <strong className="text-gray-300">Corrective Adaptation: </strong>
                  {report.corrective_adaptation}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function int(val: number) {
  return Math.round(val);
}
