"use client";

import React, { useRef, useState } from "react";
import { UploadCloud, Image as ImageIcon, Trash2, Tag, Check, Loader2, Sparkles } from "lucide-react";
import { UploadedImage } from "@/types";
import { getApiUrl } from "@/constants/api";

interface ImageUploaderProps {
  images: UploadedImage[];
  onImagesChange: (images: UploadedImage[]) => void;
  selectedLogoId: string | null;
  onSelectLogo: (id: string | null) => void;
}

export const ImageUploader: React.FC<ImageUploaderProps> = ({
  images,
  onImagesChange,
  selectedLogoId,
  onSelectLogo
}) => {
  const [isUploading, setIsUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const uploadFiles = async (files: FileList | File[]) => {
    if (!files || files.length === 0) return;

    setIsUploading(true);
    const formData = new FormData();
    Array.from(files).forEach((file) => {
      formData.append("images", file);
    });

    try {
      const res = await fetch(getApiUrl("/api/upload-images"), {
        method: "POST",
        body: formData
      });

      if (res.ok) {
        const data = await res.json();
        if (data.images && data.images.length > 0) {
          const newImages = [...images, ...data.images.map((img: UploadedImage, idx: number) => ({
            ...img,
            file: Array.from(files)[idx] || undefined
          }))];
          onImagesChange(newImages);

          // Auto-select logo if none is active
          if (!selectedLogoId) {
            const logoCandidate = newImages.find((img: UploadedImage) => img.role === "logo");
            if (logoCandidate) {
              onSelectLogo(logoCandidate.id);
            }
          }
        }
      }
    } catch (err) {
      console.error("Upload error:", err);
    } finally {
      setIsUploading(false);
    }
  };

  // Helper to generate a dummy demo logo / chart on the fly using HTML canvas
  const addSampleAsset = (type: "logo" | "chart") => {
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    if (type === "logo") {
      canvas.width = 400;
      canvas.height = 100;
      // Gradient background
      const grad = ctx.createLinearGradient(0, 0, 400, 100);
      grad.addColorStop(0, "#2563EB");
      grad.addColorStop(1, "#06B6D4");
      ctx.fillStyle = grad;
      ctx.roundRect(10, 10, 380, 80, 16);
      ctx.fill();

      // Brand text
      ctx.fillStyle = "#FFFFFF";
      ctx.font = "bold 32px sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("NEXUS AI", 200, 50);
    } else {
      canvas.width = 600;
      canvas.height = 400;
      // Background
      ctx.fillStyle = "#0F172A";
      ctx.fillRect(0, 0, 600, 400);

      // Bar chart
      const colors = ["#3B82F6", "#10B981", "#8B5CF6", "#F59E0B"];
      const heights = [120, 210, 290, 340];
      const labels = ["2023", "2024", "2025", "2026E"];

      ctx.font = "bold 20px sans-serif";
      ctx.fillStyle = "#F8FAFC";
      ctx.fillText("ARR Trajectory ($M)", 40, 45);

      for (let i = 0; i < 4; i++) {
        const x = 70 + i * 130;
        const h = heights[i];
        const y = 340 - h;
        ctx.fillStyle = colors[i];
        ctx.roundRect(x, y, 80, h, [8, 8, 0, 0]);
        ctx.fill();

        ctx.fillStyle = "#94A3B8";
        ctx.font = "14px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(labels[i], x + 40, 370);
      }
    }

    canvas.toBlob((blob) => {
      if (blob) {
        const filename = type === "logo" ? "company_logo.png" : "revenue_trajectory_chart.png";
        const file = new File([blob], filename, { type: "image/png" });
        uploadFiles([file]);
      }
    }, "image/png");
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      uploadFiles(e.dataTransfer.files);
    }
  };

  const handleRoleChange = (id: string, role: UploadedImage["role"]) => {
    const updated = images.map((img) => (img.id === id ? { ...img, role } : img));
    onImagesChange(updated);
    if (role === "logo") {
      onSelectLogo(id);
    } else if (selectedLogoId === id) {
      onSelectLogo(null);
    }
  };

  const handleRemove = (id: string) => {
    onImagesChange(images.filter((img) => img.id !== id));
    if (selectedLogoId === id) {
      onSelectLogo(null);
    }
  };

  return (
    <div className="flex flex-col space-y-3.5">
      {/* Quick Demo Sample Assets */}
      <div className="flex items-center justify-between gap-2 p-2 rounded-xl bg-slate-950/60 border border-slate-800">
        <span className="text-[11px] text-slate-400 font-medium">Quick Demo Assets:</span>
        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={() => addSampleAsset("logo")}
            disabled={isUploading}
            className="flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-semibold bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/20 transition"
          >
            <Sparkles className="w-3 h-3" />
            + Sample Logo
          </button>
          <button
            type="button"
            onClick={() => addSampleAsset("chart")}
            disabled={isUploading}
            className="flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-semibold bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/20 transition"
          >
            <Sparkles className="w-3 h-3" />
            + Sample Chart
          </button>
        </div>
      </div>

      {/* Drop Area */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-xl p-5 text-center cursor-pointer transition flex flex-col items-center justify-center gap-1.5 ${
          dragActive
            ? "border-blue-500 bg-blue-500/10"
            : "border-slate-800 hover:border-slate-700 bg-slate-900/40 hover:bg-slate-900/80"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/*"
          className="hidden"
          onChange={(e) => {
            if (e.target.files) uploadFiles(e.target.files);
          }}
        />

        {isUploading ? (
          <div className="flex flex-col items-center gap-2 text-blue-400 py-2">
            <Loader2 className="w-7 h-7 animate-spin" />
            <p className="text-xs font-medium">Processing & uploading image assets...</p>
          </div>
        ) : (
          <>
            <div className="w-9 h-9 rounded-full bg-blue-500/10 flex items-center justify-center text-blue-400">
              <UploadCloud className="w-4 h-4" />
            </div>
            <div>
              <p className="text-xs font-medium text-slate-200">
                Click or drag & drop presentation images
              </p>
              <p className="text-[10px] text-slate-400 mt-0.5">
                PNG, JPG, SVG, WEBP (Company logos, metric charts, architecture diagrams)
              </p>
            </div>
          </>
        )}
      </div>

      {/* Uploaded Image Cards */}
      {images.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400 font-medium">
            <span>Attached Presentation Assets ({images.length})</span>
            <span className="text-[10px] text-slate-400">Nemotron maps images into slide layouts</span>
          </div>

          <div className="space-y-2 max-h-[260px] overflow-y-auto pr-1">
            {images.map((img) => (
              <div
                key={img.id}
                className="flex items-center gap-3 p-2 rounded-lg bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition"
              >
                {/* Thumbnail */}
                <div className="w-11 h-11 rounded-md bg-slate-950 overflow-hidden flex items-center justify-center shrink-0 border border-slate-800">
                  <img
                    src={getApiUrl(img.url)}
                    alt={img.original_name}
                    className="w-full h-full object-contain"
                    onError={(e) => {
                      (e.target as HTMLElement).style.display = "none";
                    }}
                  />
                </div>

                {/* Info & Role Tag */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5">
                    <p className="text-xs font-medium text-slate-200 truncate">{img.original_name}</p>
                    {selectedLogoId === img.id && (
                      <span className="text-[9px] px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-300 font-bold border border-amber-500/30 shrink-0">
                        Primary Logo
                      </span>
                    )}
                  </div>
                  <p className="text-[10px] text-slate-400">
                    {img.width}x{img.height} px
                  </p>
                </div>

                {/* Role Selector */}
                <div className="flex items-center gap-1.5 shrink-0">
                  <select
                    value={img.role}
                    onChange={(e) => handleRoleChange(img.id, e.target.value as UploadedImage["role"])}
                    className="text-xs bg-slate-800 border border-slate-700 rounded-md px-2 py-1 text-slate-200 font-medium focus:outline-none focus:border-blue-500 cursor-pointer"
                  >
                    <option value="logo">🏷️ Company Logo</option>
                    <option value="hero">🖼️ Hero Visual</option>
                    <option value="chart">📊 Data Chart</option>
                    <option value="team">👥 Team Photo</option>
                    <option value="graphic">💡 Diagram</option>
                  </select>

                  <button
                    type="button"
                    onClick={() => handleRemove(img.id)}
                    className="p-1.5 rounded-md hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 transition"
                    title="Remove asset"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
