"use client";
import { useState, useEffect } from "react";
import { getAssociativeGraph } from "@/lib/api";
import { GitFork, Network, ArrowRight, ShieldCheck, Zap } from "lucide-react";

export default function AssociativeGraphView() {
  const [graph, setGraph] = useState<any>({ nodes: [], edges: [], total_links: 0 });
  const [filter, setFilter] = useState<string>("all");
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchGraph();
  }, []);

  async function fetchGraph() {
    try {
      const res = await getAssociativeGraph();
      if (res.ok) {
        const data = await res.json();
        setGraph(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  const categoryColors: Record<string, string> = {
    trigger: "text-amber-400 bg-amber-950/40 border-amber-500/30",
    distortion: "text-red-400 bg-red-950/40 border-red-500/30",
    intervention: "text-emerald-400 bg-emerald-950/40 border-emerald-500/30",
    state: "text-blue-400 bg-blue-950/40 border-blue-500/30",
    concept: "text-purple-400 bg-purple-950/40 border-purple-500/30",
  };

  const filteredEdges = graph.edges.filter((e: any) => {
    if (filter === "all") return true;
    return e.relation === filter;
  });

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-3xl p-6 md:p-8 shadow-2xl">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
        <div>
          <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest flex items-center gap-2">
            <Network size={16} className="text-purple-400" />
            <span>Associative Cognitive Graph (Hebbian Network)</span>
          </h3>
          <p className="text-xs text-gray-500 mt-1">
            Visualizing concept co-occurrences, trigger escalations, and validated intervention paths.
          </p>
        </div>

        {/* Filter buttons */}
        <div className="flex space-x-2 text-xs">
          <button
            onClick={() => setFilter("all")}
            className={`px-3 py-1 rounded-lg transition border ${filter === "all" ? "bg-purple-900/40 border-purple-500/50 text-purple-300" : "bg-[#0B0F1A] border-gray-800 text-gray-400"}`}
          >
            All ({graph.edges.length})
          </button>
          <button
            onClick={() => setFilter("mitigated_by")}
            className={`px-3 py-1 rounded-lg transition border ${filter === "mitigated_by" ? "bg-emerald-900/40 border-emerald-500/50 text-emerald-300" : "bg-[#0B0F1A] border-gray-800 text-gray-400"}`}
          >
            Mitigations
          </button>
          <button
            onClick={() => setFilter("triggers")}
            className={`px-3 py-1 rounded-lg transition border ${filter === "triggers" ? "bg-amber-900/40 border-amber-500/50 text-amber-300" : "bg-[#0B0F1A] border-gray-800 text-gray-400"}`}
          >
            Triggers
          </button>
        </div>
      </div>

      {loading ? (
        <div className="h-40 flex items-center justify-center text-gray-500 italic animate-pulse">
          Parsing cognitive graph edges...
        </div>
      ) : graph.edges.length === 0 ? (
        <div className="h-32 flex flex-col items-center justify-center text-gray-500 text-xs text-center border border-dashed border-gray-800 rounded-2xl p-4">
          <GitFork size={24} className="text-gray-600 mb-2" />
          <span>No associative links reinforced yet.</span>
          <span className="text-gray-600 mt-1">As you log scenarios and test interventions in the simulator, Hebbian associations will self-assemble here.</span>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Active Concept Nodes */}
          <div>
            <span className="text-[10px] text-gray-500 uppercase tracking-widest font-semibold block mb-2">
              Active Concept Nodes ({graph.nodes.length})
            </span>
            <div className="flex flex-wrap gap-2">
              {graph.nodes.map((node: any) => {
                const color = categoryColors[node.category] || categoryColors.concept;
                return (
                  <span
                    key={node.id}
                    className={`px-2.5 py-1 rounded-lg text-xs font-medium border ${color} flex items-center gap-1.5`}
                  >
                    <span className="text-[9px] uppercase opacity-75 font-mono">{node.category}:</span>
                    <span>{node.label}</span>
                  </span>
                );
              })}
            </div>
          </div>

          {/* Edge Link Cards */}
          <div className="pt-2">
            <span className="text-[10px] text-gray-500 uppercase tracking-widest font-semibold block mb-2">
              Relational Pathways ({filteredEdges.length})
            </span>
            <div className="grid md:grid-cols-2 gap-2.5">
              {filteredEdges.map((edge: any, idx: number) => {
                const isMitigation = edge.relation === "mitigated_by";
                return (
                  <div
                    key={idx}
                    className="bg-[#0B0F1A] border border-gray-800/80 rounded-xl p-3 flex items-center justify-between text-xs"
                  >
                    <div className="flex items-center space-x-2 flex-grow overflow-hidden pr-2">
                      <span className="text-gray-300 font-mono text-[11px] truncate">
                        {edge.source.replace(/^[^:]+:/, "")}
                      </span>
                      <div className="flex items-center text-[10px] text-purple-400 font-mono px-1.5 py-0.5 rounded bg-purple-950/40 border border-purple-500/20 whitespace-nowrap">
                        <ArrowRight size={10} className="mr-1" />
                        <span>{edge.relation}</span>
                      </div>
                      <span className="text-gray-200 font-mono text-[11px] truncate">
                        {edge.target.replace(/^[^:]+:/, "")}
                      </span>
                    </div>

                    <div className="text-right whitespace-nowrap pl-2">
                      <span className={`font-mono text-xs font-semibold ${isMitigation ? "text-emerald-400" : "text-amber-400"}`}>
                        {(edge.weight * 100).toFixed(0)}%
                      </span>
                      <span className="text-[9px] text-gray-600 block">w-link</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
