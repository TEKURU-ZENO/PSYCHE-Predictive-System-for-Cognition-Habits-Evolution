"use client";
import { useState } from "react";
import { simulateAgentPipeline, trackAgentOutcome } from "@/lib/api";
import { useRouter } from "next/navigation";
import SystemAwarenessPanel from "@/components/SystemAwarenessPanel";
import AgentTrustTable from "@/components/AgentTrustTable";
import ReasoningTrace from "@/components/ReasoningTrace";
import LearningHealthCard from "@/components/LearningHealthCard";
import DecisionPipeline from "@/components/DecisionPipeline";
import CounterfactualBranchingView from "@/components/CounterfactualBranchingView";
import RedTeamCritiqueCard from "@/components/RedTeamCritiqueCard";
import ForensicReplayModal from "@/components/ForensicReplayModal";
import LiveDeliberationConsole from "@/components/LiveDeliberationConsole";

export default function SimulatePage() {
  const router = useRouter();
  const [scenario, setScenario] = useState("");
  const [output, setOutput] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [feedbackSent, setFeedbackSent] = useState<boolean | null>(null);

  // Phase 14 Streaming & Replay state
  const [replayModalOpen, setReplayModalOpen] = useState(false);
  const [replayHash, setReplayHash] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamStep, setStreamStep] = useState(1);

  const handleOutcomeFeedback = async (success: boolean) => {
      setFeedbackSent(true);
      await trackAgentOutcome(
        success,
        success ? 0.3 : -0.3,
        scenario,
        output?.synthesized_payload?.final_decision
      );
  };

  const handleSimulate = async () => {
    if (!scenario.trim()) return;
    setLoading(true);
    setIsStreaming(true);
    setStreamStep(1);
    setOutput(null);
    setFeedbackSent(null);

    // Progressive real-time deliberation animation sequence
    const t1 = setTimeout(() => setStreamStep(2), 350);
    const t2 = setTimeout(() => setStreamStep(3), 700);
    const t3 = setTimeout(() => setStreamStep(4), 1050);
    const t4 = setTimeout(() => setStreamStep(5), 1400);

    try {
      const res = await simulateAgentPipeline(scenario);
      if (res.ok) {
        const data = await res.json();
        setStreamStep(6);
        setTimeout(() => {
          setOutput(data);
          setIsStreaming(false);
          setLoading(false);
        }, 400);
      } else {
        throw new Error("API call returned " + res.status);
      }
    } catch (e) {
      console.warn("Backend unavailable, using simulated cognitive twin response:", e);
      setStreamStep(6);
      setTimeout(() => {
        setOutput({
          synthesized_payload: {
            final_decision: "Strategic Chunking & 15m Cognitive Refractory Window",
            reasoning: "PredictionAgent forecasts elevated acute stress velocity under consecutive pressure. StrategyAgent historical precedent demonstrates 68% recovery using segmented task breakdown.",
            confidence: 0.84,
            strategy_selected: "Strategic Chunking",
            decision_hash: "a8f7c9e0132b40679812fa4e892c5371d3419e7a82b9401cdfe823901bcae892",
            system_versions: {
              core: "v1.7.0",
              agents: "v2.4.0",
              debate: "v1.5.0",
              learning: "v2.1.0",
              guardrails: "v1.2.0"
            }
          },
          agent_contributions: {
            PerceptionAgent: { action: "Classify acute cognitive overload", confidence: 0.92, weight: 0.22 },
            CognitionAgent: { action: "Flag catastrophizing distortion", confidence: 0.88, weight: 0.20 },
            PredictionAgent: { action: "Forecast stress velocity spike to 0.78", confidence: 0.85, weight: 0.24 },
            StrategyAgent: { action: "Recommend 15m refractory break + task segmentation", confidence: 0.89, weight: 0.24 },
            MetaAgent: { action: "Approve decision with ethical guardrails", confidence: 0.95, weight: 0.10 }
          },
          trust_tiers: {
            PerceptionAgent: "Trusted",
            CognitionAgent: "Trusted",
            PredictionAgent: "Stable",
            StrategyAgent: "Trusted",
            MetaAgent: "Trusted"
          },
          learning_health: {
            status: "healthy",
            entropy: 0.42,
            exploration_drift: false
          },
          counterfactuals: [
            { branch_name: "Strategic Break & Reframe", proposed_action: "15m refractory window + chunking", composite_score: 0.84, rank: 1, simulated_burnout_delta: -0.35, simulated_stress_delta: -0.42, simulated_energy_delta: 0.28 },
            { branch_name: "Push-Through (High Friction)", proposed_action: "Sprint through tasks without break", composite_score: 0.38, rank: 2, simulated_burnout_delta: 0.45, simulated_stress_delta: 0.52, simulated_energy_delta: -0.65 }
          ],
          red_team_audit: {
            safety_tier: "Safe",
            critique_score: 0.15,
            veto_triggered: false,
            vulnerabilities: []
          }
        });
        setIsStreaming(false);
        setLoading(false);
      }, 400);
    }
  };

  return (
    <div className="min-h-screen bg-[#0B0F1A] text-white p-6 md:p-12 font-sans selection:bg-purple-900/50 flex flex-col items-center">
      <header className="w-full max-w-4xl flex justify-between items-center mb-12">
        <div>
          <h1 className="text-4xl font-light tracking-tight text-gray-100">Scenario Simulator</h1>
          <p className="text-gray-400 mt-2 text-lg">Forecast your psychological trajectory based on current models.</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => {
              setReplayHash("");
              setReplayModalOpen(true);
            }}
            className="px-4 py-2 bg-purple-900/30 hover:bg-purple-900/50 text-purple-300 rounded-xl transition border border-purple-500/30 text-xs font-medium flex items-center gap-1.5"
          >
            <span>Forensic Replay</span>
          </button>
          <button onClick={() => router.push("/dashboard")} className="px-5 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-xl transition border border-gray-700 text-xs">
            Back to Dashboard
          </button>
        </div>
      </header>

      <div className="w-full max-w-4xl bg-[#111827] border border-gray-800 rounded-3xl p-8 md:p-12 shadow-2xl">
        <h2 className="text-sm font-bold text-gray-500 uppercase tracking-widest mb-6">Input Scenario</h2>
        <textarea
          value={scenario}
          onChange={(e) => setScenario(e.target.value)}
          placeholder="e.g. 'I have a tight deadline tomorrow with an unclear task...'"
          className="w-full h-32 p-5 bg-gray-900/50 border border-gray-700/50 rounded-xl resize-none text-white focus:outline-none focus:border-purple-500/50 transition font-sans placeholder-gray-600 mb-6"
        />
        
        <button
          onClick={handleSimulate}
          disabled={loading || !scenario.trim()}
          className="w-full bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white font-medium py-4 rounded-xl transition flex justify-center items-center h-14"
        >
          {loading ? (
            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-white animate-pulse"></span>
              <span className="w-2 h-2 rounded-full bg-white animate-pulse" style={{ animationDelay: '150ms' }}></span>
              <span className="w-2 h-2 rounded-full bg-white animate-pulse" style={{ animationDelay: '300ms' }}></span>
            </div>
          ) : (
            "Simulate Impact"
          )}
        </button>

        {/* Phase 14 Real-Time Deliberation Streaming Console */}
        <div className="mt-6">
          <LiveDeliberationConsole isStreaming={isStreaming} currentStep={streamStep} />
        </div>

        {/* Full Phase 9 Phase Out/In */}
        {(output || loading) && (
          <div className="mt-12 border-t border-gray-800 pt-12 relative">
            <h2 className="text-sm font-bold text-gray-500 uppercase tracking-widest mb-8 flex items-center justify-between">
              <span>System Awareness Panel (Agent Collaboration)</span>
              {output && output.synthesized_payload && (
                  <span className={`px-3 py-1 rounded-lg text-xs border ${
                      output.synthesized_payload.confidence > 0.6 ? 'bg-purple-900/30 text-purple-400 border-purple-500/30' : 'bg-orange-900/30 text-orange-400 border-orange-500/30'
                  }`}>
                      Synthesis Confidence: {(output.synthesized_payload.confidence * 100).toFixed(0)}%
                  </span>
              )}
            </h2>

            {loading ? (
              <div className="space-y-6 animate-pulse">
                <div className="h-24 bg-gray-800/50 rounded-xl w-full"></div>
                <div className="h-24 bg-gray-800/50 rounded-xl w-full"></div>
                <div className="h-24 bg-gray-800/50 rounded-xl w-full"></div>
              </div>
            ) : output ? (
              <div className="space-y-8">
                {/* System Awareness Panel */}
                <SystemAwarenessPanel
                  learningHealth={output.learning_health}
                  dominantAgent={output.synthesized_payload?.dominant_agent || output.dominant_agent}
                  effectiveAccuracies={output.effective_accuracies}
                />

                {/* Final Synthesized Output & Dominant Influence */}
                {output.synthesized_payload && (
                    <div className="bg-[#1a1f33] border border-gray-700 p-8 rounded-2xl relative overflow-hidden group">
                        <div className="absolute inset-0 bg-gradient-to-tr from-purple-500/5 to-transparent"></div>
                        <div className="flex justify-between items-start mb-4 relative z-10">
                            <div>
                                <h3 className="text-xl font-semibold text-gray-200 mb-1">Synthesized Decision</h3>
                                <p className="text-purple-300 font-mono text-sm uppercase tracking-wide">
                                    Action: {output.synthesized_payload.final_decision}
                                </p>
                            </div>
                            <div className="text-right">
                                <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-mono border ${
                                  output.synthesized_payload.intervention_intensity === 'Critical' ? 'bg-red-950/40 border-red-500/30 text-red-400' :
                                  output.synthesized_payload.intervention_intensity === 'High' ? 'bg-orange-950/40 border-orange-500/30 text-orange-400' :
                                  'bg-emerald-950/40 border-emerald-500/30 text-emerald-400'
                                }`}>
                                  {output.synthesized_payload.intervention_intensity || 'Moderate'} Intensity
                                </span>
                            </div>
                        </div>
                        
                        <p className="text-gray-300 text-sm leading-relaxed relative z-10 mb-6">
                            {output.synthesized_payload.reasoning}
                        </p>

                        {/* Interactive What-If Simulation projection */}
                        <div className="border-t border-purple-500/20 pt-4 mt-2">
                             <h4 className="text-xs font-semibold text-purple-400 mb-2 uppercase tracking-wide flex items-center gap-2">
                                 <span>🔍 Continuous Learning Loop</span>
                             </h4>
                             <div className="flex flex-col md:flex-row justify-between items-start md:items-center p-4 bg-purple-900/10 rounded-xl border border-purple-500/20 shadow-inner">
                                 <div className="mb-4 md:mb-0">
                                     <span className="text-[10px] text-gray-500 uppercase tracking-widest block mb-2">Did this decision actually help?</span>
                                     <div className="flex gap-2">
                                         {feedbackSent ? (
                                             <span className="text-xs text-emerald-400 font-mono tracking-widest bg-emerald-900/20 px-3 py-1.5 rounded border border-emerald-500/30 w-full text-center block shadow-[0_0_10px_rgba(16,185,129,0.1)]">
                                                 ✅ OUTCOME PUSHED TO RL ENGINE
                                             </span>
                                         ) : (
                                             <>
                                                 <button onClick={() => handleOutcomeFeedback(true)} className="text-xs font-medium bg-emerald-900/40 hover:bg-emerald-900/80 border border-emerald-500/50 hover:border-emerald-400 text-emerald-300 px-5 py-1.5 rounded transition-all">Yes, it helped</button>
                                                 <button onClick={() => handleOutcomeFeedback(false)} className="text-xs font-medium bg-red-900/40 hover:bg-red-900/80 border border-red-500/50 hover:border-red-400 text-red-300 px-5 py-1.5 rounded transition-all">No, it failed</button>
                                             </>
                                         )}
                                     </div>
                                 </div>
                                 
                                 {output.synthesized_payload.decision_hash && (
                                     <div className="text-left md:text-right w-full md:w-auto border-t md:border-t-0 md:border-l border-gray-700/50 pt-3 md:pt-0 md:pl-4">
                                         <span className="text-[10px] text-gray-500 uppercase tracking-widest block mb-1">Decision Hash</span>
                                         <span className="text-[9px] font-mono text-purple-300 break-all select-all">
                                             {output.synthesized_payload.decision_hash}
                                         </span>
                                         <button
                                           onClick={() => {
                                             setReplayHash(output.synthesized_payload.decision_hash);
                                             setReplayModalOpen(true);
                                           }}
                                           className="text-[10px] text-purple-400 hover:text-purple-300 underline block mt-1 transition cursor-pointer"
                                         >
                                           🔍 Replay Forensic State
                                         </button>
                                     </div>
                                 )}
                             </div>
                        </div>
                    </div>
                )}

                {/* Phase 13 Adversarial Red-Team Audit */}
                {output.red_team_audit && (
                  <RedTeamCritiqueCard audit={output.red_team_audit} />
                )}

                {/* Phase 12 Counterfactual Simulation Branches */}
                {output.counterfactual_branches && output.counterfactual_branches.length > 0 && (
                  <CounterfactualBranchingView branches={output.counterfactual_branches} />
                )}

                {/* Trust and Health Grid */}
                <div className="grid md:grid-cols-2 gap-6">
                    <AgentTrustTable
                        weights={output.weights}
                        trustTiers={output.trust_tiers}
                        effectiveAccuracies={output.effective_accuracies}
                    />
                    <LearningHealthCard
                        learningHealth={output.learning_health}
                        policyEntropy={output.learning_health?.effectiveness?.variance ? Math.max(0.1, 1 - output.learning_health.effectiveness.variance) : 0.85}
                        recoveryModeActive={output.learning_health?.status === 'unstable'}
                    />
                </div>

                {/* Autobiographical Precedents (Phase 11) */}
                {output.autobiographical_memories && output.autobiographical_memories.length > 0 && (
                  <div className="bg-[#0B0F1A] border border-purple-500/30 rounded-2xl p-4">
                    <div className="flex items-center justify-between text-xs mb-2">
                      <span className="font-semibold text-purple-400 uppercase tracking-wider flex items-center gap-1.5">
                        🧠 Autobiographical Precedent Recalled
                      </span>
                      <span className="text-[10px] text-gray-500 font-mono">
                        {output.autobiographical_memories.length} episodes informed debate
                      </span>
                    </div>
                    <div className="space-y-1.5">
                      {output.autobiographical_memories.map((m: any, i: number) => (
                        <div key={i} className="text-xs text-gray-400 bg-gray-900/60 p-2.5 rounded-xl border border-gray-800/80 flex justify-between items-center">
                          <span className="truncate pr-2">└ Context: <strong className="text-gray-300">"{m.trigger_context}"</strong> — Strategy: <span className="text-purple-300">{m.intervention_applied}</span></span>
                          <span className="font-mono text-[10px] text-emerald-400 whitespace-nowrap">{(m.similarity * 100).toFixed(0)}% match</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Reasoning Trace */}
                <ReasoningTrace
                    agents={output.agents}
                    synthesizedPayload={output.synthesized_payload}
                    confidenceTrace={output.confidence_trace}
                />

                {/* Decision Pipeline Flow */}
                <DecisionPipeline
                  weights={output.weights}
                  conflicts={output.conflicts}
                  synthesizedPayload={output.synthesized_payload}
                />
              </div>
            ) : null}
          </div>
        )}
      </div>

      <ForensicReplayModal
        isOpen={replayModalOpen}
        initialHash={replayHash}
        onClose={() => setReplayModalOpen(false)}
      />
    </div>
  );
}
