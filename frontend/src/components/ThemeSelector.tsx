"use client";

import React, { useState } from "react";
import { ThemeConfig } from "@/types";
import { PRESET_THEMES, ExtendedThemeConfig } from "@/constants/themes";
import { Palette, Check, Sliders, Eye, Sparkles } from "lucide-react";

interface ThemeSelectorProps {
  currentTheme: ThemeConfig;
  onThemeChange: (theme: ThemeConfig) => void;
  logoPlacement: "top-right" | "top-left" | "cover-only";
  onLogoPlacementChange: (placement: "top-right" | "top-left" | "cover-only") => void;
  slideCount: string;
  onSlideCountChange: (count: string) => void;
}

export const ThemeSelector: React.FC<ThemeSelectorProps> = ({
  currentTheme,
  onThemeChange,
  logoPlacement,
  onLogoPlacementChange,
  slideCount,
  onSlideCountChange
}) => {
  const [showCustom, setShowCustom] = useState(false);

  const handlePresetSelect = (preset: ExtendedThemeConfig) => {
    setShowCustom(false);
    onThemeChange(preset);
  };

  const handleCustomColorChange = (key: keyof ThemeConfig, val: string) => {
    onThemeChange({
      ...currentTheme,
      [key]: val,
      name: "Custom Brand Theme"
    });
  };

  return (
    <div className="space-y-4">
      {/* Live Miniature Theme Preview Card */}
      <div className="p-3.5 rounded-xl border border-slate-800/90 bg-[#07090E] space-y-2">
        <div className="flex items-center justify-between text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
          <span className="flex items-center gap-1.5">
            <Eye className="w-3.5 h-3.5 text-blue-400" />
            Live Palette Simulation ({currentTheme.name})
          </span>
          <span
            className="text-[10px] px-2 py-0.5 rounded-full font-bold uppercase"
            style={{ backgroundColor: `${currentTheme.accent_color}25`, color: currentTheme.accent_color }}
          >
            Active Theme
          </span>
        </div>

        {/* Mini 16:9 Canvas Simulation */}
        <div
          className="w-full aspect-[21/9] rounded-lg p-3 flex flex-col justify-between border shadow-inner relative overflow-hidden transition-all"
          style={{
            backgroundColor: currentTheme.bg_color,
            color: currentTheme.text_color,
            borderColor: currentTheme.secondary_color
          }}
        >
          {/* Header Line */}
          <div>
            <div className="h-1 w-8 rounded mb-1" style={{ backgroundColor: currentTheme.accent_color }} />
            <div className="text-[8px] font-bold uppercase tracking-wider" style={{ color: currentTheme.accent_color }}>
              EXECUTIVE PREVIEW
            </div>
            <div className="text-xs font-extrabold leading-tight">Boardroom Aesthetic</div>
          </div>

          {/* Mini Cards */}
          <div className="grid grid-cols-3 gap-1.5 my-auto">
            {[
              { val: "$4.8M", lbl: "ARR Growth" },
              { val: "98%", lbl: "NDR Retention" },
              { val: "Top 1%", lbl: "Efficiency" }
            ].map((st, i) => (
              <div
                key={i}
                className="p-1.5 rounded border relative overflow-hidden text-center"
                style={{
                  backgroundColor: currentTheme.card_bg_color,
                  borderColor: currentTheme.secondary_color
                }}
              >
                <div className="text-[10px] font-black leading-tight" style={{ color: currentTheme.accent_color }}>
                  {st.val}
                </div>
                <div className="text-[7px] font-medium opacity-80 truncate">{st.lbl}</div>
              </div>
            ))}
          </div>

          {/* Mini Footer */}
          <div className="flex items-center justify-between text-[7px] opacity-60 pt-1 border-t" style={{ borderColor: currentTheme.secondary_color }}>
            <span>Presentation Deck • Confidential</span>
            <span>16:9 Widescreen</span>
          </div>
        </div>
      </div>

      {/* Preset Theme Cards */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs text-slate-300 font-semibold">
          <span className="flex items-center gap-1.5 uppercase tracking-wider">
            <Palette className="w-3.5 h-3.5 text-blue-400" />
            Curated Executive Themes
          </span>
          <button
            type="button"
            onClick={() => setShowCustom(!showCustom)}
            className="flex items-center gap-1 text-[11px] text-blue-400 hover:text-blue-300 font-medium"
          >
            <Sliders className="w-3 h-3" />
            {showCustom ? "Hide Custom" : "Custom Hex"}
          </button>
        </div>

        <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
          {PRESET_THEMES.map((theme) => {
            const isSelected = currentTheme.name === theme.name && !showCustom;
            return (
              <button
                key={theme.name}
                type="button"
                onClick={() => handlePresetSelect(theme)}
                className={`relative p-2.5 rounded-xl border text-left transition flex flex-col justify-between ${
                  isSelected
                    ? "border-blue-500 bg-blue-500/10 shadow-md shadow-blue-500/10 ring-1 ring-blue-500"
                    : "border-slate-800 bg-slate-900/60 hover:border-slate-700 hover:bg-slate-900"
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold text-white tracking-tight">{theme.name}</span>
                    {isSelected && <Check className="w-3.5 h-3.5 text-blue-400" />}
                  </div>

                  <p className="text-[10px] text-slate-400 mb-2 truncate">{theme.tagline}</p>

                  {/* Swatches */}
                  <div className="flex items-center gap-1">
                    <span
                      className="w-3.5 h-3.5 rounded-full border border-white/20 shadow-sm"
                      style={{ backgroundColor: theme.bg_color }}
                      title="Slide Background"
                    />
                    <span
                      className="w-3.5 h-3.5 rounded-full border border-white/20 shadow-sm"
                      style={{ backgroundColor: theme.card_bg_color }}
                      title="Card Containers"
                    />
                    <span
                      className="w-3.5 h-3.5 rounded-full border border-white/20 shadow-sm"
                      style={{ backgroundColor: theme.accent_color }}
                      title="Primary Accent"
                    />
                    <span
                      className="w-3.5 h-3.5 rounded-full border border-white/20 shadow-sm"
                      style={{ backgroundColor: theme.text_color }}
                      title="Header Text"
                    />
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Custom Color Overrides (if toggled) */}
      {showCustom && (
        <div className="p-3.5 rounded-xl border border-slate-800 bg-slate-900/90 space-y-3">
          <div className="flex items-center gap-2">
            <Sparkles className="w-3.5 h-3.5 text-blue-400" />
            <span className="text-xs font-semibold text-slate-200">Custom Brand Palette</span>
          </div>
          <div className="grid grid-cols-2 gap-2.5 text-xs">
            <div>
              <label className="block text-[10px] text-slate-400 mb-1">Background Hex</label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={currentTheme.bg_color}
                  onChange={(e) => handleCustomColorChange("bg_color", e.target.value)}
                  className="w-6 h-6 rounded border-0 bg-transparent cursor-pointer"
                />
                <input
                  type="text"
                  value={currentTheme.bg_color}
                  onChange={(e) => handleCustomColorChange("bg_color", e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-0.5 text-slate-200 font-mono text-xs"
                />
              </div>
            </div>

            <div>
              <label className="block text-[10px] text-slate-400 mb-1">Accent Highlight Hex</label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={currentTheme.accent_color}
                  onChange={(e) => handleCustomColorChange("accent_color", e.target.value)}
                  className="w-6 h-6 rounded border-0 bg-transparent cursor-pointer"
                />
                <input
                  type="text"
                  value={currentTheme.accent_color}
                  onChange={(e) => handleCustomColorChange("accent_color", e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-0.5 text-slate-200 font-mono text-xs"
                />
              </div>
            </div>

            <div>
              <label className="block text-[10px] text-slate-400 mb-1">Card Container Hex</label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={currentTheme.card_bg_color}
                  onChange={(e) => handleCustomColorChange("card_bg_color", e.target.value)}
                  className="w-6 h-6 rounded border-0 bg-transparent cursor-pointer"
                />
                <input
                  type="text"
                  value={currentTheme.card_bg_color}
                  onChange={(e) => handleCustomColorChange("card_bg_color", e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-0.5 text-slate-200 font-mono text-xs"
                />
              </div>
            </div>

            <div>
              <label className="block text-[10px] text-slate-400 mb-1">Headline Text Hex</label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={currentTheme.text_color}
                  onChange={(e) => handleCustomColorChange("text_color", e.target.value)}
                  className="w-6 h-6 rounded border-0 bg-transparent cursor-pointer"
                />
                <input
                  type="text"
                  value={currentTheme.text_color}
                  onChange={(e) => handleCustomColorChange("text_color", e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-0.5 text-slate-200 font-mono text-xs"
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Logo & Deck Settings */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t border-slate-800/80">
        {/* Logo Placement */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
            Logo Placement
          </label>
          <div className="grid grid-cols-3 gap-1">
            {[
              { id: "top-right", label: "Top Right" },
              { id: "top-left", label: "Top Left" },
              { id: "cover-only", label: "Cover Only" }
            ].map((opt) => (
              <button
                key={opt.id}
                type="button"
                onClick={() => onLogoPlacementChange(opt.id as any)}
                className={`py-1.5 px-1.5 text-[11px] font-medium rounded-lg border transition text-center ${
                  logoPlacement === opt.id
                    ? "border-blue-500 bg-blue-500/15 text-blue-400"
                    : "border-slate-800 bg-slate-900/60 text-slate-400 hover:text-slate-200"
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Target Slide Count */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
            Target Slide Count
          </label>
          <div className="grid grid-cols-5 gap-1">
            {["auto", "4", "6", "8", "10"].map((cnt) => (
              <button
                key={cnt}
                type="button"
                onClick={() => onSlideCountChange(cnt)}
                className={`py-1.5 px-1 text-[11px] font-medium rounded-lg border capitalize transition ${
                  slideCount === cnt
                    ? "border-blue-500 bg-blue-500/15 text-blue-400"
                    : "border-slate-800 bg-slate-900/60 text-slate-400 hover:text-slate-200"
                }`}
              >
                {cnt}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
