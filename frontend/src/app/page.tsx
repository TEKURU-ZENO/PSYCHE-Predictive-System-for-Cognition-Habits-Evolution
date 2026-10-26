"use client";

import Link from "next/link";
import { 
  BrainCircuit, 
  Sparkles, 
  ShieldCheck, 
  Activity, 
  GitBranch, 
  Lock, 
  Database, 
  Compass, 
  Scale, 
  Flame, 
  ArrowRight, 
  Layers, 
  Cpu, 
  CheckCircle2 
} from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-[#090a0f] text-zinc-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white">
      {/* Background ambient lighting */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 left-1/2 -translate-x-1/2 w-[850px] h-[500px] bg-gradient-to-b from-indigo-950/40 via-purple-950/20 to-transparent blur-[140px] rounded-full" />
        <div className="absolute top-1/2 -left-48 w-[500px] h-[500px] bg-blue-950/20 blur-[130px] rounded-full" />
        <div className="absolute bottom-10 -right-48 w-[500px] h-[500px] bg-purple-950/20 blur-[130px] rounded-full" />
      </div>

      {/* Top Navbar */}
      <header className="sticky top-0 z-50 border-b border-zinc-800/80 bg-[#090a0f]/80 backdrop-blur-md">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-800 shadow-sm">
              <BrainCircuit className="w-5 h-5 text-indigo-400" />
            </div>
            <span className="font-semibold text-lg tracking-tight text-white">
              Psych<span className="text-indigo-400">-AI</span>
            </span>
          </Link>

          <nav className="hidden md:flex items-center gap-7 text-sm font-medium text-zinc-400">
            <Link href="/dashboard" className="hover:text-zinc-100 transition-colors">Cognitive State</Link>
            <Link href="/simulate" className="hover:text-zinc-100 transition-colors">Multi-Agent Debate</Link>
            <Link href="/evolution" className="hover:text-zinc-100 transition-colors">Longitudinal Evolution</Link>
          </nav>

          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="px-3.5 py-1.5 text-xs font-medium rounded-lg text-zinc-300 hover:text-white hover:bg-zinc-800/60 transition-colors"
            >
              Sign In
            </Link>
            <Link
              href="/dashboard"
              className="px-4 py-1.5 text-xs font-medium rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow-sm shadow-indigo-600/30 transition-all flex items-center gap-1.5"
            >
              <span>Launch Platform</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 max-w-6xl mx-auto px-6 pt-20 pb-28 relative z-10">
        <div className="flex flex-col items-center text-center max-w-3xl mx-auto">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-indigo-500/30 bg-indigo-950/30 text-indigo-300 text-xs font-mono tracking-wide mb-8 backdrop-blur-md">
            <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse" />
            <span>Autonomous Cognitive Twin Platform &middot; v1.7.0</span>
          </div>

          {/* Headline */}
          <h1 className="text-4xl sm:text-6xl font-semibold tracking-tight text-white leading-[1.12] mb-6">
            Your Cognitive Twin. <br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-300 via-purple-300 to-indigo-100">
              Continuous Multi-Agent Reasoning.
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-base sm:text-lg text-zinc-400 leading-relaxed max-w-2xl mb-10 font-normal">
            Psych-AI coordinates multi-agent dialectical debate, autobiographical episodic memory, 
            circadian cognitive rhythm forecasting, and forensic decision verification to safeguard psychological energy.
          </p>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row items-center gap-3.5 w-full sm:w-auto">
            <Link
              href="/dashboard"
              className="w-full sm:w-auto px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium shadow-xl shadow-indigo-600/25 transition-all flex items-center justify-center gap-2"
            >
              <Activity className="w-4 h-4" />
              <span>Open Cognitive Dashboard</span>
            </Link>
            <Link
              href="/simulate"
              className="w-full sm:w-auto px-6 py-3 rounded-xl bg-zinc-900/80 hover:bg-zinc-800 border border-zinc-800 text-zinc-300 text-sm font-medium transition-all flex items-center justify-center gap-2"
            >
              <GitBranch className="w-4 h-4 text-purple-400" />
              <span>Simulate Deliberation</span>
            </Link>
          </div>
        </div>

        {/* Live Architecture Grid Preview */}
        <div className="mt-20 p-1 rounded-2xl bg-gradient-to-b from-zinc-800/80 via-zinc-900/40 to-transparent">
          <div className="rounded-[15px] bg-[#0c0d14]/90 border border-zinc-800/80 p-6 sm:p-8 backdrop-blur-xl">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 mb-8 border-b border-zinc-800/80 gap-4">
              <div>
                <span className="text-xs font-mono text-indigo-400 uppercase tracking-wider block mb-1">
                  Active Multi-Agent Deliberation Bus
                </span>
                <h3 className="text-lg font-medium text-white">Dialectical Consensus Engine</h3>
              </div>
              <div className="flex items-center gap-2 font-mono text-xs text-emerald-400 bg-emerald-950/40 border border-emerald-800/50 px-3 py-1 rounded-full w-fit">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                <span>5 Agents Active &middot; Safe Mode Online</span>
              </div>
            </div>

            {/* Agent Pipeline Flow */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-3.5">
              <div className="p-4 rounded-xl bg-zinc-900/60 border border-zinc-800/80">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-mono text-zinc-400">01. SENSE</span>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-900/50 text-emerald-300 border border-emerald-700/50">Trusted</span>
                </div>
                <h4 className="text-sm font-semibold text-zinc-100">PerceptionAgent</h4>
                <p className="text-xs text-zinc-400 mt-1">Classifies acute stress signals and environmental context.</p>
              </div>

              <div className="p-4 rounded-xl bg-zinc-900/60 border border-zinc-800/80">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-mono text-zinc-400">02. AUDIT</span>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-900/50 text-emerald-300 border border-emerald-700/50">Trusted</span>
                </div>
                <h4 className="text-sm font-semibold text-zinc-100">CognitionAgent</h4>
                <p className="text-xs text-zinc-400 mt-1">Isolates cognitive distortions and heuristic vulnerabilities.</p>
              </div>

              <div className="p-4 rounded-xl bg-zinc-900/60 border border-zinc-800/80">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-mono text-zinc-400">03. FORECAST</span>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-blue-900/50 text-blue-300 border border-blue-700/50">Stable</span>
                </div>
                <h4 className="text-sm font-semibold text-zinc-100">PredictionAgent</h4>
                <p className="text-xs text-zinc-400 mt-1">Models 4-branch counterfactual burnout trajectories.</p>
              </div>

              <div className="p-4 rounded-xl bg-zinc-900/60 border border-zinc-800/80">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-mono text-zinc-400">04. FORMULATE</span>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-900/50 text-emerald-300 border border-emerald-700/50">Trusted</span>
                </div>
                <h4 className="text-sm font-semibold text-zinc-100">StrategyAgent</h4>
                <p className="text-xs text-zinc-400 mt-1">Selects Q-learning policy adapted to user precedent.</p>
              </div>

              <div className="p-4 rounded-xl bg-zinc-900/60 border border-zinc-800/80">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-mono text-zinc-400">05. GOVERN</span>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-purple-900/50 text-purple-300 border border-purple-700/50">Master</span>
                </div>
                <h4 className="text-sm font-semibold text-zinc-100">MetaAgent</h4>
                <p className="text-xs text-zinc-400 mt-1">Enforces ethical guardrails and resolves inter-agent conflict.</p>
              </div>
            </div>
          </div>
        </div>

        {/* 4 Architectural Pillars */}
        <div className="mt-28 grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Pillar 1 */}
          <div className="p-7 rounded-2xl bg-zinc-900/30 border border-zinc-800/70 hover:border-zinc-700/80 transition-colors">
            <div className="p-2.5 rounded-xl bg-indigo-950/40 border border-indigo-800/40 w-fit mb-5 text-indigo-400">
              <Database className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-medium text-white mb-2">Autobiographical Episodic Memory</h3>
            <p className="text-sm text-zinc-400 leading-relaxed mb-4">
              A Hebbian association network links triggers, cognitive distortions, and behavioral responses. Sleep-like memory consolidation extracts recurring life patterns into general schemas.
            </p>
            <div className="flex items-center gap-2 text-xs font-mono text-indigo-400">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Phase 11 Hebbian Graph Reinforced</span>
            </div>
          </div>

          {/* Pillar 2 */}
          <div className="p-7 rounded-2xl bg-zinc-900/30 border border-zinc-800/70 hover:border-zinc-700/80 transition-colors">
            <div className="p-2.5 rounded-xl bg-purple-950/40 border border-purple-800/40 w-fit mb-5 text-purple-400">
              <Compass className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-medium text-white mb-2">Circadian Rhythm & Counterfactuals</h3>
            <p className="text-sm text-zinc-400 leading-relaxed mb-4">
              Ambient rhythm monitoring models diurnal cognitive capacity and stress velocity spikes, while the 4-branch shadow engine evaluates "What-If" branches before action execution.
            </p>
            <div className="flex items-center gap-2 text-xs font-mono text-indigo-400">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Phase 12 Shadow Engine Active</span>
            </div>
          </div>

          {/* Pillar 3 */}
          <div className="p-7 rounded-2xl bg-zinc-900/30 border border-zinc-800/70 hover:border-zinc-700/80 transition-colors">
            <div className="p-2.5 rounded-xl bg-red-950/40 border border-red-800/40 w-fit mb-5 text-red-400">
              <Scale className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-medium text-white mb-2">Adversarial Red-Team & Post-Mortem</h3>
            <p className="text-sm text-zinc-400 leading-relaxed mb-4">
              Zero sycophancy or toxic positivity. Pre-dispatch audits enforce safety vetoes against burnout-accelerating consensus, while post-mortem root cause analysis penalizes degraded agents.
            </p>
            <div className="flex items-center gap-2 text-xs font-mono text-indigo-400">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Phase 13 Pre-Dispatch Gatekeeper Active</span>
            </div>
          </div>

          {/* Pillar 4 */}
          <div className="p-7 rounded-2xl bg-zinc-900/30 border border-zinc-800/70 hover:border-zinc-700/80 transition-colors">
            <div className="p-2.5 rounded-xl bg-amber-950/40 border border-amber-800/40 w-fit mb-5 text-amber-400">
              <Lock className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-medium text-white mb-2">Forensic Replay & Data Sovereignty</h3>
            <p className="text-sm text-zinc-400 leading-relaxed mb-4">
              Every deliberation is sealed with SHA-256 cryptographic hashes for bit-for-bit replayability. The Zero-Knowledge Privacy Vault empowers selective purging and total JSON twin portability.
            </p>
            <div className="flex items-center gap-2 text-xs font-mono text-indigo-400">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Phase 14 & 15 Forensic Replay Verified</span>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-zinc-800/80 py-10 bg-[#07080c] relative z-10">
        <div className="max-w-6xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between text-xs text-zinc-500 font-mono gap-4">
          <div className="flex items-center gap-2">
            <BrainCircuit className="w-4 h-4 text-indigo-400" />
            <span>Psych-AI Platform &copy; 2026 &middot; Production Certified</span>
          </div>
          <div className="flex items-center gap-6">
            <Link href="/dashboard" className="hover:text-zinc-300 transition-colors">Dashboard</Link>
            <Link href="/simulate" className="hover:text-zinc-300 transition-colors">Simulate</Link>
            <Link href="/evolution" className="hover:text-zinc-300 transition-colors">Evolution</Link>
            <Link href="/login" className="hover:text-zinc-300 transition-colors">Console</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
