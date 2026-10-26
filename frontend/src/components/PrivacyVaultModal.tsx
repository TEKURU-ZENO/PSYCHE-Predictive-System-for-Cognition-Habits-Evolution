"use client";
import { useState } from "react";
import { exportPrivacyVault } from "@/lib/api";
import { ShieldCheck, Download, Lock, FileCode, CheckCircle2, X } from "lucide-react";

interface PrivacyVaultModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function PrivacyVaultModal({ isOpen, onClose }: PrivacyVaultModalProps) {
  const [downloading, setDownloading] = useState(false);
  const [downloaded, setDownloaded] = useState(false);

  if (!isOpen) return null;

  const handleDownload = async () => {
    setDownloading(true);
    try {
      const res = await exportPrivacyVault();
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `psychai_cognitive_twin_vault_${new Date().toISOString().split("T")[0]}.json`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        setDownloaded(true);
        setTimeout(() => setDownloaded(false), 4000);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 animate-in fade-in duration-200">
      <div className="bg-[#111827] border border-gray-800 w-full max-w-xl rounded-3xl p-6 md:p-8 shadow-2xl relative">
        <div className="flex justify-between items-start pb-4 border-b border-gray-800 mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <Lock size={20} />
            </div>
            <div>
              <h2 className="text-base font-semibold text-gray-100 flex items-center gap-2">
                <span>Data Sovereignty & Privacy Vault</span>
                <span className="text-[10px] bg-indigo-900/40 text-indigo-300 px-2 py-0.5 rounded-full border border-indigo-500/30 font-mono">
                  Phase 14
                </span>
              </h2>
              <p className="text-xs text-gray-400">
                You own 100% of your cognitive models, episodic logs, and psychological weights.
              </p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-gray-800 rounded-xl text-gray-400 hover:text-white transition">
            <X size={18} />
          </button>
        </div>

        {/* Guarantees Box */}
        <div className="space-y-4 mb-6">
          <div className="bg-[#0B0F1A] border border-gray-800 p-4 rounded-2xl space-y-2 text-xs">
            <div className="flex items-center gap-2 text-gray-200 font-semibold">
              <ShieldCheck size={16} className="text-emerald-400" />
              <span>Cryptographic Privacy Guarantees</span>
            </div>
            <ul className="space-y-1.5 text-gray-400 text-[11px] pt-1">
              <li>• Complete data exportability in standard open JSON format.</li>
              <li>• Zero third-party telemetry: all deliberation traces are self-contained.</li>
              <li>• Selective memory pruning with Right to be Forgotten support.</li>
              <li>• SHA-256 tamper-evident event hashing for all cognitive decisions.</li>
            </ul>
          </div>

          <div className="bg-[#0B0F1A] border border-gray-800 p-4 rounded-2xl text-xs space-y-1 text-gray-400">
            <span className="text-gray-300 font-semibold block text-[11px]">Included in Export Bundle:</span>
            <span className="font-mono text-[10px] text-purple-300 block">
              [UserState, MoodLogs, BehaviorLogs, Triggers, EpisodicMemories, AssociativeGraph, Schemas, PostMortems]
            </span>
          </div>
        </div>

        {/* Export Button */}
        <button
          onClick={handleDownload}
          disabled={downloading}
          className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium py-3 rounded-2xl transition flex items-center justify-center space-x-2 text-xs shadow-lg shadow-indigo-600/20"
        >
          {downloading ? (
            <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
          ) : downloaded ? (
            <>
              <CheckCircle2 size={16} className="text-emerald-300" />
              <span>Vault Bundle Exported Successfully!</span>
            </>
          ) : (
            <>
              <Download size={16} />
              <span>Download Complete Cognitive Twin Vault (JSON)</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
