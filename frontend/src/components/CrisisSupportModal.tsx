"use client";

import React from "react";
import { Phone, MessageSquare, ShieldAlert, Heart, ExternalLink, X } from "lucide-react";

interface Helpline {
  name: string;
  region: string;
  contact: string;
  type: string;
  action_url?: string;
  web_url?: string;
  description: string;
}

interface CrisisSupportModalProps {
  isOpen: boolean;
  onClose?: () => void;
  crisisData?: {
    title?: string;
    message?: string;
    helplines?: Helpline[];
    immediate_steps?: string[];
  } | null;
}

const DEFAULT_HELPLINES: Helpline[] = [
  {
    name: "988 Suicide & Crisis Lifeline",
    region: "United States & Canada",
    contact: "988",
    type: "call_or_text",
    action_url: "tel:988",
    web_url: "https://988lifeline.org",
    description: "Free, confidential, 24/7 support for anyone in distress or crisis."
  },
  {
    name: "Crisis Text Line",
    region: "US, UK, Canada",
    contact: "Text HOME to 741741",
    type: "text",
    action_url: "sms:741741?body=HOME",
    web_url: "https://www.crisistextline.org",
    description: "Free 24/7 text support with a trained crisis counselor."
  },
  {
    name: "The Trevor Project",
    region: "LGBTQ Youth (US)",
    contact: "1-866-488-7386 or Text START to 678-678",
    type: "call_or_text",
    action_url: "tel:18664887386",
    web_url: "https://www.thetrevorproject.org",
    description: "24/7 confidential crisis intervention and suicide prevention for LGBTQ youth."
  },
  {
    name: "Veterans Crisis Line",
    region: "United States",
    contact: "Dial 988, then press 1",
    type: "call",
    action_url: "tel:988",
    web_url: "https://www.veteranscrisisline.net",
    description: "24/7 confidential crisis line for veterans and their loved ones."
  },
  {
    name: "International Helplines (Find A Helpline)",
    region: "Global (130+ Countries)",
    contact: "findahelpline.com",
    type: "directory",
    action_url: "https://findahelpline.com",
    web_url: "https://findahelpline.com",
    description: "Free, confidential international directory of local crisis centers worldwide."
  }
];

export default function CrisisSupportModal({ isOpen, onClose, crisisData }: CrisisSupportModalProps) {
  if (!isOpen) return null;

  const helplines = crisisData?.helplines || DEFAULT_HELPLINES;
  const message = crisisData?.message || (
    "It sounds like you are going through an overwhelming amount of pain right now. " +
    "Please know you do not have to carry this alone. There are compassionate, " +
    "trained professionals available 24/7 who want to listen and help you through this moment safely."
  );

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="crisis-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-fade-in font-sans"
    >
      <div className="relative w-full max-w-2xl bg-[#0f1422] border-2 border-red-500/80 rounded-3xl p-6 md:p-8 shadow-2xl shadow-red-950/60 text-white max-h-[90vh] overflow-y-auto">
        
        {/* Header */}
        <div className="flex items-start justify-between pb-5 border-b border-red-500/30">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-red-600/20 border border-red-500/40 rounded-2xl text-red-400">
              <ShieldAlert className="w-8 h-8 animate-pulse text-red-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-red-500/30 text-red-200 border border-red-500/40 uppercase tracking-widest">
                  CRISIS PROTOCOL ACTIVE
                </span>
              </div>
              <h2 id="crisis-modal-title" className="text-2xl font-bold text-white tracking-tight mt-1">
                Immediate Human Support & Safety Resources
              </h2>
            </div>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              aria-label="Close crisis resources modal"
              className="p-2 text-gray-300 hover:text-white bg-gray-800/80 rounded-xl transition hover:bg-gray-700/80"
              title="Close"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Empathetic de-escalation message */}
        <div className="my-6 p-4 rounded-2xl bg-red-950/40 border border-red-500/30 text-red-100 text-sm leading-relaxed">
          <p className="font-medium">{message}</p>
          <p className="mt-2 text-xs text-red-300/80 italic">
            Automated cognitive coaching has been suspended. Your immediate safety is the only priority.
          </p>
        </div>

        {/* Primary Lifelines */}
        <div className="space-y-3 mb-6">
          <h3 className="text-xs uppercase tracking-wider font-bold text-gray-400 font-mono">
            Direct Emergency Lifelines (Free, Confidential, 24/7)
          </h3>
          
          <div className="grid gap-3 sm:grid-cols-2">
            {helplines.map((h, i) => (
              <div
                key={i}
                className="p-4 rounded-2xl bg-[#172033] border border-gray-700/60 hover:border-red-500/50 transition flex flex-col justify-between group"
              >
                <div>
                  <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
                    <span className="font-mono text-[11px] text-red-300">{h.region}</span>
                    <span className="text-[10px] uppercase px-1.5 py-0.5 bg-gray-800 rounded">{h.type}</span>
                  </div>
                  <h4 className="font-semibold text-white group-hover:text-red-300 transition text-sm">
                    {h.name}
                  </h4>
                  <p className="text-xs text-gray-400 mt-1 line-clamp-2 leading-relaxed">
                    {h.description}
                  </p>
                </div>

                <div className="mt-4 flex items-center gap-2 pt-3 border-t border-gray-800">
                  {h.action_url && (
                    <a
                      href={h.action_url}
                      className="flex-1 py-2 px-3 bg-red-600 hover:bg-red-500 text-white rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 transition shadow-lg shadow-red-600/20"
                    >
                      {h.type.includes("call") ? <Phone className="w-3.5 h-3.5" /> : <MessageSquare className="w-3.5 h-3.5" />}
                      <span>{h.contact}</span>
                    </a>
                  )}
                  {h.web_url && (
                    <a
                      href={h.web_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-xl text-xs transition"
                      title="Open website"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Immediate Safety Steps */}
        <div className="p-4 rounded-2xl bg-gray-900/60 border border-gray-800 text-xs text-gray-300 space-y-2">
          <h4 className="font-bold text-gray-200 flex items-center gap-1.5 uppercase font-mono text-[11px]">
            <Heart className="w-3.5 h-3.5 text-red-400" />
            <span>Immediate Safety Steps</span>
          </h4>
          <ul className="list-disc pl-4 space-y-1 text-gray-400">
            <li>Reach out to one of the free helplines above right now — you do not need to be in immediate suicide risk to talk.</li>
            <li>If you are in immediate physical danger, call emergency services (911, 999, 112) or go to the nearest emergency room.</li>
            <li>Step away from any objects that could be used for self-harm and connect with someone you trust.</li>
          </ul>
        </div>

        {/* Footer Notice */}
        <div className="mt-6 text-center text-[11px] text-gray-500">
          Psych-AI is an automated cognitive tool, not a crisis responder or licensed healthcare provider.
        </div>
      </div>
    </div>
  );
}
