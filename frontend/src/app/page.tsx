"use client";

import React, { useState, useEffect, useRef } from "react";
import { Navbar } from "@/components/Navbar";
import { SlidePreview } from "@/components/SlidePreview";
import { PlanModal } from "@/components/PlanModal";
import {
  ThemeConfig,
  UploadedImage,
  GeneratePptResponse,
  JobStatusResponse
} from "@/types";
import {
  Upload,
  X,
  Copy,
  Check,
  Code2,
  Sparkles,
  Loader2,
  AlertCircle,
  Terminal,
  ChevronDown,
  ChevronUp,
  Image as ImageIcon,
  MessageSquare,
  Wand2,
  FileText,
  TrendingUp,
  BarChart3,
  Layers,
  ArrowRight,
  SlidersHorizontal
} from "lucide-react";
import { getApiUrl } from "@/constants/api";

const DEFAULT_THEME: ThemeConfig = {
  name: "Clean Executive Light",
  primary_color: "#18181B",
  secondary_color: "#F4F4F5",
  accent_color: "#09090B",
  bg_color: "#FFFFFF",
  text_color: "#09090B",
  card_bg_color: "#F4F4F5",
  muted_text_color: "#71717A",
  heading_color: "#1D4ED8",
  subheading_color: "#0284C7"
};

const DEFAULT_JSON = JSON.stringify(
  {
    company: "NexusAI Cloud",
    executive_summary: "Enterprise multi-agent autonomous presentation engine.",
    metrics: [
      { label: "ARR", value: "$12.8M" },
      { label: "YoY Growth", value: "+148%" },
      { label: "Net Retention", value: "134%" }
    ],
    highlights: [
      "Sub-100ms distributed multimodal inference",
      "Defensible enterprise workflow integrations",
      "Zero token starvation architecture"
    ]
  },
  null,
  2
);

export default function Home() {
  // Context state
  const [activeContextTab, setActiveContextTab] = useState<"json" | "media">("json");
  const [jsonData, setJsonData] = useState<string>(DEFAULT_JSON);
  const [isJsonValid, setIsJsonValid] = useState<boolean>(true);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [copiedJson, setCopiedJson] = useState<boolean>(false);

  // Images state
  const [images, setImages] = useState<UploadedImage[]>([]);
  const [logoId, setLogoId] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Prompt / Chat state
  const [prompt, setPrompt] = useState<string>(
    "Create a publication-grade McKinsey boardroom presentation. Emphasize traction metrics, defensible unit economics, and 18-month strategic horizons."
  );

  // Pipeline state
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [generationProgress, setGenerationProgress] = useState<number>(0);
  const [generationStep, setGenerationStep] = useState<string>("");
  const [agentLogs, setAgentLogs] = useState<string[]>([]);
  const [showLogs, setShowLogs] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [generatedResult, setGeneratedResult] = useState<GeneratePptResponse | null>(null);
  const [isPlanModalOpen, setIsPlanModalOpen] = useState<boolean>(false);

  const logsEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll logs
  useEffect(() => {
    if (logsEndRef.current && showLogs) {
      logsEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [agentLogs, showLogs]);

  // Validate JSON
  const handleJsonChange = (val: string) => {
    setJsonData(val);
    try {
      JSON.parse(val);
      setIsJsonValid(true);
      setValidationError(null);
    } catch (e: any) {
      setIsJsonValid(false);
      setValidationError(e.message);
    }
  };

  const handleFormatJson = () => {
    try {
      const parsed = JSON.parse(jsonData);
      setJsonData(JSON.stringify(parsed, null, 2));
      setIsJsonValid(true);
      setValidationError(null);
    } catch {
      // ignore
    }
  };

  const handleCopyJson = () => {
    navigator.clipboard.writeText(jsonData);
    setCopiedJson(true);
    setTimeout(() => setCopiedJson(false), 2000);
  };

  // Upload Images
  const handleUploadFiles = async (files: FileList | File[]) => {
    if (!files || files.length === 0) return;
    setIsUploading(true);
    const formData = new FormData();
    Array.from(files).forEach((file) => formData.append("images", file));

    try {
      const res = await fetch(getApiUrl("/api/upload-images"), {
        method: "POST",
        body: formData
      });

      if (res.ok) {
        const data = await res.json();
        if (data.images && data.images.length > 0) {
          const newImgs: UploadedImage[] = data.images.map((img: UploadedImage, idx: number) => ({
            ...img,
            file: Array.from(files)[idx] || undefined
          }));
          const combined = [...images, ...newImgs];
          setImages(combined);

          if (!logoId) {
            const possibleLogo = combined.find((i) => i.role === "logo" || i.original_name.toLowerCase().includes("logo"));
            if (possibleLogo) setLogoId(possibleLogo.id);
          }
        }
      }
    } catch (err) {
      console.error("Image upload failed:", err);
    } finally {
      setIsUploading(false);
    }
  };

  const handleRemoveImage = (id: string) => {
    setImages(images.filter((img) => img.id !== id));
    if (logoId === id) setLogoId(null);
  };

  const handleToggleLogo = (id: string) => {
    setLogoId(logoId === id ? null : id);
  };

  // Demo asset generator
  const addSampleAsset = (type: "logo" | "chart") => {
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    if (type === "logo") {
      canvas.width = 400;
      canvas.height = 100;
      ctx.fillStyle = "#09090B";
      ctx.fillRect(0, 0, 400, 100);
      ctx.fillStyle = "#FFFFFF";
      ctx.font = "bold 32px sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("NEXUS AI", 200, 50);
    } else {
      canvas.width = 600;
      canvas.height = 400;
      ctx.fillStyle = "#F4F4F5";
      ctx.fillRect(0, 0, 600, 400);

      const colors = ["#71717A", "#52525B", "#27272A", "#09090B"];
      const heights = [120, 210, 290, 340];
      const labels = ["2023", "2024", "2025", "2026E"];

      ctx.font = "bold 20px sans-serif";
      ctx.fillStyle = "#09090B";
      ctx.fillText("ARR Trajectory ($M)", 40, 45);

      for (let i = 0; i < 4; i++) {
        const x = 70 + i * 130;
        const h = heights[i];
        const y = 340 - h;
        ctx.fillStyle = colors[i];
        ctx.fillRect(x, y, 80, h);
        ctx.fillStyle = "#52525B";
        ctx.font = "14px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(labels[i], x + 40, 370);
      }
    }

    canvas.toBlob((blob) => {
      if (blob) {
        const filename = type === "logo" ? "company_logo.png" : "revenue_trajectory_chart.png";
        const file = new File([blob], filename, { type: "image/png" });
        handleUploadFiles([file]);
      }
    }, "image/png");
  };

  // Quick Preset Loader
  const loadPreset = (type: "boardroom" | "pitch" | "qbr") => {
    if (type === "boardroom") {
      setPrompt("You are a senior partner at McKinsey & Company preparing an 8-slide presentation for a Board of Directors meeting. Focus on high-impact visuals, defensible technology moats, unit economics, and 18-month strategic horizons.");
      setJsonData(JSON.stringify({
        company: "NexusAI Cloud",
        executive_summary: "Enterprise multi-agent autonomous presentation engine.",
        metrics: [
          { label: "ARR", value: "$12.8M" },
          { label: "YoY Growth", value: "+148%" },
          { label: "Net Retention", value: "134%" }
        ],
        market_opportunity: {
          tam: "$140B Enterprise Automation",
          sam: "$42B Multi-Agent Systems"
        }
      }, null, 2));
    } else if (type === "pitch") {
      setPrompt("Create a persuasive Series A pitch deck emphasizing hypergrowth traction, enterprise retention, low CAC/LTV, and market dominance.");
      setJsonData(JSON.stringify({
        company: "NexusAI",
        funding_target: "$12M Series A",
        metrics: [
          { label: "Annual Run Rate", value: "$8.5M" },
          { label: "MoM Growth", value: "18.4%" },
          { label: "Gross Margin", value: "84%" }
        ]
      }, null, 2));
    } else {
      setPrompt("Executive quarterly review (QBR) highlighting record revenue, operational discipline, and next quarter key strategic priorities.");
      setJsonData(JSON.stringify({
        company: "NexusAI",
        period: "Q3 2026",
        metrics: [
          { label: "Quarterly Revenue", value: "$3.4M" },
          { label: "EBITDA Margin", value: "28%" },
          { label: "Customer Expansion", value: "+44%" }
        ]
      }, null, 2));
    }
  };

  // Generate Presentation
  const handleGenerate = async () => {
    if (!isJsonValid) {
      setErrorMsg("Please fix JSON syntax errors before generating.");
      return;
    }

    setErrorMsg(null);
    setIsGenerating(true);
    setGenerationProgress(5);
    setGenerationStep("Ingesting data, images, and prompt directives...");
    setAgentLogs(["[INGEST] Packaging multipart payload with prompt, JSON data, and uploaded media..."]);

    try {
      let themeToUse = DEFAULT_THEME;
      let slideCountToUse = "auto";
      try {
        const parsed = JSON.parse(jsonData);
        if (parsed.theme) {
          if (typeof parsed.theme === "object") {
            themeToUse = parsed.theme;
          } else if (typeof parsed.theme === "string" && parsed.theme.toLowerCase().includes("mint")) {
            themeToUse = {
              name: "Executive Mint Blue",
              primary_color: "#0F766E",
              secondary_color: "#E6FFFA",
              accent_color: "#0D9488",
              bg_color: "#FFFFFF",
              text_color: "#0F172A",
              card_bg_color: "#F0FDFA",
              muted_text_color: "#5A7184",
              heading_color: "#0F766E",
              subheading_color: "#0D9488"
            };
          }
        }
        if (parsed.n_slides) {
          slideCountToUse = String(parsed.n_slides);
        }
      } catch (e) {
        // ignore parse error here
      }

      const formData = new FormData();
      formData.append("json_data", jsonData);
      formData.append("prompt", prompt);
      formData.append("slide_count", slideCountToUse);
      formData.append("theme", JSON.stringify(themeToUse));
      formData.append("logo_config", JSON.stringify({ image_id: logoId, placement: "top-right" }));
      formData.append("existing_images", JSON.stringify(images));

      images.forEach((img) => {
        if (img.file) {
          formData.append("images", img.file, img.original_name);
        }
      });

      const res = await fetch(getApiUrl("/api/generate-ppt?async=true"), {
        method: "POST",
        body: formData
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.error || "Failed to initiate presentation generation");
      }

      const initData = await res.json();
      const currentJobId = initData.job_id;
      setGenerationProgress(initData.progress || 10);
      setGenerationStep(initData.step || "Job queued in orchestration worker...");

      // Poll until completion
      await new Promise<void>((resolve, reject) => {
        const intervalId = setInterval(async () => {
          try {
            const pollRes = await fetch(getApiUrl(`/api/jobs/${currentJobId}`));
            if (!pollRes.ok) throw new Error("Failed to poll generation status");
            const jobData: JobStatusResponse = await pollRes.json();

            setGenerationProgress(jobData.progress || 10);
            setGenerationStep(jobData.step || "Processing...");

            if (jobData.logs && jobData.logs.length > 0) {
              setAgentLogs(jobData.logs);
            }

            if (jobData.status === "completed") {
              clearInterval(intervalId);
              if (jobData.result) {
                setGeneratedResult(jobData.result);
                if (jobData.result.logs && jobData.result.logs.length > 0) {
                  setAgentLogs(jobData.result.logs);
                }
                if (jobData.result.images && jobData.result.images.length > 0) {
                  setImages((prev) => {
                    const existingIds = new Set(prev.map((img) => img.id));
                    const newImgs = jobData.result!.images!.filter((img) => !existingIds.has(img.id));
                    return [...prev, ...newImgs];
                  });
                }
              }
              resolve();
            } else if (jobData.status === "failed") {
              clearInterval(intervalId);
              reject(new Error(jobData.error || "Generation pipeline failed"));
            }
          } catch (err) {
            clearInterval(intervalId);
            reject(err);
          }
        }, 1200);
      });
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || "An unexpected error occurred during generation.");
    } finally {
      setIsGenerating(false);
    }
  };

  // Shortcut Cmd/Ctrl + Enter to generate
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      if (!isGenerating && isJsonValid) {
        handleGenerate();
      }
    }
  };

  return (
    <div className="min-h-screen bg-white text-zinc-900 flex flex-col font-sans selection:bg-zinc-200">
      <Navbar onReset={() => loadPreset("boardroom")} />

      <main className="flex-1 w-full max-w-7xl mx-auto p-4 sm:p-6 lg:p-8 grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8">
        {/* LEFT COLUMN: Restructured Studio Workspace (5 cols) */}
        <div className="lg:col-span-5 flex flex-col space-y-5">
          {/* Card 1: Context Attachments (Data JSON + Media Images segmented switcher) */}
          <div className="p-4 sm:p-5 rounded-2xl bg-white border border-zinc-200 shadow-xs flex flex-col space-y-3.5">
            <div className="flex items-center justify-between pb-3 border-b border-zinc-100">
              {/* Segmented Switcher */}
              <div className="flex items-center p-1 bg-zinc-100 rounded-xl">
                <button
                  type="button"
                  onClick={() => setActiveContextTab("json")}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
                    activeContextTab === "json"
                      ? "bg-white text-zinc-950 shadow-xs"
                      : "text-zinc-600 hover:text-zinc-950"
                  }`}
                >
                  <Code2 className="w-3.5 h-3.5" />
                  <span>Data JSON</span>
                  <span className={`text-[10px] font-mono px-1 rounded ${isJsonValid ? "text-emerald-700 bg-emerald-50" : "text-rose-700 bg-rose-50"}`}>
                    {isJsonValid ? "valid" : "error"}
                  </span>
                </button>

                <button
                  type="button"
                  onClick={() => setActiveContextTab("media")}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
                    activeContextTab === "media"
                      ? "bg-white text-zinc-950 shadow-xs"
                      : "text-zinc-600 hover:text-zinc-950"
                  }`}
                >
                  <ImageIcon className="w-3.5 h-3.5" />
                  <span>Images</span>
                  {images.length > 0 && (
                    <span className="text-[10px] font-mono px-1.5 py-0.2 rounded-full bg-zinc-200 text-zinc-800">
                      {images.length}
                    </span>
                  )}
                </button>
              </div>

              {/* Action utilities */}
              {activeContextTab === "json" ? (
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={handleFormatJson}
                    disabled={!isJsonValid}
                    className="text-xs text-zinc-500 hover:text-zinc-950 transition flex items-center gap-1 cursor-pointer disabled:opacity-30"
                    title="Prettify JSON"
                  >
                    <Wand2 className="w-3 h-3" />
                    <span>Format</span>
                  </button>
                  <span className="text-zinc-300">•</span>
                  <button
                    type="button"
                    onClick={handleCopyJson}
                    className="text-xs text-zinc-500 hover:text-zinc-950 transition flex items-center gap-1 cursor-pointer"
                    title="Copy JSON"
                  >
                    {copiedJson ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
                    <span>{copiedJson ? "Copied" : "Copy"}</span>
                  </button>
                </div>
              ) : (
                <div className="flex items-center gap-1.5">
                  <button
                    type="button"
                    onClick={() => addSampleAsset("logo")}
                    className="text-[11px] font-medium px-2 py-0.5 rounded-md bg-zinc-100 hover:bg-zinc-200 text-zinc-700 transition cursor-pointer"
                  >
                    + Logo
                  </button>
                  <button
                    type="button"
                    onClick={() => addSampleAsset("chart")}
                    className="text-[11px] font-medium px-2 py-0.5 rounded-md bg-zinc-100 hover:bg-zinc-200 text-zinc-700 transition cursor-pointer"
                  >
                    + Chart
                  </button>
                </div>
              )}
            </div>

            {/* Content Area */}
            {activeContextTab === "json" ? (
              <div className="space-y-2">
                <textarea
                  value={jsonData}
                  onChange={(e) => handleJsonChange(e.target.value)}
                  placeholder="Paste structured business JSON data here..."
                  spellCheck={false}
                  rows={9}
                  className="w-full p-3 font-mono text-xs text-zinc-900 bg-zinc-50 border border-zinc-200 rounded-xl focus:border-zinc-950 focus:bg-white focus:outline-none leading-relaxed resize-y transition"
                />
                {validationError && (
                  <p className="text-[11px] text-rose-600 font-mono">{validationError}</p>
                )}

                {/* Quick Presets row */}
                <div className="flex items-center gap-2 pt-1">
                  <span className="text-[11px] font-medium text-zinc-400">Load sample:</span>
                  <button
                    type="button"
                    onClick={() => loadPreset("boardroom")}
                    className="text-[11px] font-semibold text-zinc-600 hover:text-zinc-950 underline decoration-zinc-300 underline-offset-2 cursor-pointer"
                  >
                    McKinsey Board
                  </button>
                  <span className="text-zinc-300">•</span>
                  <button
                    type="button"
                    onClick={() => loadPreset("pitch")}
                    className="text-[11px] font-semibold text-zinc-600 hover:text-zinc-950 underline decoration-zinc-300 underline-offset-2 cursor-pointer"
                  >
                    Series A Pitch
                  </button>
                  <span className="text-zinc-300">•</span>
                  <button
                    type="button"
                    onClick={() => loadPreset("qbr")}
                    className="text-[11px] font-semibold text-zinc-600 hover:text-zinc-950 underline decoration-zinc-300 underline-offset-2 cursor-pointer"
                  >
                    QBR Review
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept="image/*"
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files) handleUploadFiles(e.target.files);
                  }}
                />

                {/* Drag and Drop Box */}
                <div
                  onClick={() => fileInputRef.current?.click()}
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={(e) => {
                    e.preventDefault();
                    if (e.dataTransfer.files) handleUploadFiles(e.dataTransfer.files);
                  }}
                  className="border border-dashed border-zinc-300 hover:border-zinc-500 bg-zinc-50 hover:bg-zinc-100/70 p-5 rounded-xl text-center cursor-pointer transition flex flex-col items-center justify-center gap-2 group"
                >
                  {isUploading ? (
                    <div className="flex items-center gap-2 text-zinc-600 py-1">
                      <Loader2 className="w-4 h-4 animate-spin text-zinc-900" />
                      <span className="text-xs font-medium">Uploading images...</span>
                    </div>
                  ) : (
                    <>
                      <div className="w-8 h-8 rounded-full bg-white border border-zinc-200 flex items-center justify-center text-zinc-600 shadow-xs">
                        <Upload className="w-4 h-4" />
                      </div>
                      <div>
                        <p className="text-xs font-semibold text-zinc-800">
                          Click or drag & drop images
                        </p>
                        <p className="text-[11px] text-zinc-500 mt-0.5">
                          Logos, financial charts, product screenshots, diagrams
                        </p>
                      </div>
                    </>
                  )}
                </div>

                {/* Thumbnail list */}
                {images.length > 0 && (
                  <div className="space-y-2 max-h-44 overflow-y-auto pr-1">
                    {images.map((img) => (
                      <div
                        key={img.id}
                        className="flex items-center justify-between p-2 rounded-lg bg-zinc-50 border border-zinc-200 text-xs"
                      >
                        <div className="flex items-center gap-2.5 min-w-0">
                          <div className="w-8 h-8 rounded bg-white overflow-hidden flex items-center justify-center shrink-0 border border-zinc-200">
                            <img
                              src={getApiUrl(img.url)}
                              alt={img.original_name}
                              className="w-full h-full object-contain"
                              onError={(e) => ((e.target as HTMLElement).style.display = "none")}
                            />
                          </div>
                          <div className="min-w-0">
                            <p className="text-xs font-semibold text-zinc-800 truncate">{img.original_name}</p>
                            <p className="text-[10px] text-zinc-500 font-mono">{img.role}</p>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <button
                            type="button"
                            onClick={() => handleToggleLogo(img.id)}
                            className={`text-[10px] font-semibold px-2 py-0.5 rounded cursor-pointer transition ${
                              logoId === img.id
                                ? "bg-zinc-950 text-white"
                                : "bg-white text-zinc-600 hover:text-zinc-950 border border-zinc-200"
                            }`}
                          >
                            {logoId === img.id ? "Logo" : "Set Logo"}
                          </button>
                          <button
                            type="button"
                            onClick={() => handleRemoveImage(img.id)}
                            className="p-1 text-zinc-400 hover:text-zinc-900 transition cursor-pointer"
                          >
                            <X className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Card 2: Command & Chat Instructions Hub */}
          <div className="p-4 sm:p-5 rounded-2xl bg-white border border-zinc-200 shadow-xs flex flex-col space-y-3.5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-zinc-700" />
                <span className="text-xs font-bold uppercase tracking-wider text-zinc-900">
                  Instructions & Prompt
                </span>
              </div>
              <span className="text-[11px] font-mono text-zinc-500">⌘ + Enter to generate</span>
            </div>

            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={4}
              placeholder="Specify presentation requirements, tone, target audience, slide count, or narrative structure..."
              className="w-full p-3 font-sans text-xs text-zinc-900 bg-zinc-50 border border-zinc-200 rounded-xl focus:border-zinc-950 focus:bg-white focus:outline-none leading-relaxed resize-y transition"
            />

            {/* Quick Directive Pills */}
            <div className="flex flex-wrap gap-1.5 pt-0.5">
              {[
                "+ Highlight ARR Growth",
                "+ McKinsey Style",
                "+ 18-Month Horizons",
                "+ Detail Moats"
              ].map((pill) => (
                <button
                  key={pill}
                  type="button"
                  onClick={() => setPrompt((prev) => (prev ? `${prev.trim()} ${pill.replace("+ ", "")}.` : `${pill.replace("+ ", "")}.`))}
                  className="text-[11px] font-medium px-2 py-0.5 rounded-md bg-zinc-100 hover:bg-zinc-200 text-zinc-700 hover:text-zinc-950 transition cursor-pointer border border-zinc-200"
                >
                  {pill}
                </button>
              ))}
            </div>

            {errorMsg && (
              <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            {/* MASTER CTA BUTTON */}
            <button
              type="button"
              onClick={handleGenerate}
              disabled={isGenerating || !isJsonValid}
              className="w-full py-3.5 px-4 rounded-xl bg-zinc-950 hover:bg-zinc-800 text-white font-bold text-xs tracking-wide transition flex items-center justify-between shadow-xs disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer"
            >
              <div className="flex items-center gap-2">
                {isGenerating ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin text-white" />
                    <span>Synthesizing Presentation...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 text-white" />
                    <span>Generate Presentation (.PPTX)</span>
                  </>
                )}
              </div>
              <span className="text-[11px] font-mono font-medium opacity-80">16:9 HD</span>
            </button>

            {/* Generating Progress Indicator */}
            {isGenerating && (
              <div className="p-3.5 rounded-xl bg-zinc-50 border border-zinc-200 space-y-2">
                <div className="flex items-center justify-between text-xs font-mono text-zinc-600">
                  <span className="truncate max-w-[80%]">{generationStep}</span>
                  <span className="text-zinc-900 font-bold">{generationProgress}%</span>
                </div>
                <div className="w-full bg-zinc-200 rounded-full h-1.5 overflow-hidden">
                  <div
                    className="bg-zinc-950 h-full rounded-full transition-all duration-300"
                    style={{ width: `${Math.max(5, generationProgress)}%` }}
                  />
                </div>
              </div>
            )}

            {/* Collapsible Execution Logs */}
            {agentLogs.length > 0 && (
              <div className="pt-1">
                <button
                  type="button"
                  onClick={() => setShowLogs(!showLogs)}
                  className="flex items-center justify-between w-full text-[11px] font-mono text-zinc-500 hover:text-zinc-900 transition py-1 cursor-pointer"
                >
                  <span className="flex items-center gap-1.5">
                    <Terminal className="w-3.5 h-3.5" />
                    <span>LangGraph Agent Telemetry ({agentLogs.length})</span>
                  </span>
                  {showLogs ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                </button>

                {showLogs && (
                  <div className="mt-2 p-3 bg-zinc-950 rounded-xl border border-zinc-900 font-mono text-[11px] max-h-48 overflow-y-auto space-y-1 text-zinc-400">
                    {agentLogs.map((log, idx) => (
                      <div key={idx} className="flex items-start gap-2 leading-relaxed">
                        <span className="text-zinc-600 select-none shrink-0 font-mono">
                          {String(idx + 1).padStart(2, "0")}
                        </span>
                        <span className="break-words text-zinc-200">{log}</span>
                      </div>
                    ))}
                    <div ref={logsEndRef} />
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* RIGHT COLUMN: Presentation Preview Stage (7 cols) */}
        <div className="lg:col-span-7 flex flex-col space-y-4">
          {generatedResult ? (
            <SlidePreview
              plan={generatedResult.plan}
              downloadUrl={generatedResult.download_url}
              filename={generatedResult.filename}
              images={images}
              logoId={logoId}
              logoPlacement="top-right"
              qaReport={generatedResult.qa_report}
              onOpenPlanModal={() => setIsPlanModalOpen(true)}
            />
          ) : (
            /* Clean Light Presentation Preview Stage */
            <div className="p-6 sm:p-8 rounded-2xl bg-white border border-zinc-200 shadow-xs flex flex-col justify-between h-full min-h-[560px]">
              {/* Top Stage Bar */}
              <div className="flex items-center justify-between pb-4 border-b border-zinc-100">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-zinc-950" />
                  <span className="text-xs font-bold uppercase tracking-wider text-zinc-800">
                    Presentation Preview
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-zinc-100 text-zinc-600 border border-zinc-200">
                    16:9 Widescreen
                  </span>
                </div>
                <span className="text-xs text-zinc-400">PowerPoint Native (.pptx)</span>
              </div>

              {/* 16:9 Slide Canvas Simulation */}
              <div className="my-6 w-full aspect-[16/9] rounded-xl p-6 sm:p-8 flex flex-col justify-between border border-zinc-200 bg-zinc-50 shadow-xs relative overflow-hidden">
                {/* Simulated Slide Header */}
                <div className="flex items-start justify-between">
                  <div className="space-y-1 max-w-[80%]">
                    <div className="text-[10px] font-bold font-mono uppercase tracking-widest text-zinc-500">
                      Executive Briefing • Boardroom Review
                    </div>
                    <h2 className="text-sm sm:text-xl font-extrabold text-zinc-950 tracking-tight leading-snug">
                      Autonomous Multi-Agent Systems For Enterprise Decision-Making
                    </h2>
                    <p className="text-[10px] sm:text-xs text-zinc-500 font-medium">
                      Enterprise Cohort Growth, Low Latency Inference & Defensible Platform Moats
                    </p>
                  </div>

                  <div className="px-2.5 py-1 rounded-lg bg-white border border-zinc-200 text-right shrink-0">
                    <span className="text-[10px] sm:text-xs font-bold tracking-wider text-zinc-900">NEXUS AI</span>
                  </div>
                </div>

                {/* 3 Metric Cards + Trajectory Chart */}
                <div className="grid grid-cols-1 sm:grid-cols-4 gap-2.5 my-auto">
                  <div className="p-3 rounded-lg bg-white border border-zinc-200 text-left">
                    <span className="text-[9px] font-semibold uppercase text-zinc-500 block mb-0.5">
                      Annual Run Rate
                    </span>
                    <div className="text-base sm:text-xl font-bold font-mono text-zinc-950">
                      $12.8M
                    </div>
                    <span className="text-[9px] font-semibold text-emerald-600 flex items-center gap-0.5 mt-0.5">
                      <TrendingUp className="w-2.5 h-2.5" /> +148% YoY
                    </span>
                  </div>

                  <div className="p-3 rounded-lg bg-white border border-zinc-200 text-left">
                    <span className="text-[9px] font-semibold uppercase text-zinc-500 block mb-0.5">
                      Net Retention
                    </span>
                    <div className="text-base sm:text-xl font-bold font-mono text-zinc-950">
                      134%
                    </div>
                    <span className="text-[9px] text-zinc-500 block mt-0.5">
                      Tier-1 Accounts
                    </span>
                  </div>

                  <div className="p-3 rounded-lg bg-white border border-zinc-200 text-left">
                    <span className="text-[9px] font-semibold uppercase text-zinc-500 block mb-0.5">
                      Inference Speed
                    </span>
                    <div className="text-base sm:text-xl font-bold font-mono text-zinc-950">
                      &lt;120ms
                    </div>
                    <span className="text-[9px] text-zinc-500 block mt-0.5">
                      Zero Token Latency
                    </span>
                  </div>

                  <div className="p-3 rounded-lg bg-white border border-zinc-200 flex flex-col justify-between">
                    <span className="text-[9px] font-semibold uppercase text-zinc-500 block mb-0.5">
                      Revenue Curve
                    </span>
                    <div className="flex items-end justify-between gap-1.5 h-8 pt-1">
                      <div className="w-1/4 bg-zinc-300 rounded-t h-[40%]" />
                      <div className="w-1/4 bg-zinc-400 rounded-t h-[65%]" />
                      <div className="w-1/4 bg-zinc-600 rounded-t h-[85%]" />
                      <div className="w-1/4 bg-zinc-950 rounded-t h-[100%]" />
                    </div>
                    <div className="flex justify-between text-[7px] font-mono text-zinc-400 pt-1">
                      <span>Q1</span>
                      <span>Q2</span>
                      <span>Q3</span>
                      <span>Q4</span>
                    </div>
                  </div>
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between text-[8px] sm:text-[10px] font-mono text-zinc-400 pt-2 border-t border-zinc-200">
                  <span>Board of Directors Briefing • Confidential</span>
                  <span>PowerPoint Native Widescreen 16:9</span>
                </div>
              </div>

              {/* Bottom Preset Starters */}
              <div className="space-y-2">
                <span className="text-[11px] font-bold uppercase tracking-wider text-zinc-500 block">
                  Quick Starter Presets
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {[
                    {
                      key: "boardroom",
                      title: "McKinsey Boardroom",
                      desc: "8-slide strategic review with chart analyses & executive conclusions.",
                      tag: "Recommended"
                    },
                    {
                      key: "pitch",
                      title: "Series A Pitch",
                      desc: "High-velocity venture narrative emphasizing rapid enterprise ARR capture.",
                      tag: "Fundraising"
                    },
                    {
                      key: "qbr",
                      title: "Quarterly Review (QBR)",
                      desc: "Operational cadence deck with unit economics & next quarter priorities.",
                      tag: "Executive"
                    }
                  ].map((p) => (
                    <button
                      key={p.key}
                      type="button"
                      onClick={() => loadPreset(p.key as any)}
                      className="p-3 rounded-xl bg-zinc-50 border border-zinc-200 hover:border-zinc-400 hover:bg-zinc-100/70 text-left transition cursor-pointer group flex flex-col justify-between"
                    >
                      <div>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-bold text-zinc-900 group-hover:underline">
                            {p.title}
                          </span>
                          <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-white text-zinc-700 border border-zinc-200 font-medium">
                            {p.tag}
                          </span>
                        </div>
                        <p className="text-[10px] text-zinc-500 leading-relaxed line-clamp-2">
                          {p.desc}
                        </p>
                      </div>
                      <span className="text-[10px] font-bold text-zinc-900 mt-2 flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                        Load preset &rarr;
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Plan Schema Inspector Modal */}
      <PlanModal
        isOpen={isPlanModalOpen}
        onClose={() => setIsPlanModalOpen(false)}
        plan={generatedResult ? generatedResult.plan : null}
      />
    </div>
  );
}
