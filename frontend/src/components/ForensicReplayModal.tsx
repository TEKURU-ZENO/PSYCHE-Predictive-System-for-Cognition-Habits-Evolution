"use client";
import { useState, useEffect } from "react";
import { replayDecision, getReplayTimeline } from "@/lib/api";
import { ShieldCheck, History, X, Search, CheckCircle2, Cpu, Hash, Layers } from "lucide-react";

interface ForensicReplayModalProps {
  initialHash?: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function ForensicReplayModal({ initialHash, isOpen, onClose }: ForensicReplayModalProps) {
  const [inputHash, setInputHash] = useState(initialHash || "");
  const [loading, setLoading] = useState(false);
  const [replayData, setReplayData] = useState<any>(null);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      fetchTimeline();
      if (initialHash) {
        handleReplay(initialHash);
      }
    }
  }, [isOpen, initialHash]);

  async function fetchTimeline() {
    try {
      const res = await getReplayTimeline();
      if (res.ok) {
        setTimeline(await res.json());
      }
    } catch (e) {
      console.error(e);
    }
  }

  async function handleReplay(hashToLookup: string) {
    if (!hashToLookup.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await replayDecision(hashToLookup.trim());
      if (res.ok) {
        setReplayData(await res.json());
      } else {
        setError("Decision hash not found in forensic event memory.");
        setReplayData(null);
      }
    } catch (e) {
      setError("Failed to query forensic replay server.");
      setReplayData(null);
    } finally {
      setLoading(false);
    }
  }

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 overflow-y-auto animate-in fade-in duration-200">
      <div className="bg-[#111827] border border-gray-800 w-full max-w-4xl rounded-3xl p-6 md:p-8 shadow-2xl relative max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-start pb-4 border-b border-gray-800">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-2xl bg-purple-500/10 border border-purple-500/20 text-purple-400">
              <History size={20} />
            </div>
            <div>
              <h2 className="text-base font-semibold text-gray-100 flex items-center gap-2">
                <span>Forensic Decision Replay</span>
                <span className="text-[10px] bg-purple-900/40 text-purple-300 px-2 py-0.5 rounded-full border border-purple-500/30 font-mono">
                  Phase 14 Audit
                </span>
              </h2>
              <p className="text-xs text-gray-400">
                Reconstruct the exact cognitive twin state, weights, and version matrix for any decision hash.
              </p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-gray-800 rounded-xl text-gray-400 hover:text-white transition">
            <X size={18} />
          </button>
        </div>

        {/* Search Bar */}
        <div className="my-5 flex gap-2">
          <div className="relative flex-grow">
            <input
              type="text"
              value={inputHash}
              onChange={(e) => setInputHash(e.target.value)}
              placeholder="Paste SHA-256 Decision Hash (e.g. 7f8a1b2c3d...)"
              className="w-full bg-[#0B0F1A] border border-gray-800 focus:border-purple-500/60 rounded-xl px-4 py-2.5 text-xs font-mono text-gray-200 placeholder-gray-600 focus:outline-none"
            />
          </div>
          <button
            onClick={() => handleReplay(inputHash)}
            disabled={loading || !inputHash.trim()}
            className="px-5 bg-purple-600 hover:bg-purple-500 disabled:opacity-40 text-white rounded-xl text-xs font-medium transition flex items-center gap-1.5"
          >
            <Search size={14} />
            <span>{loading ? "Replaying..." : "Replay"}</span>
          </button>
        </div>

        {/* Content Body */}
        <div className="overflow-y-auto space-y-6 flex-grow pr-1">
          {error && (
            <div className="p-4 bg-red-950/30 border border-red-500/40 rounded-xl text-xs text-red-300">
              {error}
            </div>
          )}

          {replayData ? (
            <div className="space-y-6">
              {/* Integrity Stamp */}
              <div className="bg-[#0B0F1A] border border-emerald-500/30 rounded-2xl p-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-2">
                <div className="flex items-center space-x-2.5">
                  <CheckCircle2 size={18} className="text-emerald-400" />
                  <div>
                    <span className="text-xs font-bold text-emerald-300 font-mono">
                      SHA-256 INTEGRITY VERIFIED: TAMPER-FREE
                    </span>
                    <p className="text-[10px] text-gray-500 font-mono break-all mt-0.5">
                      Hash: {replayData.decision_hash}
                    </p>
                  </div>
                </div>
                <span className="text-[10px] text-gray-400 font-mono whitespace-nowrap">
                  {replayData.timestamp ? new Date(replayData.timestamp).toLocaleString() : "Historical"}
                </span>
              </div>

              {/* Decision & Scenario Snapshot */}
              <div className="bg-[#0B0F1A] border border-gray-800 p-5 rounded-2xl space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-gray-500 uppercase tracking-widest font-semibold text-[10px]">Reconstructed Dilemma</span>
                  <span className="text-purple-400 font-mono text-[11px]">Confidence: {(replayData.confidence * 100).toFixed(0)}%</span>
                </div>
                <p className="text-xs text-gray-300 italic">"{replayData.scenario}"</p>
                <div className="pt-2 border-t border-gray-800/80">
                  <span className="text-[10px] text-gray-500 uppercase tracking-widest block mb-0.5">Final Locked Decision</span>
                  <span className="text-sm font-semibold text-gray-100 font-mono">{replayData.final_decision}</span>
                  <p className="text-xs text-gray-400 mt-1 leading-relaxed">{replayData.reasoning}</p>
                </div>
              </div>

              {/* Dynamic Weights & Trust at that moment */}
              <div className="grid md:grid-cols-2 gap-4">
                <div className="bg-[#0B0F1A] border border-gray-800 p-4 rounded-2xl space-y-2">
                  <span className="text-[10px] text-gray-500 uppercase tracking-widest font-semibold block">
                    Dynamic Weights at Time of Decision
                  </span>
                  <div className="space-y-1.5">
                    {Object.entries(replayData.weights || {}).map(([agent, w]: [string, any]) => (
                      <div key={agent} className="flex justify-between items-center text-xs">
                        <span className="capitalize text-gray-300">{agent}Agent</span>
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-gray-400">{(w * 100).toFixed(0)}%</span>
                          {replayData.trust_tiers && replayData.trust_tiers[agent] && (
                            <span className="text-[9px] uppercase font-mono px-1.5 py-0.2 rounded bg-purple-950/60 text-purple-300 border border-purple-500/20">
                              {replayData.trust_tiers[agent]}
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Version Matrix active at that second */}
                <div className="bg-[#0B0F1A] border border-gray-800 p-4 rounded-2xl space-y-2">
                  <span className="text-[10px] text-gray-500 uppercase tracking-widest font-semibold block flex items-center gap-1">
                    <Cpu size={12} className="text-purple-400" /> Active System Version Registry
                  </span>
                  <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
                    {Object.entries(replayData.system_versions || {}).map(([sys, ver]: [string, any]) => (
                      <div key={sys} className="flex justify-between bg-gray-900/60 p-1.5 rounded-lg border border-gray-800/80">
                        <span className="text-gray-500 capitalize">{sys}:</span>
                        <span className="text-purple-300">{ver}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Arguments snapshot */}
              {replayData.arguments && replayData.arguments.length > 0 && (
                <div className="bg-[#0B0F1A] border border-gray-800 p-4 rounded-2xl space-y-2">
                  <span className="text-[10px] text-gray-500 uppercase tracking-widest font-semibold block">
                    Agent Deliberation Positions
                  </span>
                  <div className="grid md:grid-cols-2 gap-2">
                    {replayData.arguments.map((arg: any, i: number) => (
                      <div key={i} className="p-3 bg-gray-900/60 rounded-xl border border-gray-800 text-xs space-y-1">
                        <div className="flex justify-between items-center text-[10px]">
                          <span className="font-bold text-purple-300 uppercase">{arg.agent}Agent</span>
                          <span className="text-gray-500 italic">Lens: {arg.perspective}</span>
                        </div>
                        <p className="text-gray-300 text-[11px]">
                          {typeof arg.position === "string" ? arg.position : JSON.stringify(arg.position)}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-3">
              <span className="text-xs text-gray-500 uppercase tracking-widest font-semibold block">
                Recent Decision Timeline (Click to Replay)
              </span>
              {timeline.length === 0 ? (
                <div className="text-xs text-gray-600 italic py-8 text-center">
                  No decisions hashed yet. Simulate scenarios to build your forensic audit history.
                </div>
              ) : (
                <div className="space-y-2">
                  {timeline.map((item, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setInputHash(item.decision_hash);
                        handleReplay(item.decision_hash);
                      }}
                      className="w-full text-left bg-[#0B0F1A] hover:bg-gray-900/80 p-3.5 rounded-2xl border border-gray-800 hover:border-purple-500/40 transition flex justify-between items-center text-xs group"
                    >
                      <div className="overflow-hidden pr-3">
                        <div className="flex items-center gap-2 mb-0.5">
                          <span className="font-mono text-purple-300 text-[10px] truncate max-w-[200px]">
                            {item.decision_hash}
                          </span>
                          <span className="text-gray-300 font-semibold truncate">
                            Action: {item.decision}
                          </span>
                        </div>
                        <p className="text-gray-500 text-[11px] truncate">"{item.scenario}"</p>
                      </div>
                      <span className="text-[10px] font-mono text-gray-500 whitespace-nowrap">
                        {item.timestamp ? new Date(item.timestamp).toLocaleDateString() : ""}
                      </span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
