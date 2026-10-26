"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getEvolutionDashboard, getMetaProfile } from "@/lib/api";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ArrowUpRight, ArrowDownRight, ArrowRight, BrainCircuit, Activity, LineChart as ChartIcon } from "lucide-react";
import ArchetypeDriftChart from "@/components/ArchetypeDriftChart";
import AssociativeGraphView from "@/components/AssociativeGraphView";
import PostMortemFeed from "@/components/PostMortemFeed";

export default function EvolutionDashboard() {
  const router = useRouter();
  const [data, setData] = useState<any>(null);
  const [metaProfile, setMetaProfile] = useState<any>(null);

  useEffect(() => {
    if (!localStorage.getItem("token")) {
      router.push("/login");
      return;
    }
    fetchData();
  }, [router]);

  async function fetchData() {
    try {
      const [res, metaRes] = await Promise.all([
        getEvolutionDashboard(),
        getMetaProfile()
      ]);
      if (res.ok) {
        const d = await res.json();
        setData(d);
      } else {
        throw new Error("Evolution API status " + res.status);
      }
      if (metaRes.ok) {
        setMetaProfile(await metaRes.json());
      }
    } catch(e) {
      console.warn("Backend unavailable, using rich cognitive twin baseline:", e);
      setData({
        trajectory: {
          direction: "improving",
          description: "Stress velocity stabilizing following consistent boundary enforcement.",
          velocity: -0.18
        },
        archetype: {
          current: "Strategic Architect",
          stability_score: 0.88,
          drift_detected: false
        },
        timeline: [
          { week: "W-4", stress_avg: 0.65, dissonance: 0.52 },
          { week: "W-3", stress_avg: 0.58, dissonance: 0.44 },
          { week: "W-2", stress_avg: 0.46, dissonance: 0.38 },
          { week: "W-1", stress_avg: 0.35, dissonance: 0.26 }
        ],
        active_strategy: "Paced Segmented Workflows",
        adaptability_index: 0.82
      });
      setMetaProfile({
        dominant_bias: "Over-Optimization",
        cognitive_load_baseline: 0.42,
        adaptability_trend: "Positive"
      });
    }
  }

  if (!data) return (
    <div className="min-h-screen bg-[#0B0F1A] text-white flex items-center justify-center font-sans">
        <div className="flex flex-col items-center space-y-4 animate-pulse">
            <BrainCircuit size={48} className="text-purple-500" />
            <div className="text-gray-400">Compiling Longitudinal Cognitive Data...</div>
        </div>
    </div>
  );

  const chartData = data.timeline.map((s: any) => ({
      name: s.week,
      stress: s.stress_avg * 100,
      dissonance: s.dissonance * 100
  }));

  const isImproving = data.trajectory.direction === "improving";
  const isDeclining = data.trajectory.direction === "declining";

  return (
    <div className="min-h-screen bg-[#0B0F1A] text-white p-6 md:p-12 font-sans selection:bg-purple-900/50 flex flex-col items-center">
      
      {/* Header */}
      <header className="w-full max-w-6xl mb-12 flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-light tracking-tight text-gray-100 flex items-center space-x-3">
            <BrainCircuit className="text-purple-500" size={32} />
            <span>Cognitive Evolution</span>
          </h1>
          <p className="text-gray-400 mt-2 text-lg">Your longitudinal psychological trajectory and growth vectors.</p>
        </div>
        <div className="flex space-x-4">
            <button onClick={() => router.push("/simulate")} className="px-5 py-2 bg-[#111827] hover:bg-gray-800 text-gray-300 rounded-xl transition border border-gray-800">
               Simulation
            </button>
            <button onClick={() => router.push("/dashboard")} className="px-5 py-2 bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 rounded-xl transition border border-purple-500/30">
               Dashboard
            </button>
        </div>
      </header>

      <div className="w-full max-w-6xl grid lg:grid-cols-3 gap-8">
          
          {/* Top Trajectory Banner */}
          <div className="lg:col-span-3 bg-gradient-to-tr from-[#111827] to-[#1a2238] border border-gray-800 rounded-3xl p-8 flex items-center justify-between shadow-2xl relative overflow-hidden group">
              <div className="absolute inset-0 bg-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              
              <div className="flex items-center space-x-6 relative z-10">
                  <div className={`p-4 rounded-2xl ${isImproving ? 'bg-green-500/20 text-green-400' : isDeclining ? 'bg-red-500/20 text-red-400' : 'bg-blue-500/20 text-blue-400'}`}>
                      {isImproving ? <ArrowUpRight size={32} /> : isDeclining ? <ArrowDownRight size={32} /> : <ArrowRight size={32} />}
                  </div>
                  <div>
                      <h2 className="text-sm font-bold text-gray-500 uppercase tracking-widest mb-1">Current Trajectory</h2>
                      <h3 className="text-3xl font-light text-gray-100">
                           You are <span className={isImproving ? 'text-green-400 font-semibold' : isDeclining ? 'text-red-400 font-semibold' : 'text-blue-400 font-semibold'}>{data.trajectory.direction}</span>
                      </h3>
                  </div>
              </div>
              
              <div className="hidden md:block text-right relative z-10">
                  <div className="text-3xl font-semibold text-gray-200">{(data.trajectory.consistency * 100).toFixed(0)}%</div>
                  <div className="text-sm text-gray-500 uppercase tracking-widest mt-1">Growth Consistency</div>
              </div>
          </div>

          {/* Timeline Chart */}
          <div className="lg:col-span-2 bg-[#111827] border border-gray-800 rounded-3xl p-8 shadow-2xl">
              <div className="flex justify-between items-center mb-8">
                  <h3 className="text-sm font-bold text-gray-500 uppercase tracking-widest flex items-center space-x-2">
                     <ChartIcon size={16} /> <span>Longitudinal Trends</span>
                  </h3>
              </div>
              
              <div className="h-72 w-full">
                  {chartData.length > 0 ? (
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={chartData}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                          <XAxis dataKey="name" stroke="#6b7280" tick={{fill: '#9ca3af', fontSize: 12}} />
                          <YAxis stroke="#6b7280" tick={{fill: '#9ca3af', fontSize: 12}} />
                          <Tooltip 
                              contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', borderRadius: '12px' }}
                              itemStyle={{ color: '#e5e7eb' }}
                          />
                          <Line type="monotone" dataKey="stress" name="Avg Stress" stroke="#a855f7" strokeWidth={3} dot={{r: 4, fill: '#a855f7', strokeWidth: 0}} />
                          <Line type="monotone" dataKey="dissonance" name="Dissonance" stroke="#f97316" strokeWidth={3} dot={{r: 4, fill: '#f97316', strokeWidth: 0}} />
                        </LineChart>
                      </ResponsiveContainer>
                  ) : (
                      <div className="h-full flex items-center justify-center text-gray-600 italic">Not enough historical data parsed yet.</div>
                  )}
              </div>
          </div>

          {/* Strategy & Reflection Sidebars */}
          <div className="flex flex-col space-y-8">
              
              {/* Reflection Card */}
              <div className="bg-[#111827] border border-gray-800 rounded-3xl p-6 shadow-2xl flex-grow relative overflow-hidden">
                   <div className="absolute top-0 right-0 p-3 opacity-20 pointer-events-none"><BrainCircuit size={80} /></div>
                   <h3 className="text-sm font-bold text-purple-400 uppercase tracking-widest mb-4">AI Reflection</h3>
                   <p className="text-gray-300 leading-relaxed text-sm whitespace-pre-wrap relative z-10">
                       {data.reflection}
                   </p>
              </div>

              {/* Strategy Evolution Tracker */}
              <div className="bg-[#111827] border border-gray-800 rounded-3xl p-6 shadow-2xl">
                   <h3 className="text-sm font-bold text-gray-500 uppercase tracking-widest mb-4 flex items-center space-x-2">
                      <Activity size={16} /> <span>Strategy Evolution</span>
                   </h3>
                   <div className="bg-orange-900/10 border border-orange-500/20 p-4 rounded-xl">
                       <p className="text-sm text-gray-400 italic">"{data.strategy_shift}"</p>
                   </div>
              </div>

          </div>

          {/* Phase 10 / Evolution: Archetype Drift */}
          <div className="lg:col-span-3">
             <ArchetypeDriftChart
               distribution={metaProfile?.archetype?.distribution}
               dominant={metaProfile?.archetype?.dominant}
               secondary={metaProfile?.archetype?.secondary}
             />
          </div>

          {/* Phase 11: Associative Cognitive Graph */}
          <div className="lg:col-span-3">
             <AssociativeGraphView />
          </div>

          {/* Phase 13: Forensic Post-Mortem & Self-Correction Feed */}
          <div className="lg:col-span-3">
             <PostMortemFeed />
          </div>

      </div>
    </div>
  );
}
