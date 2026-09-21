"use client";

import React, { useState } from "react";
import {
  Check,
  Copy,
  Code2,
  AlertTriangle,
  Wand2,
  Trash2,
  BarChart3,
  TrendingUp,
  Rocket,
  Compass,
  FileCode
} from "lucide-react";

interface JsonEditorProps {
  value: string;
  onChange: (val: string) => void;
  isValid: boolean;
  validationError: string | null;
  onSelectTemplate: (key: string) => void;
  templates: Record<string, { name: string; description: string }>;
}

export const JsonEditor: React.FC<JsonEditorProps> = ({
  value,
  onChange,
  isValid,
  validationError,
  onSelectTemplate,
  templates
}) => {
  const [copied, setCopied] = useState(false);
  const [activePreset, setActivePreset] = useState<string>("mckinsey_boardroom");

  const handleCopy = () => {
    navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleFormat = () => {
    try {
      const parsed = JSON.parse(value);
      onChange(JSON.stringify(parsed, null, 2));
    } catch {
      // ignore
    }
  };

  const handleClear = () => {
    onChange("{\n  \n}");
  };

  const presets = [
    {
      key: "mckinsey_boardroom",
      name: "McKinsey Board",
      tag: "3 Charts",
      icon: BarChart3,
      accent: "from-blue-500/20 to-cyan-500/20",
      border: "hover:border-cyan-500/50"
    },
    {
      key: "pitch_deck",
      name: "Pitch Deck",
      tag: "Series A",
      icon: Rocket,
      accent: "from-purple-500/20 to-indigo-500/20",
      border: "hover:border-purple-500/50"
    },
    {
      key: "qbr",
      name: "QBR Review",
      tag: "Corporate",
      icon: TrendingUp,
      accent: "from-emerald-500/20 to-teal-500/20",
      border: "hover:border-emerald-500/50"
    },
    {
      key: "product_launch",
      name: "GTM Launch",
      tag: "Strategy",
      icon: Compass,
      accent: "from-amber-500/20 to-orange-500/20",
      border: "hover:border-amber-500/50"
    }
  ];

  return (
    <div className="flex flex-col h-full space-y-3.5">
      {/* Top Header & Action Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
            <FileCode className="w-3.5 h-3.5 text-cyan-400" />
          </div>
          <span className="text-xs font-bold text-slate-200 tracking-wide uppercase">
            Structured Business Data
          </span>
          {isValid ? (
            <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/25">
              <Check className="w-3 h-3" /> Valid JSON
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded-full border border-rose-500/30">
              <AlertTriangle className="w-3 h-3" /> Syntax Error
            </span>
          )}
        </div>

        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={handleFormat}
            disabled={!isValid}
            className="flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded-lg bg-[#11172A] hover:bg-[#1A2340] border border-white/[0.08] hover:border-cyan-500/40 text-slate-300 hover:text-white transition disabled:opacity-40 disabled:cursor-not-allowed shadow-sm"
            title="Prettify JSON indentation"
          >
            <Wand2 className="w-3 h-3 text-cyan-400" />
            <span>Format</span>
          </button>
          <button
            type="button"
            onClick={handleCopy}
            className="flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded-lg bg-[#11172A] hover:bg-[#1A2340] border border-white/[0.08] hover:border-cyan-500/40 text-slate-300 hover:text-white transition shadow-sm"
            title="Copy JSON to clipboard"
          >
            {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3 text-slate-400" />}
            <span>{copied ? "Copied" : "Copy"}</span>
          </button>
          <button
            type="button"
            onClick={handleClear}
            className="p-1.5 rounded-lg bg-[#11172A] hover:bg-rose-500/15 border border-white/[0.08] hover:border-rose-500/40 text-slate-400 hover:text-rose-400 transition"
            title="Clear editor"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Preset Cards Selector */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {presets.map((item) => {
          const Icon = item.icon;
          const isSelected = activePreset === item.key;
          return (
            <button
              key={item.key}
              type="button"
              onClick={() => {
                setActivePreset(item.key);
                onSelectTemplate(item.key);
              }}
              className={`relative p-2.5 rounded-xl border text-left transition-all flex flex-col justify-between group cursor-pointer ${
                isSelected
                  ? "bg-gradient-to-b from-[#16213E] to-[#0E1528] border-cyan-500/60 shadow-[0_0_15px_rgba(6,182,212,0.15)] ring-1 ring-cyan-500/40"
                  : "bg-[#090D18]/90 border-white/[0.06] hover:bg-[#0E1526] hover:border-white/[0.15]"
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <div className={`w-6 h-6 rounded-md flex items-center justify-center bg-gradient-to-tr ${item.accent} border border-white/[0.08]`}>
                  <Icon className="w-3.5 h-3.5 text-cyan-300" />
                </div>
                <span className="text-[9px] px-1.5 py-0.2 rounded-full font-mono font-bold bg-white/[0.06] text-slate-300">
                  {item.tag}
                </span>
              </div>
              <div className="text-[11px] font-bold text-slate-200 group-hover:text-white truncate">
                {item.name}
              </div>
            </button>
          );
        })}
      </div>

      {/* Code Editor Container */}
      <div className="relative flex-1 min-h-[310px] rounded-2xl border border-white/[0.08] bg-[#05070E] overflow-hidden focus-within:border-cyan-500/50 focus-within:ring-1 focus-within:ring-cyan-500/30 transition-all shadow-2xl flex flex-col">
        {/* Editor Top Status Bar */}
        <div className="px-3 py-1.5 bg-[#090D1A] border-b border-white/[0.06] flex items-center justify-between text-[10px] font-mono text-slate-400">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400/80" />
            <span>payload.json</span>
          </div>
          <div className="flex items-center gap-3">
            <span>UTF-8</span>
            <span>JSON Mode</span>
          </div>
        </div>

        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Paste or write your structured JSON data here..."
          spellCheck={false}
          className="w-full flex-1 p-3.5 font-mono text-xs text-slate-200 bg-transparent resize-none focus:outline-none leading-relaxed selection:bg-blue-600/40"
        />
      </div>

      {/* Validation Error Banner */}
      {validationError && (
        <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs font-mono break-all flex items-start gap-2 animate-in fade-in duration-200">
          <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
          <span>{validationError}</span>
        </div>
      )}
    </div>
  );
};
