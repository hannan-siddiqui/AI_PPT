"use client";

import React, { useState } from "react";
import { SlidePlan } from "@/types";
import { X, Copy, Check, FileJson } from "lucide-react";

interface PlanModalProps {
  isOpen: boolean;
  onClose: () => void;
  plan: SlidePlan | null;
}

export const PlanModal: React.FC<PlanModalProps> = ({ isOpen, onClose, plan }) => {
  const [copied, setCopied] = useState(false);

  if (!isOpen || !plan) return null;

  const jsonString = JSON.stringify(plan, null, 2);

  const handleCopy = () => {
    navigator.clipboard.writeText(jsonString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs animate-in fade-in">
      <div className="relative w-full max-w-3xl rounded-2xl bg-white border border-zinc-200 shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-200 bg-white">
          <div className="flex items-center gap-2">
            <FileJson className="w-4 h-4 text-zinc-600" />
            <h3 className="text-sm font-bold text-zinc-900">SlideDeckSchema (JSON)</h3>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-100 hover:bg-zinc-200 text-zinc-800 text-xs font-semibold transition cursor-pointer"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5 text-zinc-500" />}
              <span>{copied ? "Copied" : "Copy Schema"}</span>
            </button>
            <button
              type="button"
              onClick={onClose}
              className="p-1.5 rounded-lg hover:bg-zinc-100 text-zinc-500 hover:text-zinc-900 transition cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* JSON Code Viewer */}
        <div className="p-6 overflow-y-auto flex-1 font-mono text-xs text-zinc-800 leading-relaxed bg-zinc-50 selection:bg-zinc-200">
          <pre>{jsonString}</pre>
        </div>
      </div>
    </div>
  );
};
