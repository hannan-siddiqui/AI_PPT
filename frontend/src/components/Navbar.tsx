"use client";

import React, { useEffect, useState } from "react";
import { Sparkles, Layers, Cpu, Eye, CheckCircle2, RotateCcw } from "lucide-react";
import { getApiUrl } from "@/constants/api";

interface NavbarProps {
  onReset?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onReset }) => {
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">("checking");
  const [modelName, setModelName] = useState<string>("nemotron-3-ultra-550b");
  const [visionModel, setVisionModel] = useState<string>("kimi-k3");

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(getApiUrl("/api/health"));
        if (res.ok) {
          const data = await res.json();
          setBackendStatus("online");
          if (data.agent_2_data_instructions) {
            setModelName(data.agent_2_data_instructions.split(" ")[0].replace("nvidia/", ""));
          } else if (data.model) {
            setModelName(data.model.replace("nvidia/", ""));
          }
          if (data.agent_1_vision) {
            setVisionModel(data.agent_1_vision.split(" ")[0].replace("moonshotai/", ""));
          } else if (data.vision_model) {
            setVisionModel(data.vision_model.replace("moonshotai/", ""));
          }
        } else {
          setBackendStatus("offline");
        }
      } catch {
        setBackendStatus("offline");
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-zinc-200/80 bg-white/90 backdrop-blur-md px-6 py-3.5 flex items-center justify-between transition-all">
      {/* Brand */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-zinc-950 flex items-center justify-center shadow-xs">
          <Layers className="w-4 h-4 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-base font-bold tracking-tight text-zinc-950">SlideCraft</h1>
            <span className="text-[10px] font-mono uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-zinc-100 text-zinc-600 border border-zinc-200">
              v1.0
            </span>
          </div>
        </div>
      </div>

      {/* Center / Model Badges */}
      <div className="hidden md:flex items-center gap-2 text-xs font-mono">
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-zinc-50 border border-zinc-200 text-zinc-600">
          <Eye className="w-3 h-3 text-zinc-500" />
          <span>OCR: {visionModel}</span>
        </div>
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-zinc-50 border border-zinc-200 text-zinc-600">
          <Cpu className="w-3 h-3 text-zinc-500" />
          <span>LLM: {modelName}</span>
        </div>
      </div>

      {/* Right Status */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 text-xs font-medium px-3 py-1 rounded-full bg-zinc-50 border border-zinc-200 text-zinc-600">
          <span
            className={`w-2 h-2 rounded-full ${
              backendStatus === "online"
                ? "bg-emerald-500"
                : backendStatus === "checking"
                ? "bg-amber-400 animate-pulse"
                : "bg-rose-500"
            }`}
          />
          <span className="text-[11px] font-mono text-zinc-600">
            {backendStatus === "online" ? "System Ready" : backendStatus}
          </span>
        </div>

        {onReset && (
          <button
            type="button"
            onClick={onReset}
            className="p-1.5 rounded-lg text-zinc-500 hover:text-zinc-950 hover:bg-zinc-100 transition cursor-pointer"
            title="Reset to default sample"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        )}
      </div>
    </header>
  );
};
