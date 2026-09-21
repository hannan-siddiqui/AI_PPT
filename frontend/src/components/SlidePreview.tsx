"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  SlidePlan,
  SlideData,
  UploadedImage,
  QAJudgeReport
} from "@/types";
import {
  ChevronLeft,
  ChevronRight,
  Download,
  Code,
  Sparkles,
  Maximize2,
  Minimize2,
  MessageSquareText,
  Volume2,
  Tv,
  CheckCircle2,
  ShieldCheck,
  ChevronDown,
  ChevronUp
} from "lucide-react";
import { getApiUrl } from "@/constants/api";

interface SlidePreviewProps {
  plan: SlidePlan;
  downloadUrl: string;
  filename: string;
  images: UploadedImage[];
  logoId: string | null;
  logoPlacement: "top-right" | "top-left" | "cover-only";
  qaReport?: QAJudgeReport;
  onOpenPlanModal: () => void;
}

export const SlidePreview: React.FC<SlidePreviewProps> = ({
  plan,
  downloadUrl,
  filename,
  images,
  logoId,
  logoPlacement,
  qaReport,
  onOpenPlanModal
}) => {
  const [currentIdx, setCurrentIdx] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showSpeakerNotes, setShowSpeakerNotes] = useState(true);
  const [isDownloading, setIsDownloading] = useState(false);
  const [showQaDetails, setShowQaDetails] = useState(false);

  const handleDownload = async (e: React.MouseEvent) => {
    e.preventDefault();
    if (isDownloading) return;
    setIsDownloading(true);
    try {
      const fullUrl = getApiUrl(downloadUrl);
      const res = await fetch(fullUrl);
      if (!res.ok) throw new Error("Failed to download file");
      const blob = await res.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = blobUrl;
      const cleanName = (filename || "Presentation.pptx").trim();
      a.download = cleanName.endsWith(".pptx") ? cleanName : `${cleanName}.pptx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(() => window.URL.revokeObjectURL(blobUrl), 2000);
    } catch (err) {
      console.error("Blob download failed, fallback to direct URL:", err);
      window.location.href = getApiUrl(downloadUrl);
    } finally {
      setIsDownloading(false);
    }
  };

  const slides = plan.slides || [];
  const currentSlide: SlideData | undefined = slides[currentIdx];
  const theme = plan.theme;
  const total = slides.length;

  const nextSlide = useCallback(() => {
    if (currentIdx < total - 1) setCurrentIdx((prev) => prev + 1);
  }, [currentIdx, total]);

  const prevSlide = useCallback(() => {
    if (currentIdx > 0) setCurrentIdx((prev) => prev - 1);
  }, [currentIdx]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight" || e.key === " ") {
        nextSlide();
      } else if (e.key === "ArrowLeft") {
        prevSlide();
      } else if (e.key === "Escape" && isFullscreen) {
        setIsFullscreen(false);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [nextSlide, prevSlide, isFullscreen]);

  // Find image helper (by id or direct url)
  const getImage = (imgId?: string | null, imgUrl?: string | null) => {
    if (imgUrl) return { url: imgUrl, id: imgId || "chart", role: "chart" as const, filename: "chart.png", original_name: "chart.png", width: 1800, height: 1000 };
    if (!imgId) return null;
    return images.find((i) => i.id === imgId) || null;
  };

  const activeLogo = getImage(logoId);

  // Render individual slide canvas content
  const renderSlideContent = (slide: SlideData, isFull: boolean = false) => {
    return (
      <div
        className="w-full h-full flex flex-col justify-between p-6 sm:p-8 relative overflow-hidden transition-colors"
        style={{
          backgroundColor: theme.bg_color,
          color: theme.text_color
        }}
      >
        {/* Logo if placed on content slides */}
        {activeLogo &&
          slide.layout_type !== "title_hero" &&
          logoPlacement !== "cover-only" && (
            <div
              className={`absolute top-6 ${
                logoPlacement === "top-left" ? "left-8" : "right-8"
              } h-8 w-24 flex items-center justify-end z-10`}
            >
              <img
                src={getApiUrl(activeLogo.url)}
                alt="Logo"
                className="max-h-8 max-w-24 object-contain"
              />
            </div>
          )}

        {/* SLIDE CONTENT DISPATCHER */}
        {slide.layout_type === "title_hero" ? (
          // PUBLICATION-GRADE EXECUTIVE BOARDROOM COVER
          <div className="flex flex-col h-full justify-between relative px-2 py-1">
            {/* Left Vertical Ribbon */}
            <div
              className="absolute left-0 top-0 bottom-0 w-1.5 rounded-l"
              style={{ backgroundColor: theme.primary_color || "#1D4ED8" }}
            />

            {/* Top Area: Status Pill */}
            <div className="pt-2 pl-4">
              <div
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-bold tracking-wider uppercase border"
                style={{
                  backgroundColor: theme.secondary_color || "#F1F5F9",
                  borderColor: theme.subheading_color || "#0284C7",
                  color: theme.subheading_color || "#0284C7"
                }}
              >
                <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: theme.accent_color || "#0284C7" }} />
                <span>{slide.kicker || "BOARD OF DIRECTORS BRIEFING"}</span>
              </div>
            </div>

            {/* Middle Grid: Left Headline + Right Briefing Scope Card */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center px-4 my-auto">
              {/* Left Column */}
              <div className="md:col-span-7 space-y-3">
                <h1
                  className={`font-extrabold tracking-tight leading-tight ${
                    isFull ? "text-3xl sm:text-4xl lg:text-5xl" : "text-xl sm:text-2xl lg:text-3xl"
                  }`}
                  style={{ color: theme.heading_color || "#1D4ED8" }}
                >
                  {slide.title}
                </h1>

                {slide.subtitle && (
                  <p
                    className={`leading-relaxed ${
                      isFull ? "text-base sm:text-lg" : "text-xs sm:text-sm"
                    }`}
                    style={{ color: theme.muted_text_color || "#64748B" }}
                  >
                    {slide.subtitle}
                  </p>
                )}

                <div className="pt-1">
                  <span
                    className="text-[11px] font-semibold"
                    style={{ color: theme.subheading_color || "#0284C7" }}
                  >
                    Target Audience: CXOs & Board of Directors • Governance Grade Diagnostic
                  </span>
                </div>
              </div>

              {/* Right Column: Hero Image OR Executive Briefing Scope Card */}
              <div className="md:col-span-5">
                {getImage(slide.image_id) ? (
                  <div
                    className="p-3 rounded-xl border relative shadow-xs"
                    style={{
                      backgroundColor: theme.card_bg_color || "#FFFFFF",
                      borderColor: theme.secondary_color || "#E2E8F0"
                    }}
                  >
                    <div
                      className="text-[9px] font-bold tracking-wider uppercase mb-2"
                      style={{ color: theme.subheading_color || "#0284C7" }}
                    >
                      EXHIBIT // EMPIRICAL OVERVIEW
                    </div>
                    <img
                      src={getApiUrl(getImage(slide.image_id)!.url)}
                      alt="Hero"
                      className="max-h-48 max-w-full object-contain rounded-lg mx-auto"
                    />
                  </div>
                ) : (
                  <div
                    className="p-4 rounded-xl border relative shadow-xs space-y-2.5 overflow-hidden"
                    style={{
                      backgroundColor: theme.card_bg_color || "#F8FAFC",
                      borderColor: theme.secondary_color || "#E2E8F0"
                    }}
                  >
                    {/* Top Accent Stripe */}
                    <div
                      className="absolute top-0 left-0 right-0 h-1"
                      style={{ backgroundColor: theme.subheading_color || "#0284C7" }}
                    />
                    <div>
                      <div
                        className="text-[11px] font-bold tracking-wider uppercase"
                        style={{ color: theme.heading_color || "#1D4ED8" }}
                      >
                        EXECUTIVE BRIEFING SCOPE
                      </div>
                      <div
                        className="text-[9.5px]"
                        style={{ color: theme.muted_text_color || "#64748B" }}
                      >
                        Strategic agenda & diagnostic dimensions:
                      </div>
                    </div>

                    <div className="space-y-1.5 pt-1">
                      {(slide.focus_areas && slide.focus_areas.length > 0
                        ? slide.focus_areas
                        : [
                            "Empirical Diagnostics: Quantitative evaluation across core operational dimensions",
                            "Divisional Parity Analysis: Benchmarking high-performer compensation and capacity",
                            "Workforce Capacity Dynamics: SOP FTE to EOP retention trajectories",
                            "Strategic Governance Roadmap: Boardroom resolutions and priority next steps"
                          ]
                      ).map((item, idx) => (
                        <div key={idx} className="flex items-start gap-2 text-[10.5px] leading-snug">
                          <span
                            className="font-bold select-none text-xs"
                            style={{ color: theme.accent_color || "#0284C7" }}
                          >
                            ▪
                          </span>
                          <span style={{ color: theme.text_color || "#0F172A" }}>{item}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Bottom: 4-Column Boardroom Metadata Ribbon */}
            <div
              className="pt-2 pb-1 border-t grid grid-cols-2 sm:grid-cols-4 gap-3 text-left pl-4"
              style={{ borderColor: theme.secondary_color || "#E2E8F0" }}
            >
              <div>
                <div
                  className="text-[8px] font-bold uppercase tracking-wider"
                  style={{ color: theme.muted_text_color || "#64748B" }}
                >
                  PREPARED FOR
                </div>
                <div
                  className="text-[10.5px] font-bold"
                  style={{ color: theme.text_color || "#0F172A" }}
                >
                  Board of Directors / CXOs
                </div>
              </div>
              <div>
                <div
                  className="text-[8px] font-bold uppercase tracking-wider"
                  style={{ color: theme.muted_text_color || "#64748B" }}
                >
                  PREPARED BY
                </div>
                <div
                  className="text-[10.5px] font-bold"
                  style={{ color: theme.text_color || "#0F172A" }}
                >
                  {slide.presenter || "Executive Strategic Advisory"}
                </div>
              </div>
              <div>
                <div
                  className="text-[8px] font-bold uppercase tracking-wider"
                  style={{ color: theme.muted_text_color || "#64748B" }}
                >
                  DATE & CYCLE
                </div>
                <div
                  className="text-[10.5px] font-bold"
                  style={{ color: theme.text_color || "#0F172A" }}
                >
                  Annual Strategy Review
                </div>
              </div>
              <div>
                <div
                  className="text-[8px] font-bold uppercase tracking-wider"
                  style={{ color: theme.muted_text_color || "#64748B" }}
                >
                  CLASSIFICATION
                </div>
                <div
                  className="text-[10.5px] font-bold"
                  style={{ color: theme.heading_color || "#1D4ED8" }}
                >
                  STRICTLY CONFIDENTIAL
                </div>
              </div>
            </div>
          </div>
        ) : slide.layout_type === "stats_kpis" ? (
          // STATS & KPIS LAYOUT
          <div className="flex flex-col h-full justify-between">
            <div>
              <div
                className="h-1 w-12 rounded mb-2"
                style={{ backgroundColor: theme.subheading_color || "#0284C7" }}
              />
              <div
                className="text-[11px] font-bold tracking-widest uppercase mb-1"
                style={{ color: theme.subheading_color || "#0284C7" }}
              >
                {slide.kicker || "KEY METRICS"}
              </div>
              <h2
                className={`font-bold tracking-tight ${isFull ? "text-3xl" : "text-xl sm:text-2xl"}`}
                style={{ color: theme.heading_color || "#1D4ED8" }}
              >
                {slide.title}
              </h2>
              {slide.subtitle && (
                <p
                  className="text-xs sm:text-sm mt-0.5"
                  style={{ color: theme.subheading_color || "#0284C7" }}
                >
                  {slide.subtitle}
                </p>
              )}
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 my-auto">
              {(slide.stats || []).map((st, i) => (
                <div
                  key={i}
                  className="p-4 rounded-xl border relative flex flex-col justify-between overflow-hidden shadow-sm"
                  style={{
                    backgroundColor: theme.card_bg_color,
                    borderColor: theme.secondary_color
                  }}
                >
                  <div
                    className="absolute top-0 left-0 right-0 h-1"
                    style={{ backgroundColor: theme.subheading_color || "#0284C7" }}
                  />
                  <div>
                    <div
                      className={`font-extrabold tracking-tight mb-1 ${isFull ? "text-4xl" : "text-2xl sm:text-3xl"}`}
                      style={{ color: theme.heading_color || "#1D4ED8" }}
                    >
                      {st.value}
                    </div>
                    {st.change && (
                      <div className="text-[11px] font-bold text-emerald-600 mb-2 flex items-center gap-1">
                        <span>▲</span> {st.change}
                      </div>
                    )}
                    <div className="text-xs font-bold leading-snug">{st.label}</div>
                  </div>
                  {st.subtext && (
                    <div
                      className="text-[10px] mt-2 leading-tight"
                      style={{ color: theme.muted_text_color || "#64748B" }}
                    >
                      {st.subtext}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ) : slide.layout_type === "chart_focus" ? (
          // DEDICATED CHART FOCUS LAYOUT (60% Chart + Strategic Analysis)
          <div className="flex flex-col h-full justify-between">
            <div>
              <div
                className="h-1 w-12 rounded mb-1.5"
                style={{ backgroundColor: theme.subheading_color || "#0284C7" }}
              />
              <div
                className="text-[11px] font-bold tracking-widest uppercase mb-1"
                style={{ color: theme.subheading_color || "#0284C7" }}
              >
                {slide.kicker || "EXECUTIVE DATA INTELLIGENCE"}
              </div>
              <h2
                className={`font-extrabold tracking-tight ${isFull ? "text-3xl" : "text-lg sm:text-2xl"}`}
                style={{ color: theme.heading_color || "#1D4ED8" }}
              >
                {slide.title}
              </h2>
              {slide.subtitle && (
                <p
                  className="text-xs sm:text-sm mt-0.5"
                  style={{ color: theme.subheading_color || "#0284C7" }}
                >
                  {slide.subtitle}
                </p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-12 gap-3.5 my-auto items-stretch">
              {/* Left Column: Strategic Takeaways */}
              <div
                className="md:col-span-5 p-3.5 sm:p-4 rounded-xl border flex flex-col justify-between shadow-sm relative overflow-hidden"
                style={{
                  backgroundColor: theme.card_bg_color,
                  borderColor: theme.secondary_color
                }}
              >
                <div
                  className="absolute top-0 left-0 right-0 h-1"
                  style={{ backgroundColor: theme.subheading_color || "#0284C7" }}
                />
                <div>
                  <span
                    className="text-[10px] font-bold tracking-wider uppercase block mb-2"
                    style={{ color: theme.subheading_color || "#0284C7" }}
                  >
                    Strategic Takeaways & Evidence
                  </span>
                  <div className="space-y-2">
                    {(slide.bullets || []).map((b, i) => (
                      <div key={i} className="flex items-start gap-2 text-xs sm:text-[13px] leading-relaxed">
                        <span
                          className="font-bold text-xs mt-0.5 shrink-0"
                          style={{ color: theme.heading_color || "#1D4ED8" }}
                        >
                          ▪
                        </span>
                        <span>{b}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div
                  className="text-[9px] pt-2 mt-2 border-t font-semibold"
                  style={{ borderColor: theme.secondary_color, color: theme.muted_text_color || "#64748B" }}
                >
                  Boardroom Executive Decision Summary
                </div>
              </div>

              {/* Right Column: Prominent Chart Frame */}
              <div
                className="md:col-span-7 p-2 rounded-xl border flex flex-col justify-between items-center overflow-hidden shadow-sm relative"
                style={{
                  backgroundColor: theme.card_bg_color,
                  borderColor: theme.secondary_color
                }}
              >
                <div className="w-full flex-1 flex items-center justify-center min-h-[220px]">
                  {getImage(slide.image_id, slide.image_url) ? (
                    <img
                      src={getApiUrl(getImage(slide.image_id, slide.image_url)!.url)}
                      alt="Data Chart"
                      className="max-h-64 w-full object-contain rounded-lg"
                    />
                  ) : (
                    <div className="text-center p-4">
                      <Sparkles
                        className="w-8 h-8 mx-auto mb-2 opacity-60"
                        style={{ color: theme.heading_color || "#1D4ED8" }}
                      />
                      <div
                        className="text-xs font-bold uppercase tracking-wider"
                        style={{ color: theme.heading_color || "#1D4ED8" }}
                      >
                        Executive Chart Visual
                      </div>
                      <p
                        className="text-[11px] mt-1"
                        style={{ color: theme.muted_text_color || "#64748B" }}
                      >
                        Quantitative Distribution Analysis
                      </p>
                    </div>
                  )}
                </div>

                <div
                  className="w-full text-right text-[8px] font-mono opacity-60 px-2 pt-1 border-t"
                  style={{ borderColor: theme.secondary_color }}
                >
                  Source: Enterprise Analytics Dataset • Confidential
                </div>
              </div>
            </div>
          </div>
        ) : slide.layout_type === "split_image_text" ? (
          // SPLIT SCREEN (Narrative + Image)
          <div className="flex flex-col h-full justify-between">
            <div>
              <div
                className="h-1 w-12 rounded mb-2"
                style={{ backgroundColor: theme.subheading_color || "#0284C7" }}
              />
              <div
                className="text-[11px] font-bold tracking-widest uppercase mb-1"
                style={{ color: theme.subheading_color || "#0284C7" }}
              >
                {slide.kicker || "STRATEGIC OVERVIEW"}
              </div>
              <h2
                className={`font-bold tracking-tight ${isFull ? "text-3xl" : "text-xl sm:text-2xl"}`}
                style={{ color: theme.heading_color || "#1D4ED8" }}
              >
                {slide.title}
              </h2>
              {slide.subtitle && (
                <p
                  className="text-xs sm:text-sm mt-0.5"
                  style={{ color: theme.subheading_color || "#0284C7" }}
                >
                  {slide.subtitle}
                </p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-12 gap-4 my-auto items-stretch">
              <div
                className="md:col-span-7 p-4 sm:p-5 rounded-xl border flex flex-col justify-center space-y-3 shadow-sm"
                style={{
                  backgroundColor: theme.card_bg_color,
                  borderColor: theme.secondary_color
                }}
              >
                <span
                  className="text-[10px] font-bold tracking-wider uppercase"
                  style={{ color: theme.subheading_color || "#0284C7" }}
                >
                  Key Takeaways & Evidence
                </span>
                {(slide.bullets || []).map((b, i) => (
                  <div key={i} className="flex items-start gap-2.5 text-xs sm:text-sm leading-relaxed">
                    <span
                      className="font-bold text-xs mt-0.5"
                      style={{ color: theme.heading_color || "#1D4ED8" }}
                    >
                      ▪
                    </span>
                    <span>{b}</span>
                  </div>
                ))}
              </div>

              <div
                className="md:col-span-5 p-3 rounded-xl border flex items-center justify-center overflow-hidden shadow-sm"
                style={{
                  backgroundColor: theme.card_bg_color,
                  borderColor: theme.secondary_color
                }}
              >
                {getImage(slide.image_id, slide.image_url) ? (
                  <img
                    src={getApiUrl(getImage(slide.image_id, slide.image_url)!.url)}
                    alt="Slide graphic"
                    className="max-h-56 w-auto object-contain rounded shadow-sm"
                  />
                ) : (
                  <div className="text-center p-4">
                    <Sparkles
                      className="w-8 h-8 mx-auto mb-2 opacity-60"
                      style={{ color: theme.heading_color || "#1D4ED8" }}
                    />
                    <div
                      className="text-xs font-bold uppercase tracking-wider"
                      style={{ color: theme.heading_color || "#1D4ED8" }}
                    >
                      Executive Visual
                    </div>
                    <p
                      className="text-[11px] mt-1"
                      style={{ color: theme.muted_text_color || "#64748B" }}
                    >
                      High-impact strategic execution
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : slide.layout_type === "timeline_process" ? (
          // TIMELINE / ROADMAP
          <div className="flex flex-col h-full justify-between">
            <div>
              <div
                className="h-1 w-12 rounded mb-2"
                style={{ backgroundColor: theme.subheading_color || "#0284C7" }}
              />
              <div
                className="text-[11px] font-bold tracking-widest uppercase mb-1"
                style={{ color: theme.subheading_color || "#0284C7" }}
              >
                {slide.kicker || "ROADMAP & EXECUTION"}
              </div>
              <h2
                className={`font-bold tracking-tight ${isFull ? "text-3xl" : "text-xl sm:text-2xl"}`}
                style={{ color: theme.heading_color || "#1D4ED8" }}
              >
                {slide.title}
              </h2>
              {slide.subtitle && (
                <p
                  className="text-xs sm:text-sm mt-0.5"
                  style={{ color: theme.subheading_color || "#0284C7" }}
                >
                  {slide.subtitle}
                </p>
              )}
            </div>

            <div className="grid grid-cols-3 sm:grid-cols-4 gap-3 my-auto">
              {(slide.timeline_steps || []).map((step, i) => (
                <div
                  key={i}
                  className="p-3.5 rounded-xl border relative flex flex-col justify-between overflow-hidden shadow-sm"
                  style={{
                    backgroundColor: theme.card_bg_color,
                    borderColor: theme.secondary_color
                  }}
                >
                  <div
                    className="w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs text-white mb-2.5 shadow-sm"
                    style={{ backgroundColor: theme.subheading_color || "#0284C7" }}
                  >
                    {i + 1}
                  </div>
                  <div>
                    <div
                      className="text-[10px] font-bold uppercase tracking-wider mb-1"
                      style={{ color: theme.subheading_color || "#0284C7" }}
                    >
                      {step.step || step.quarter || `Phase ${i + 1}`}
                    </div>
                    <div
                      className="text-xs sm:text-sm font-bold mb-1.5"
                      style={{ color: theme.heading_color || "#1D4ED8" }}
                    >
                      {step.title}
                    </div>
                    <p
                      className="text-[11px] leading-relaxed"
                      style={{ color: theme.muted_text_color || "#64748B" }}
                    >
                      {step.description || step.detail}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : slide.layout_type === "closing_contact" ? (
          // CLOSING / ACTION PLAN (Dual-Card Boardroom Layout - Fully Aligned & Filled)
          <div className="flex flex-col h-full justify-between">
            {/* Slide Header */}
            <div>
              <div
                className="h-1 w-12 rounded mb-2"
                style={{ backgroundColor: theme.subheading_color || "#0284C7" }}
              />
              <div
                className="text-[11px] font-bold tracking-wider uppercase mb-1"
                style={{ color: theme.subheading_color || "#0284C7" }}
              >
                {slide.kicker || "CONCLUSION & BOARD ACTION PLAN"}
              </div>
              <h2
                className={`font-black tracking-tight leading-tight mb-1 ${
                  isFull ? "text-2xl" : "text-xl sm:text-2xl"
                }`}
                style={{ color: theme.heading_color || "#1D4ED8" }}
              >
                {slide.title || "Recommended Resolutions & Executive Next Steps"}
              </h2>
              {slide.subtitle && (
                <p
                  className="text-xs font-medium"
                  style={{ color: theme.subheading_color || "#0284C7" }}
                >
                  {slide.subtitle}
                </p>
              )}
            </div>

            {/* Dual Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-3.5 my-auto pt-2">
              {/* Left Card: Immediate Board Resolutions (7 cols) */}
              <div
                className="md:col-span-7 p-4 rounded-xl border flex flex-col justify-between"
                style={{
                  backgroundColor: theme.card_bg_color || "#FFFFFF",
                  borderColor: theme.secondary_color || "#E2E8F0"
                }}
              >
                <div>
                  <div className="flex items-center gap-1.5 mb-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                    <span
                      className="text-[10px] font-bold tracking-wider uppercase"
                      style={{ color: theme.subheading_color || "#0284C7" }}
                    >
                      PRIORITY EXECUTIVE WORKSTREAMS
                    </span>
                  </div>
                  <h3
                    className="text-sm font-bold mb-3"
                    style={{ color: theme.heading_color || "#1D4ED8" }}
                  >
                    Immediate Board Resolutions
                  </h3>
                  <div className="space-y-2">
                    {(slide.bullets && slide.bullets.length > 0
                      ? slide.bullets
                      : [
                          "Charter cross-divisional compensation taskforce to institutionalize parity",
                          "Approve targeted leadership development pathways for emerging talent",
                          "Mandate quarterly demographic & compensation audits for Board Committee",
                          "Authorize phased 90-day technical resource allocation roadmap"
                        ]
                    ).slice(0, 4).map((b, i) => (
                      <div key={i} className="flex items-start gap-2 text-xs">
                        <span className="text-emerald-600 font-bold shrink-0 mt-0.5">✔</span>
                        <span style={{ color: theme.text_color || "#0F172A" }}>{b}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Right Card: Governance & Execution (5 cols) */}
              <div
                className="md:col-span-5 p-4 rounded-xl border flex flex-col justify-between"
                style={{
                  backgroundColor: theme.card_bg_color || "#FFFFFF",
                  borderColor: theme.secondary_color || "#E2E8F0"
                }}
              >
                <div>
                  <div className="flex items-center gap-1.5 mb-2">
                    <span className="w-2 h-2 rounded-full bg-blue-500" />
                    <span
                      className="text-[10px] font-bold tracking-wider uppercase"
                      style={{ color: theme.subheading_color || "#0284C7" }}
                    >
                      GOVERNANCE & EXECUTION
                    </span>
                  </div>
                  <h3
                    className="text-sm font-bold mb-3"
                    style={{ color: theme.heading_color || "#1D4ED8" }}
                  >
                    Steering & Advisory Cadence
                  </h3>
                  <div className="space-y-2 text-xs">
                    <div>
                      <span className="font-bold text-[10px] uppercase block" style={{ color: theme.subheading_color }}>
                        Steering Cadence
                      </span>
                      <span className="text-zinc-600 text-[11px]">Bi-weekly executive checkpoint</span>
                    </div>
                    <div>
                      <span className="font-bold text-[10px] uppercase block" style={{ color: theme.subheading_color }}>
                        Board Oversight
                      </span>
                      <span className="text-zinc-600 text-[11px]">Quarterly Audit & Risk Review</span>
                    </div>
                    <div>
                      <span className="font-bold text-[10px] uppercase block" style={{ color: theme.subheading_color }}>
                        Target Horizon
                      </span>
                      <span className="text-zinc-600 text-[11px]">90-Day phased execution window</span>
                    </div>
                    <div>
                      <span className="font-bold text-[10px] uppercase block" style={{ color: theme.subheading_color }}>
                        Advisory Contact
                      </span>
                      <span className="text-zinc-600 text-[11px]">Senior Strategy Leadership</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          // DEFAULT / CARDS GRID
          <div className="flex flex-col h-full justify-between">
            <div>
              <div
                className="h-1 w-12 rounded mb-2"
                style={{ backgroundColor: theme.subheading_color || "#0284C7" }}
              />
              <div
                className="text-[11px] font-bold tracking-wider uppercase mb-1"
                style={{ color: theme.subheading_color || "#0284C7" }}
              >
                {slide.kicker}
              </div>
              <h2
                className={`font-black tracking-tight leading-tight mb-1 ${
                  isFull ? "text-2xl" : "text-xl sm:text-2xl"
                }`}
                style={{ color: theme.heading_color || "#1D4ED8" }}
              >
                {slide.title}
              </h2>
              {slide.subtitle && (
                <p
                  className="text-xs font-medium"
                  style={{ color: theme.subheading_color || "#0284C7" }}
                >
                  {slide.subtitle}
                </p>
              )}
            </div>

            <div
              className={`grid gap-3.5 my-auto pt-2 ${
                (slide.cards || []).length <= 2
                  ? "grid-cols-1 sm:grid-cols-2"
                  : (slide.cards || []).length === 3
                  ? "grid-cols-1 sm:grid-cols-3"
                  : "grid-cols-1 sm:grid-cols-2 lg:grid-cols-4"
              }`}
            >
              {(slide.cards || []).map((c, i) => (
                <div
                  key={i}
                  className="p-3.5 rounded-xl border flex flex-col justify-between"
                  style={{
                    backgroundColor: theme.card_bg_color || "#FFFFFF",
                    borderColor: theme.secondary_color || "#E2E8F0"
                  }}
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span
                        className="text-[10px] font-bold tracking-widest px-2 py-0.5 rounded-full"
                        style={{
                          backgroundColor: `${theme.primary_color}15`,
                          color: theme.subheading_color || theme.primary_color
                        }}
                      >
                        {c.badge || `0${i + 1}`}
                      </span>
                    </div>
                    <h3
                      className="text-xs sm:text-sm font-bold mb-1.5 leading-snug"
                      style={{ color: theme.heading_color || "#1D4ED8" }}
                    >
                      {c.title}
                    </h3>
                    <p
                      className="text-[11px] leading-relaxed"
                      style={{ color: theme.muted_text_color || "#64748B" }}
                    >
                      {c.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Slide Footer (ONLY shown if user explicitly requested footer_text in instructions) */}
        {slide.layout_type !== "title_hero" && plan.footer_text && (
          <div
            className="pt-2.5 flex items-center justify-between text-[10px] font-medium border-t"
            style={{
              borderColor: theme.secondary_color,
              color: theme.muted_text_color || "#94A3B8"
            }}
          >
            <span>{plan.footer_text}</span>
            <span>
              Slide {currentIdx + 1} of {total}
            </span>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full space-y-3.5">
      {/* Top Deck Action Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 p-3 rounded-xl bg-white border border-zinc-200 shadow-xs">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-sm font-bold text-zinc-900 tracking-tight">{plan.deck_title}</h2>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-zinc-100 text-zinc-700 font-mono font-medium border border-zinc-200">
              {total} Slides
            </span>

            {qaReport && (
              <button
                type="button"
                onClick={() => setShowQaDetails(!showQaDetails)}
                className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-zinc-100 hover:bg-zinc-200 text-zinc-800 font-medium text-[10px] border border-zinc-200 transition cursor-pointer"
                title="Click to view VLM-as-Judge Quality Assurance inspection report"
              >
                <ShieldCheck className="w-3 h-3 text-zinc-600" />
                <span>QA Score: {qaReport.score}/100</span>
                {showQaDetails ? <ChevronUp className="w-2.5 h-2.5" /> : <ChevronDown className="w-2.5 h-2.5" />}
              </button>
            )}
          </div>
          {plan.deck_subtitle && (
            <p className="text-xs text-zinc-500 truncate max-w-sm">{plan.deck_subtitle}</p>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Present Mode Button */}
          <button
            type="button"
            onClick={() => setIsFullscreen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-100 hover:bg-zinc-200 text-zinc-800 border border-zinc-200 text-xs font-medium transition cursor-pointer"
            title="Present live in fullscreen mode"
          >
            <Tv className="w-3.5 h-3.5 text-zinc-600" />
            <span>Present</span>
          </button>

          <button
            type="button"
            onClick={onOpenPlanModal}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-100 hover:bg-zinc-200 text-zinc-700 border border-zinc-200 text-xs font-medium transition cursor-pointer"
          >
            <Code className="w-3.5 h-3.5 text-zinc-500" />
            <span>Schema</span>
          </button>

          <button
            type="button"
            onClick={handleDownload}
            disabled={isDownloading}
            className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-zinc-950 hover:bg-zinc-800 text-white font-semibold text-xs transition active:scale-95 disabled:opacity-50 cursor-pointer shadow-xs"
            title="Download PowerPoint presentation file"
          >
            <Download className="w-3.5 h-3.5 stroke-[2.5]" />
            <span>{isDownloading ? "Downloading..." : "Download .PPTX"}</span>
          </button>
        </div>
      </div>

      {/* VLM-as-Judge QA Audit Drawer */}
      {qaReport && showQaDetails && (
        <div className="p-3.5 rounded-xl bg-zinc-50 border border-zinc-200 text-xs space-y-2 animate-in fade-in slide-in-from-top-1 text-zinc-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span className="font-bold text-slate-100">Stage 5: VLM-as-Judge QA Assessment ({qaReport.score}/100)</span>
            </div>
            <span className="text-[11px] text-emerald-400 font-semibold uppercase tracking-wider">
              {qaReport.passed ? "Verified & Certified" : "Action Required"}
            </span>
          </div>
          <p className="text-slate-300 leading-relaxed text-[11px]">
            {qaReport.feedback}
          </p>
          {qaReport.applied_fixes && qaReport.applied_fixes.length > 0 && (
            <div className="pt-1 border-t border-slate-800">
              <div className="text-[10px] uppercase font-semibold text-slate-400 mb-1">Automated Visual & Layout Adjustments:</div>
              <ul className="list-disc list-inside space-y-0.5 text-[11px] text-teal-300">
                {qaReport.applied_fixes.map((fix, idx) => (
                  <li key={idx}>{fix}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* 16:9 Live Presentation Canvas */}
      <div className="relative w-full aspect-[16/9] rounded-2xl overflow-hidden shadow-2xl border border-slate-800/80 transition-all select-none">
        {currentSlide && renderSlideContent(currentSlide, false)}
      </div>

      {/* Slide Navigation, Thumbnails & Speaker Notes Toggle */}
      <div className="space-y-2">
        <div className="flex items-center justify-between gap-3 p-2 rounded-xl bg-white border border-zinc-200 shadow-xs">
          <div className="flex items-center gap-1.5">
            <button
              type="button"
              onClick={prevSlide}
              disabled={currentIdx === 0}
              className="p-1.5 rounded-lg bg-zinc-100 hover:bg-zinc-200 text-zinc-700 disabled:opacity-30 disabled:cursor-not-allowed transition cursor-pointer"
              title="Previous slide (Left Arrow)"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="text-xs font-mono font-medium text-zinc-600 px-1">
              {currentIdx + 1} / {total}
            </span>
            <button
              type="button"
              onClick={nextSlide}
              disabled={currentIdx === total - 1}
              className="p-1.5 rounded-lg bg-zinc-100 hover:bg-zinc-200 text-zinc-700 disabled:opacity-30 disabled:cursor-not-allowed transition cursor-pointer"
              title="Next slide (Right Arrow)"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          {/* Thumbnail Ribbon */}
          <div className="flex items-center gap-1.5 overflow-x-auto max-w-md py-1 px-1">
            {slides.map((s, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => setCurrentIdx(idx)}
                className={`shrink-0 w-12 h-8 rounded-lg border text-[11px] font-mono flex items-center justify-center transition cursor-pointer ${
                  currentIdx === idx
                    ? "border-zinc-950 bg-zinc-950 text-white font-bold shadow-xs"
                    : "border-zinc-200 bg-zinc-50 text-zinc-600 hover:text-zinc-950 hover:border-zinc-300"
                }`}
              >
                <span>{idx + 1}</span>
              </button>
            ))}
          </div>

          {/* Speaker Notes Toggle */}
          <button
            type="button"
            onClick={() => setShowSpeakerNotes(!showSpeakerNotes)}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium border transition cursor-pointer ${
              showSpeakerNotes
                ? "border-zinc-950 bg-zinc-950 text-white"
                : "border-zinc-200 bg-zinc-50 text-zinc-600 hover:text-zinc-900"
            }`}
          >
            <MessageSquareText className="w-3.5 h-3.5" />
            <span>Notes</span>
          </button>
        </div>

        {/* Collapsible Speaker Notes Drawer */}
        {showSpeakerNotes && currentSlide?.notes && (
          <div className="p-3.5 rounded-xl bg-zinc-50 border border-zinc-200 text-xs leading-relaxed text-zinc-700 animate-in fade-in slide-in-from-top-1">
            <div className="flex items-center gap-1.5 text-zinc-900 font-bold uppercase tracking-wider text-[10px] mb-1">
              <Volume2 className="w-3 h-3 text-zinc-600" />
              Presenter Talking Points (Slide {currentIdx + 1})
            </div>
            <p className="italic text-zinc-600">{currentSlide.notes}</p>
          </div>
        )}
      </div>

      {/* FULLSCREEN KEYNOTE PRESENTATION MODAL */}
      {isFullscreen && currentSlide && (
        <div className="fixed inset-0 z-50 bg-black flex flex-col justify-between p-6 sm:p-12 animate-in fade-in">
          {/* Floating Exit & Navigation Overlay */}
          <div className="absolute top-6 right-8 z-30 flex items-center gap-3">
            <span className="text-xs font-mono text-slate-400 px-3 py-1 rounded-full bg-slate-900/80 border border-slate-700">
              {currentIdx + 1} / {total} (Use Arrow Keys)
            </span>
            <button
              type="button"
              onClick={() => setIsFullscreen(false)}
              className="p-2 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-slate-200 border border-slate-700 shadow-lg transition"
              title="Exit presentation mode (Esc)"
            >
              <Minimize2 className="w-5 h-5" />
            </button>
          </div>

          {/* Centered Large 16:9 Slide Canvas */}
          <div className="w-full max-w-6xl mx-auto my-auto aspect-[16/9] rounded-2xl overflow-hidden shadow-2xl border border-slate-800 relative">
            {renderSlideContent(currentSlide, true)}
          </div>

          {/* Bottom Floating Nav Buttons */}
          <div className="flex items-center justify-center gap-4 z-20">
            <button
              type="button"
              onClick={prevSlide}
              disabled={currentIdx === 0}
              className="px-4 py-2 rounded-xl bg-slate-900/90 hover:bg-slate-800 text-slate-200 border border-slate-700 disabled:opacity-30 disabled:cursor-not-allowed transition flex items-center gap-2 text-xs font-semibold"
            >
              <ChevronLeft className="w-4 h-4" /> Previous
            </button>
            <button
              type="button"
              onClick={nextSlide}
              disabled={currentIdx === total - 1}
              className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold disabled:opacity-30 disabled:cursor-not-allowed transition flex items-center gap-2 text-xs"
            >
              Next <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
