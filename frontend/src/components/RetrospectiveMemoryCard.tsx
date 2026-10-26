"use client";
import { useState } from "react";
import { queryRetrospective, triggerConsolidation } from "@/lib/api";
import { Brain, Sparkles, History, CheckCircle2, AlertCircle, RefreshCw, Layers } from "lucide-react";

interface RetrospectiveMemoryProps {
  initialSchemas?: any[];
}

export default function RetrospectiveMemoryCard({ initialSchemas = [] }: RetrospectiveMemoryProps) {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [consolidating, setConsolidating] = useState(false);
  const [retroData, setRetroData] = useState<any>(null);
  const [schemas, setSchemas] = useState<any[]>(initialSchemas);

  const handleQuery = async () => {
    if (!question.trim()) return;
    setLoading(true);
    try {
      const res = await queryRetrospective(question);
      if (res.ok) {
        const data = await res.json();
        setRetroData(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleConsolidate = async () => {
    setConsolidating(true);
    try {
      const res = await triggerConsolidation();
      if (res.ok) {
        const data = await res.json();
        if (data.schemas) setSchemas(data.schemas);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setConsolidating(false);
    }
  };

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-3xl p-6 md:p-8 shadow-2xl relative overflow-hidden">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400">
            <Brain size={20} />
          </div>
          <div>
            <h3 className="text-base font-semibold text-gray-100 flex items-center gap-2">
              <span>Autobiographical Memory Engine</span>
              <span className="text-[10px] bg-purple-900/40 text-purple-300 px-2 py-0.5 rounded-full border border-purple-500/30 font-mono">
                Phase 11
              </span>
            </h3>
            <p className="text-xs text-gray-500 mt-0.5">
              Associative memory recall across past psychological episodes and consolidated mental models.
            </p>
          </div>
        </div>

        <button
          onClick={handleConsolidate}
          disabled={consolidating}
          className="flex items-center space-x-2 text-xs bg-gray-900 hover:bg-gray-850 text-gray-400 hover:text-purple-300 px-3 py-1.5 rounded-xl border border-gray-800 transition disabled:opacity-50"
          title="Consolidate past episodes into high-order schemas"
        >
          <RefreshCw size={12} className={consolidating ? "animate-spin text-purple-400" : ""} />
          <span>{consolidating ? "Consolidating..." : "Consolidate Schemas"}</span>
        </button>
      </div>

      {/* Retrospective Search Input */}
      <div className="space-y-3 mb-6">
        <div className="relative">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleQuery()}
            placeholder="Ask your memory: 'When did I feel like this before and what worked?'"
            className="w-full bg-[#0B0F1A] border border-gray-800 focus:border-purple-500/60 rounded-xl px-4 py-3 text-sm text-gray-200 placeholder-gray-600 focus:outline-none transition pr-28"
          />
          <button
            onClick={handleQuery}
            disabled={loading || !question.trim()}
            className="absolute right-2 top-2 bottom-2 px-4 bg-purple-600 hover:bg-purple-500 disabled:opacity-40 text-white rounded-lg text-xs font-medium transition flex items-center space-x-1.5"
          >
            {loading ? (
              <span className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            ) : (
              <>
                <Sparkles size={12} />
                <span>Recall</span>
              </>
            )}
          </button>
        </div>

        {/* Quick query presets */}
        <div className="flex flex-wrap gap-2 text-[11px] text-gray-500">
          <span>Presets:</span>
          <button
            onClick={() => { setQuestion("coding under tight deadline stress"); }}
            className="hover:text-purple-400 underline decoration-dotted"
          >
            Coding deadline stress
          </button>
          <span>•</span>
          <button
            onClick={() => { setQuestion("social fatigue after back-to-back meetings"); }}
            className="hover:text-purple-400 underline decoration-dotted"
          >
            Meeting fatigue
          </button>
          <span>•</span>
          <button
            onClick={() => { setQuestion("overwhelmed by unclear goals and self-doubt"); }}
            className="hover:text-purple-400 underline decoration-dotted"
          >
            Unclear goals & doubt
          </button>
        </div>
      </div>

      {/* Retrospective Response Section */}
      {retroData && (
        <div className="mb-6 bg-[#0B0F1A] border border-purple-500/30 rounded-2xl p-5 relative overflow-hidden animate-in fade-in duration-300">
          <div className="flex justify-between items-start mb-3">
            <span className="text-xs font-semibold text-purple-400 uppercase tracking-wider flex items-center gap-1.5">
              <History size={14} /> Grounded Memory Synthesis
            </span>
            <span className="text-[10px] font-mono text-purple-300 bg-purple-950/60 px-2 py-0.5 rounded border border-purple-500/30">
              Confidence: {(retroData.confidence * 100).toFixed(0)}%
            </span>
          </div>

          <p className="text-sm text-gray-300 leading-relaxed mb-4">
            {retroData.answer}
          </p>

          {/* Matched Precedent Episodes */}
          {retroData.matched_episodes && retroData.matched_episodes.length > 0 && (
            <div className="space-y-2 border-t border-gray-800/80 pt-3">
              <span className="text-[10px] text-gray-500 uppercase tracking-widest font-semibold block mb-1">
                Autobiographical Evidence Episodes
              </span>
              <div className="grid md:grid-cols-2 gap-2">
                {retroData.matched_episodes.map((ep: any, idx: number) => (
                  <div key={idx} className="bg-[#111827] border border-gray-800 p-3 rounded-xl text-xs space-y-1">
                    <div className="flex justify-between items-center text-[10px]">
                      <span className="text-purple-300 font-mono">Episode #{ep.id} ({ep.trigger_context})</span>
                      <span className={`px-1.5 py-0.2 rounded font-mono ${ep.outcome_delta > 0 ? "text-emerald-400 bg-emerald-950/50" : "text-red-400 bg-red-950/50"}`}>
                        {ep.outcome_delta > 0 ? `+${(ep.outcome_delta * 100).toFixed(0)}%` : `${(ep.outcome_delta * 100).toFixed(0)}%`}
                      </span>
                    </div>
                    <p className="text-gray-400 text-[11px] line-clamp-2 italic">"{ep.scenario}"</p>
                    <div className="text-[10px] text-gray-500 pt-1 flex items-center justify-between">
                      <span>Applied: <strong className="text-gray-300">{ep.intervention_applied}</strong></span>
                      <span className="text-gray-600 font-mono">Sim: {(ep.similarity * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Consolidated Schemas */}
      {schemas && schemas.length > 0 && (
        <div className="border-t border-gray-800/80 pt-4">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider flex items-center gap-1.5">
              <Layers size={13} className="text-purple-400" /> Consolidated Psychological Schemas
            </span>
            <span className="text-[10px] text-gray-500">{schemas.length} patterns distilled</span>
          </div>
          <div className="grid md:grid-cols-2 gap-3">
            {schemas.slice(0, 4).map((s: any, idx: number) => (
              <div key={idx} className="bg-[#0B0F1A]/80 border border-gray-800/90 hover:border-purple-500/40 transition rounded-xl p-3.5">
                <div className="flex justify-between items-center text-xs mb-1.5">
                  <span className="font-medium text-purple-300">{s.theme}</span>
                  {s.confidence && (
                    <span className="text-[10px] font-mono text-gray-500">{(s.confidence * 100).toFixed(0)}% Conf</span>
                  )}
                </div>
                <p className="text-xs text-gray-400 leading-relaxed">
                  {s.consolidated_insight || s.insight}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
