"use client";
import { useState, useEffect, useRef } from "react";
import StateOrb from "@/components/StateOrb";
import MoodChart from "@/components/MoodChart";
import NudgeCard from "@/components/NudgeCard";
import SystemAwarenessPanel from "@/components/SystemAwarenessPanel";
import LearningHealthCard from "@/components/LearningHealthCard";
import RetrospectiveMemoryCard from "@/components/RetrospectiveMemoryCard";
import AmbientMonitorBanner from "@/components/AmbientMonitorBanner";
import PrivacyVaultModal from "@/components/PrivacyVaultModal";
import { Lock } from "lucide-react";
import { logMood, getCurrentState, logBehavior, analyzeText, getRisk, getPlaybook, getMetaProfile, getTelemetry, getConsolidatedSchemas, getAmbientStatus } from "@/lib/api";
import { useRouter } from "next/navigation";

export default function Dashboard() {
  const router = useRouter();
  const [state, setState] = useState<any>({ emotion: "neutral" });
  const [nudge, setNudge] = useState<any>(null);
  const [chartData, setChartData] = useState<any[]>([]);
  
  const [journalText, setJournalText] = useState("");
  const [biases, setBiases] = useState<any[]>([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [riskAlert, setRiskAlert] = useState<any>(null);
  const [playbook, setPlaybook] = useState<any[]>([]);
  const [metaProfile, setMetaProfile] = useState<any>(null);
  const [telemetry, setTelemetry] = useState<any>(null);
  const [schemas, setSchemas] = useState<any[]>([]);
  const [ambientData, setAmbientData] = useState<any>(null);
  const [vaultOpen, setVaultOpen] = useState(false);

  useEffect(() => {
    if (!localStorage.getItem("token")) {
      router.push("/login");
      return;
    }
    fetchState();
  }, [router]);

  async function fetchState() {
    try {
      const res = await getCurrentState();
      if (res.ok) {
        const data = await res.json();
        setState(data);
        if (data.emotion !== "neutral") {
          setChartData([{ time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}), intensity: data.intensity || 0.5, mood: data.emotion }]);
        }
      }

      const riskRes = await getRisk();
      if (riskRes.ok) {
        const riskData = await riskRes.json();
        if (riskData.type) setRiskAlert(riskData);
      }

      const pbRes = await getPlaybook();
      if (pbRes.ok) {
        setPlaybook(await pbRes.json());
      }

      const metaRes = await getMetaProfile();
      if (metaRes.ok) {
        setMetaProfile(await metaRes.json());
      }

      const telRes = await getTelemetry();
      if (telRes.ok) {
        setTelemetry(await telRes.json());
      }

      const scRes = await getConsolidatedSchemas();
      if (scRes.ok) {
        setSchemas(await scRes.json());
      }

      const ambRes = await getAmbientStatus();
      if (ambRes.ok) {
        setAmbientData(await ambRes.json());
      }
    } catch (e) {
      console.warn("Backend unavailable or initial state, providing default dashboard baseline:", e);
      setState({ emotion: "focused", intensity: 0.65 });
      setChartData([
        { time: "09:00", intensity: 0.4, mood: "calm" },
        { time: "12:00", intensity: 0.6, mood: "focused" },
        { time: "15:00", intensity: 0.75, mood: "strained" },
        { time: "18:00", intensity: 0.5, mood: "reflective" }
      ]);
      setTelemetry({
        dominant_agent: "StrategyAgent",
        system_stability: "Stable",
        avg_reliability: 0.94,
        learning_status: "Improving",
        entropy: 0.38
      });
      setAmbientData({
        circadian_phase: "Midday Surge",
        cognitive_capacity: 0.85,
        stress_velocity: 0.12,
        active_alerts: []
      });
    }
  }

  async function handleLog(mood: string, intensity: number) {
    setState({ emotion: mood, intensity });
    setChartData(prev => [...prev, { time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}), intensity, mood }]);
    
    try {
      const res = await logMood({ mood_type: mood, intensity });
      if (res.ok) {
        const data = await res.json();
        if (data.nudge) setNudge(data.nudge);
      }
    } catch (e) { console.error(e); }
  }

  async function handleActionLog(type: string, ctx: string) {
    try {
      await logBehavior({ type, value: 1.0, context: ctx });
      // Minor UI confirmation could go here
    } catch(e) { console.error(e); }
  }

  async function handleAnalyze() {
    if (!journalText.trim()) return;
    setAnalyzing(true);
    try {
      const res = await analyzeText(journalText);
      if (res.ok) {
        const data = await res.json();
        setBiases(data.biases || []);
      }
    } catch (e) { console.error(e); }
    setAnalyzing(false);
  }

  const renderHighlightedText = () => {
    const regex = /\b(always|never|everyone|no one)\b/gi;
    const parts: (string | React.ReactNode)[] = journalText.split(regex);
    for (let i = 1; i < parts.length; i += 2) {
      parts[i] = <span key={i} className="underline decoration-red-500/70 underline-offset-4 bg-red-500/10 rounded px-1">{parts[i]}</span>;
    }
    return <div className="p-4 whitespace-pre-wrap font-sans text-transparent">{parts.map((p, i) => p)}</div>;
  };

  const messages: Record<string, string> = {
    stressed: "You've been slightly stressed today.",
    calm: "You're centered and calm right now.",
    motivated: "High energy! You are highly motivated.",
    fatigued: "You're running low on energy.",
    neutral: "I'm ready when you are. How are you feeling?"
  };

  return (
    <div className="min-h-screen bg-[#0B0F1A] text-white p-6 md:p-12 font-sans selection:bg-purple-900/50 flex flex-col items-center relative overflow-hidden">
      
      {/* Warning Banner Layer */}
      {riskAlert && (
        <div className="w-full max-w-6xl mb-8 animate-dropdown">
          <div className="bg-gradient-to-r from-red-900/90 to-orange-900/80 border border-red-500/50 shadow-2xl rounded-2xl p-4 flex justify-between items-center backdrop-blur-md relative overflow-hidden group">
            <div className="flex items-center space-x-4 z-10 relative">
              <div className="bg-red-500/20 p-2 rounded-full border border-red-500/30">
                <span className="w-3 h-3 bg-red-400 rounded-full animate-ping block"></span>
              </div>
              <div>
                <h3 className="font-bold text-red-100 uppercase tracking-widest text-sm flex items-center space-x-2">
                  <span>Early Warning Detected</span>
                  {riskAlert.confidence && <span className="bg-red-950 px-2 py-0.5 rounded text-xs text-red-300">{(riskAlert.confidence * 100).toFixed(0)}% Certainty</span>}
                </h3>
                <p className="text-red-200/90 text-sm mt-1">{riskAlert.message}</p>
              </div>
            </div>
            <button onClick={() => setRiskAlert(null)} className="text-red-300 hover:text-white transition z-10 relative bg-red-950/50 p-2 rounded-xl">Dismiss</button>
            <div className="absolute inset-0 bg-red-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-1000 blur-2xl"></div>
          </div>
        </div>
      )}

      <div className="flex space-x-8 w-full max-w-7xl">
        {/* Main Column */}
      <div className="flex-1 max-w-4xl mx-auto flex flex-col space-y-12">
        <header className="flex justify-between items-end">
          <div>
            <h1 className="text-4xl font-light tracking-tight text-gray-100">Your Mind Today</h1>
            <p className="text-gray-400 mt-2 text-lg">{messages[state.emotion] || messages.neutral}</p>
          </div>
          <div className="flex space-x-3 mb-2">
            <button onClick={() => setVaultOpen(true)} className="px-4 py-2 bg-indigo-950/40 hover:bg-indigo-900/60 text-indigo-300 rounded-xl transition border border-indigo-500/30 text-xs font-medium flex items-center gap-1.5">
              <Lock size={12} />
              <span>Privacy Vault</span>
            </button>
            <button onClick={() => router.push("/simulate")} className="px-5 py-2 bg-[#111827] hover:bg-gray-800 text-gray-300 rounded-xl transition border border-gray-800 text-xs">
               Simulation
            </button>
            <button onClick={() => router.push("/evolution")} className="px-5 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white rounded-xl transition shadow-lg shadow-purple-500/20 font-medium text-xs">
               Evolution Engine
            </button>
          </div>
        </header>

        {ambientData && <AmbientMonitorBanner ambientData={ambientData} />}

        {telemetry && (
          <SystemAwarenessPanel
            learningHealth={telemetry.learning_health}
            dominantAgent={telemetry.dominant_agent}
            effectiveAccuracies={telemetry.effective_accuracies}
          />
        )}

        <div className="grid lg:grid-cols-2 gap-12">
          {/* Left Column: Perception & Logging */}
          <div className="flex flex-col space-y-8 h-full"> 
            <StateOrb emotion={state.emotion} />
            
            <div className="bg-[#111827] rounded-3xl p-8 border border-gray-800 shadow-2xl">
              <h3 className="text-xs text-gray-500 mb-6 uppercase tracking-widest font-bold">Log your psychological state</h3>
              <div className="grid grid-cols-2 gap-4">
                <button onClick={() => handleLog("calm", 0.3)} className="bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 py-3 rounded-2xl transition border border-cyan-500/10">Calm</button>
                <button onClick={() => handleLog("motivated", 0.9)} className="bg-purple-500/10 hover:bg-purple-500/20 text-purple-400 py-3 rounded-2xl transition border border-purple-500/10">Motivated</button>
                <button onClick={() => handleLog("stressed", 0.8)} className="bg-orange-500/10 hover:bg-orange-500/20 text-orange-400 py-3 rounded-2xl transition border border-orange-500/10">Stressed</button>
                <button onClick={() => handleLog("fatigued", 0.2)} className="bg-slate-700/30 hover:bg-slate-700/50 text-slate-400 py-3 rounded-2xl transition border border-slate-700/50">Fatigued</button>
              </div>
            </div>

            <div className="bg-[#111827] rounded-3xl p-8 border border-gray-800 shadow-2xl">
              <h3 className="text-xs text-gray-500 mb-6 uppercase tracking-widest font-bold">Log recent behavior</h3>
              <div className="flex space-x-3">
                <button onClick={() => handleActionLog("task", "coding")} className="px-4 py-2 bg-blue-900/40 text-blue-300 rounded-xl hover:bg-blue-800/60 transition">💻 Coding</button>
                <button onClick={() => handleActionLog("social", "meeting")} className="px-4 py-2 bg-green-900/40 text-green-300 rounded-xl hover:bg-green-800/60 transition">🤝 Meeting</button>
                <button onClick={() => handleActionLog("study", "learning")} className="px-4 py-2 bg-amber-900/40 text-amber-300 rounded-xl hover:bg-amber-800/60 transition">📚 Study</button>
              </div>
            </div>
          </div>

          {/* Center Column: Cognition & Trends */}
          <div className="flex flex-col h-full space-y-8">
            <div className="bg-[#111827] p-8 rounded-3xl border border-gray-800 flex-grow shadow-2xl">
              <div className="flex justify-between items-start mb-8">
                <div>
                  <div className="text-xs text-gray-500 uppercase font-bold tracking-widest mb-1">State Vector</div>
                  <div className="text-xl font-medium text-gray-200 capitalize">{state.emotion} Dominant</div>
                </div>
              </div>
              <MoodChart data={chartData} />
            </div>

            <div className="bg-[#111827] p-8 rounded-3xl border border-gray-800 shadow-2xl flex flex-col">
              <h3 className="text-xs text-gray-500 mb-4 uppercase tracking-widest font-bold">Thought Journal</h3>
              <div className="relative flex-grow">
                {/* The overlay for rendering custom highlights */}
                <div className="absolute inset-0 pointer-events-none z-10 break-words text-gray-300 text-sm h-32 overflow-hidden">
                  {renderHighlightedText()}
                </div>
                {/* Ghost Text Overlay */}
                {/\bi always fail\b/i.test(journalText) && (
                  <div className="absolute inset-x-4 top-10 pointer-events-none z-15 text-gray-500 italic text-sm animate-pulse flex flex-col items-start translate-y-10">
                    <span className="text-purple-400 shadow-xl bg-gray-900/80 px-3 py-1 rounded-lg border border-purple-500/30">
                      💡 Sometimes I struggle, but I can improve...
                    </span>
                  </div>
                )}
                <textarea 
                  value={journalText} 
                  onChange={(e) => setJournalText(e.target.value)} 
                  placeholder="What's on your mind? (Try typing: 'I always fail' to see detection)"
                  className="w-full h-32 p-4 bg-gray-900/50 border border-gray-700/50 rounded-xl resize-none text-transparent caret-white focus:outline-none focus:border-purple-500/50 transition relative z-20 text-sm font-sans"
                />
              </div>
              <button 
                onClick={handleAnalyze} 
                className="mt-4 bg-purple-600 hover:bg-purple-500 text-white py-2 px-6 rounded-xl font-medium transition self-start disabled:opacity-50"
                disabled={analyzing}
              >
                {analyzing ? "Analyzing..." : "Analyze Thoughts"}
              </button>
            </div>
          </div>
        </div>

        {/* Phase 11 Autobiographical Memory & Retrospective Explorer */}
        <RetrospectiveMemoryCard initialSchemas={schemas} />
      </div>

      {/* Right Sidebar: Insight Panel */}
      <div className="w-80 bg-[#111827] border-l border-gray-800 p-6 flex flex-col pt-12 overflow-y-auto hidden xl:flex">
        <h2 className="text-sm font-bold text-gray-500 uppercase tracking-widest mb-6">Cognitive Mirror</h2>
        
        {telemetry && (
          <div className="mb-6">
            <LearningHealthCard
              learningHealth={telemetry.learning_health}
              policyEntropy={0.82}
              recoveryModeActive={telemetry.learning_health?.status === "unstable"}
            />
          </div>
        )}

        {metaProfile ? (
          <div className="space-y-6">
            
            {/* 1. Risk (burnout) */}
            {metaProfile["7_day_projection"] && (
              <div className="bg-red-900/10 border border-red-500/30 rounded-2xl p-5 relative overflow-hidden group">
                <div className="absolute inset-0 bg-gradient-to-tr from-red-500/5 to-transparent transition-opacity opacity-0 group-hover:opacity-100"></div>
                <div className="flex justify-between items-start mb-2 relative z-10">
                   <div className="flex items-center space-x-2">
                     <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                     <h4 className="font-semibold text-red-300 font-sans tracking-wide">Long-Term Risk</h4>
                   </div>
                   {metaProfile["7_day_projection"].confidence && (
                     <div className="text-[10px] bg-red-950 px-2 py-0.5 rounded text-red-400 border border-red-500/30">
                       {(metaProfile["7_day_projection"].confidence * 100).toFixed(0)}% Conf
                     </div>
                   )}
                </div>
                <div className="text-sm text-gray-300 relative z-10">{metaProfile["7_day_projection"].risk}</div>
                <p className="text-xs text-gray-500 mt-2 italic relative z-10">{metaProfile["7_day_projection"].reason}</p>
                
                {/* Explainability / Basis expansion */}
                {metaProfile["7_day_projection"].basis && metaProfile["7_day_projection"].basis.length > 0 && (
                   <div className="mt-4 pt-3 border-t border-red-500/20 relative z-10">
                      <details className="cursor-pointer group/details">
                         <summary className="text-xs font-semibold text-red-400/80 hover:text-red-300 transition marker:text-transparent">
                            🔍 Why this insight?
                         </summary>
                         <ul className="mt-2 space-y-1 bg-[#0B0F1A]/80 p-2 rounded-lg border border-red-500/10">
                           {metaProfile["7_day_projection"].basis.map((b: string, i: number) => (
                              <li key={i} className="text-[10px] text-gray-400 font-mono tracking-tighter">└ {b}</li>
                           ))}
                         </ul>
                      </details>
                   </div>
                )}
              </div>
            )}

            {/* 2. Dissonance */}
            {metaProfile.dissonance && metaProfile.dissonance.dissonance > 0.4 && (
              <div className="bg-orange-900/10 border border-orange-500/30 rounded-2xl p-5 relative">
                <h4 className="font-semibold text-orange-300 mb-2">Behavioral Dissonance</h4>
                <div className="text-sm text-gray-300">{metaProfile.dissonance.insight}</div>
                <div className="mt-3 bg-[#0B0F1A] h-1.5 rounded-full overflow-hidden">
                  <div className="bg-orange-500 h-full" style={{ width: `${metaProfile.dissonance.dissonance * 100}%` }}></div>
                </div>
              </div>
            )}

            {/* 3. Archetype */}
            {metaProfile.archetype && (
              <div className="bg-cyan-900/10 border border-cyan-500/30 rounded-2xl p-5 flex flex-col items-center">
                <div className="text-xs font-bold text-cyan-700 uppercase tracking-widest mb-2">Current Mode</div>
                <h4 className="font-medium text-cyan-300 text-lg">You are currently operating in a {metaProfile.archetype.dominant}-dominant mode.</h4>
                {metaProfile.archetype.secondary && (
                   <p className="text-xs text-gray-500 mt-2">Secondary: {metaProfile.archetype.secondary}</p>
                )}
              </div>
            )}

          </div>
        ) : (
          <div className="text-sm text-gray-600 italic mb-6">Compiling Meta Intelligence...</div>
        )}

        <h2 className="text-sm font-bold text-gray-500 uppercase tracking-widest mt-10 mb-6">Your Personal Playbook</h2>
        {playbook.length > 0 ? (
          <div className="space-y-3">
             {playbook.map((strategy, idx) => (
                <div key={idx} className="bg-[#0B0F1A]/80 border border-gray-800 rounded-xl p-4 flex justify-between items-center text-sm group hover:border-purple-500/50 transition">
                   <div>
                     <div className="font-medium text-gray-200 group-hover:text-purple-300 transition">{strategy.action}</div>
                     <div className="text-xs text-gray-500 capitalize leading-relaxed">{strategy.emotion} State</div>
                   </div>
                   <div className="text-right">
                     <div className="font-bold text-purple-400">{(strategy.score * 100).toFixed(0)}%</div>
                     <div className="text-[10px] bg-purple-900/30 text-purple-200 px-1.5 py-0.5 rounded mt-1">{(strategy.confidence * 100).toFixed(0)}% Conf</div>
                   </div>
                </div>
             ))}
          </div>
        ) : (
          <div className="text-sm text-gray-600 italic">Playbook is compiling strategies based on RL loops...</div>
        )}
      </div>

      </div>

      <NudgeCard nudge={nudge} onClose={() => setNudge(null)} />
      <PrivacyVaultModal isOpen={vaultOpen} onClose={() => setVaultOpen(false)} />
    </div>
  );
}
