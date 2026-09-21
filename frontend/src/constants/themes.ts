import { ThemeConfig } from "@/types";

export interface ExtendedThemeConfig extends ThemeConfig {
  tagline?: string;
  category?: string;
}

export const PRESET_THEMES: ExtendedThemeConfig[] = [
  {
    name: "Midnight Executive",
    tagline: "Corporate Boardroom & Strategy",
    category: "Executive",
    primary_color: "#0F172A",
    secondary_color: "#1E293B",
    accent_color: "#3B82F6",
    bg_color: "#090D16",
    text_color: "#F8FAFC",
    card_bg_color: "#131C2E",
    muted_text_color: "#94A3B8"
  },
  {
    name: "Hyperion Obsidian",
    tagline: "High-Tech, AI & Infrastructure",
    category: "Tech",
    primary_color: "#030712",
    secondary_color: "#1F2937",
    accent_color: "#8B5CF6",
    bg_color: "#0B0B14",
    text_color: "#F9FAFB",
    card_bg_color: "#151624",
    muted_text_color: "#A1A1AA"
  },
  {
    name: "Emerald ESG & FinTech",
    tagline: "FinTech, Growth & Sustainable Scaling",
    category: "FinTech",
    primary_color: "#022C22",
    secondary_color: "#064E3B",
    accent_color: "#10B981",
    bg_color: "#041410",
    text_color: "#ECFDF5",
    card_bg_color: "#09241C",
    muted_text_color: "#6EE7B7"
  },
  {
    name: "Crimson Venture",
    tagline: "Series A/B Venture Capital",
    category: "Venture",
    primary_color: "#1C0D11",
    secondary_color: "#381923",
    accent_color: "#F43F5E",
    bg_color: "#12080B",
    text_color: "#FFF1F2",
    card_bg_color: "#241118",
    muted_text_color: "#FDA4AF"
  },
  {
    name: "Sunset Amber",
    tagline: "Product Launches & High-Energy GTM",
    category: "Commercial",
    primary_color: "#1F1608",
    secondary_color: "#3D2B10",
    accent_color: "#F59E0B",
    bg_color: "#120D05",
    text_color: "#FEF3C7",
    card_bg_color: "#261B0A",
    muted_text_color: "#FDE68A"
  },
  {
    name: "Clean Nordic Light",
    tagline: "Minimalist Executive Crisp White",
    category: "Minimal",
    primary_color: "#FFFFFF",
    secondary_color: "#F1F5F9",
    accent_color: "#4F46E5",
    bg_color: "#F8FAFC",
    text_color: "#0F172A",
    card_bg_color: "#FFFFFF",
    muted_text_color: "#64748B"
  }
];
