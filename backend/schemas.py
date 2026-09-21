"""
Pydantic Schemas for the AI Presentation Pipeline
Enforces strict SlideDeckSchema, Vision Analysis schemas, and QA Judge Reports.
"""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class ThemeConfig(BaseModel):
    name: str = "Corporate Navy"
    primary_color: str = "#1D4ED8"
    secondary_color: str = "#F1F5F9"
    accent_color: str = "#0284C7"
    bg_color: str = "#FFFFFF"
    text_color: str = "#0F172A"
    card_bg_color: str = "#F8FAFC"
    muted_text_color: Optional[str] = "#64748B"
    heading_color: Optional[str] = "#1D4ED8"
    subheading_color: Optional[str] = "#0284C7"


class StatItem(BaseModel):
    value: str
    label: str
    change: Optional[str] = None
    subtext: Optional[str] = None


class CardItem(BaseModel):
    badge: Optional[str] = None
    title: str
    description: str


class TimelineItem(BaseModel):
    step: Optional[str] = None
    quarter: Optional[str] = None
    title: str
    description: Optional[str] = None
    detail: Optional[str] = None


class SlideData(BaseModel):
    slide_number: int
    layout_type: Literal[
        "title_hero",
        "stats_kpis",
        "cards_grid",
        "chart_focus",
        "split_image_text",
        "timeline_process",
        "closing_contact"
    ] = "cards_grid"
    kicker: Optional[str] = None
    title: str
    subtitle: Optional[str] = None
    presenter: Optional[str] = None
    bullets: Optional[List[str]] = Field(default_factory=list)
    stats: Optional[List[StatItem]] = Field(default_factory=list)
    cards: Optional[List[CardItem]] = Field(default_factory=list)
    timeline_steps: Optional[List[TimelineItem]] = Field(default_factory=list)
    focus_areas: Optional[List[str]] = Field(default_factory=list)
    image_id: Optional[str] = None
    image_url: Optional[str] = None
    notes: Optional[str] = None


class SlideDeckSchema(BaseModel):
    deck_title: str
    deck_subtitle: Optional[str] = None
    footer_text: Optional[str] = None
    theme: ThemeConfig = Field(default_factory=ThemeConfig)
    slides: List[SlideData] = Field(default_factory=list)


class VisionAnalysisResult(BaseModel):
    image_id: str
    filename: str
    original_name: str
    width: int = 800
    height: int = 600
    role: Literal["chart", "logo", "hero", "team", "graphic"] = "graphic"
    summary: str
    detected_metrics: List[str] = Field(default_factory=list)
    chart_type: Optional[str] = None
    suggested_slide_title: Optional[str] = None


class QAJudgeReport(BaseModel):
    passed: bool = True
    score: int = 95
    feedback: str = "Presentation passes visual and executive hierarchy standards."
    clipping_risk_detected: bool = False
    checked_slides_count: int = 0
    suggested_adjustments: List[str] = Field(default_factory=list)
    applied_fixes: List[str] = Field(default_factory=list)
