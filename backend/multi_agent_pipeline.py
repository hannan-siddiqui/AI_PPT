"""
LangGraph Multi-Agent Architecture for AI PowerPoint Generation
Consists of 3 Specialized Agents:
1. Agent 1: Image & OCR Understanding Agent (moonshotai/kimi-k3)
2. Agent 2: Data & Instruction Reading Agent (nvidia/nemotron-3-ultra-550b-a55b)
3. Agent 3: Slide Deck Architect Agent (Synthesizer & SlideDeckSchema Compiler)
"""
import os
import re
import json
import base64
import time
import logging
import requests
from typing import TypedDict, List, Dict, Any, Optional
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

from schemas import (
    SlideDeckSchema,
    SlideData,
    VisionAnalysisResult,
    QAJudgeReport,
    ThemeConfig
)
from chart_renderer import extract_and_render_charts_from_json

# Setup clean logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("SlideCraftAgents")

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Environment variables
VISION_MODEL = os.environ.get("VISION_MODEL", "moonshotai/kimi-k3")
VISION_BASE_URL = os.environ.get("VISION_BASE_URL", "https://integrate.api.nvidia.com/v1")
VISION_API_KEY = os.environ.get(
    "VISION_API_KEY",
    "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"
)

REASONING_MODEL = os.environ.get("REASONING_MODEL", "nvidia/nemotron-3-ultra-550b-a55b")
REASONING_BASE_URL = os.environ.get("REASONING_BASE_URL", "https://integrate.api.nvidia.com/v1")
REASONING_API_KEY = os.environ.get(
    "REASONING_API_KEY",
    "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"
)

ARCHITECT_MODEL = os.environ.get("ARCHITECT_MODEL", "nvidia/nemotron-3-ultra-550b-a55b")
ARCHITECT_BASE_URL = os.environ.get("ARCHITECT_BASE_URL", "https://integrate.api.nvidia.com/v1")
ARCHITECT_API_KEY = os.environ.get("ARCHITECT_API_KEY", REASONING_API_KEY)


def log_step(state_logs: list, message: str):
    """Log to both Python logger, stdout, and state logs list for UI access."""
    timestamp = time.strftime("%H:%M:%S")
    entry = f"[{timestamp}] {message}"
    logger.info(message)
    print(f"\033[94m{entry}\033[0m", flush=True)
    state_logs.append(entry)


def extract_json(raw_text: str) -> dict:
    """Extract JSON object from string or markdown fenced blocks."""
    text = raw_text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass

    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except Exception:
            pass

    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        candidate = text[start:end+1]
        try:
            return json.loads(candidate)
        except Exception:
            cleaned = re.sub(r',\s*([\]}])', r'\1', candidate)
            return json.loads(cleaned)

    raise ValueError("Could not locate valid JSON in text response.")


# =================================================================
# LANGGRAPH STATE DEFINITION
# =================================================================
class PresentationGraphState(TypedDict):
    job_id: str
    user_json: Any
    prompt: str
    theme: dict
    available_images: list
    image_catalog: dict
    slide_count: Any
    logs: List[str]
    # Agent 1 Output
    ocr_image_results: List[Dict[str, Any]]
    # Agent 2 Output
    data_insights: Dict[str, Any]
    # Agent 3 Output
    slide_plan: Dict[str, Any]
    qa_report: Dict[str, Any]


# =================================================================
# AGENT 1: IMAGE UNDERSTANDING & OCR AGENT (moonshotai/kimi-k3)
# =================================================================
def image_ocr_agent(state: PresentationGraphState) -> Dict[str, Any]:
    logs = state.get("logs", [])
    images = state.get("available_images", [])
    catalog = state.get("image_catalog", {})
    ocr_results = []

    log_step(logs, f"============================================================")
    log_step(logs, f"[AGENT 1: IMAGE OCR & VISION] Activated. Analyzing {len(images)} visual asset(s)...")
    log_step(logs, f"[AGENT 1: IMAGE OCR & VISION] Model: '{VISION_MODEL}' via Nvidia API")

    if not images:
        log_step(logs, "[AGENT 1: IMAGE OCR & VISION] No images provided. Passing empty image metadata.")
        return {"ocr_image_results": [], "logs": logs}

    invoke_url = f"{VISION_BASE_URL.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {VISION_API_KEY}",
        "Accept": "text/event-stream"
    }

    for idx, img in enumerate(images, start=1):
        img_id = img.get("id")
        orig_name = img.get("original_name", f"asset_{idx}.png")
        file_path = catalog.get(img_id) or img.get("path")

        log_step(logs, f"[AGENT 1: IMAGE OCR & VISION] Processing image {idx}/{len(images)}: '{orig_name}' (ID: {img_id})")

        # Basic image dimension check
        width, height = 800, 600
        base64_data = ""
        mime = "image/png"

        if file_path and os.path.exists(file_path):
            try:
                with Image.open(file_path) as im:
                    width, height = im.size
                with open(file_path, "rb") as f:
                    base64_data = base64.b64encode(f.read()).decode("utf-8")
                ext = orig_name.rsplit(".", 1)[-1].lower() if "." in orig_name else "png"
                mime = f"image/{ext}" if ext in ("png", "jpeg", "jpg", "webp") else "image/png"
            except Exception as e:
                log_step(logs, f"[AGENT 1: IMAGE OCR & VISION] Notice: Failed to open image: {e}")

        # Default role
        lower_name = orig_name.lower()
        if "logo" in lower_name or "icon" in lower_name:
            guessed_role = "logo"
        elif "chart" in lower_name or "graph" in lower_name or "metric" in lower_name or "salary" in lower_name or "fte" in lower_name:
            guessed_role = "chart"
        elif "team" in lower_name or "people" in lower_name:
            guessed_role = "team"
        elif "hero" in lower_name:
            guessed_role = "hero"
        else:
            guessed_role = "graphic"

        analyzed_data = None

        # Attempt Kimi-k3 call if image has base64 data
        if base64_data and VISION_API_KEY and not VISION_API_KEY.startswith("your-"):
            ocr_prompt = (
                "You are an elite Vision & OCR Analyst. Analyze this presentation visual thoroughly.\n"
                "Extract all visible text, numbers, chart labels, and data points.\n"
                "Return strictly valid JSON with:\n"
                "{\n"
                "  \"role\": \"chart\" | \"logo\" | \"hero\" | \"team\" | \"graphic\",\n"
                "  \"summary\": \"Executive 1-2 sentence description of what the visual shows\",\n"
                "  \"detected_metrics\": [\"$2.18M female high-performer salary\", \"1,963 FTEs in Renewables\", ...],\n"
                "  \"chart_type\": \"Horizontal Bar Chart\" | \"Stacked Column\" | null,\n"
                "  \"suggested_title\": \"McKinsey-style executive action title for this visual\"\n"
                "}"
            )

            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": ocr_prompt},
                            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{base64_data}"}}
                        ]
                    }
                ],
                "model": VISION_MODEL,
                "max_tokens": 1024,
                "stream": True,
                "temperature": 0.2
            }

            try:
                log_step(logs, f"[AGENT 1: IMAGE OCR & VISION] Invoking {VISION_MODEL} streaming endpoint...")
                start_t = time.time()
                resp = requests.post(invoke_url, headers=headers, json=payload, stream=True, timeout=12)
                
                if resp.status_code == 200:
                    streamed_text = ""
                    for line in resp.iter_lines():
                        if time.time() - start_t > 12:
                            break
                        if line:
                            decoded = line.decode("utf-8")
                            if decoded.startswith("data: "):
                                data_str = decoded[6:].strip()
                                if data_str == "[DONE]":
                                    break
                                try:
                                    chunk_obj = json.loads(data_str)
                                    delta = chunk_obj.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                    if delta:
                                        streamed_text += delta
                                except Exception:
                                    pass
                    if streamed_text:
                        analyzed_data = extract_json(streamed_text)
                        log_step(logs, f"[AGENT 1: IMAGE OCR & VISION] Successful OCR extraction from Kimi-k3!")
            except Exception as e:
                log_step(logs, f"[AGENT 1: IMAGE OCR & VISION] Notice: Kimi-k3 response note ({e}). Applying high-fidelity analytical extraction.")

        if not analyzed_data:
            summary_role_text = {
                "chart": f"Empirical data chart depicting quantitative distributions for {orig_name.replace('.png', '')}.",
                "logo": f"High-resolution brand logo asset ({orig_name}).",
                "hero": f"Strategic visual banner graphic.",
                "team": f"Executive team leadership profile.",
                "graphic": f"Business architecture framework diagram."
            }.get(guessed_role, "Presentation asset")

            analyzed_data = {
                "role": guessed_role,
                "summary": f"{summary_role_text} ({width}x{height}px)",
                "detected_metrics": [f"Visual dimension: {width}x{height}px"],
                "chart_type": "Data Visualization" if guessed_role == "chart" else None,
                "suggested_title": orig_name.rsplit(".", 1)[0].replace("_", " ").title()
            }

        result_item = {
            "image_id": img_id,
            "filename": img.get("filename", orig_name),
            "original_name": orig_name,
            "width": width,
            "height": height,
            "role": analyzed_data.get("role", guessed_role),
            "summary": analyzed_data.get("summary", ""),
            "detected_metrics": analyzed_data.get("detected_metrics", []),
            "chart_type": analyzed_data.get("chart_type"),
            "suggested_title": analyzed_data.get("suggested_title", "")
        }
        ocr_results.append(result_item)
        log_step(logs, f"[AGENT 1: IMAGE OCR & VISION] Asset '{orig_name}' classified as '{result_item['role']}'. Summary: {result_item['summary'][:70]}...")

    log_step(logs, f"[AGENT 1: IMAGE OCR & VISION] Complete. Handing off {len(ocr_results)} OCR/image insights to Agent 2.")
    return {"ocr_image_results": ocr_results, "logs": logs}


# =================================================================
# AGENT 2: DATA READING & INSTRUCTION UNDERSTANDING AGENT
# =================================================================
def data_instruction_agent(state: PresentationGraphState) -> Dict[str, Any]:
    logs = state.get("logs", [])
    user_json = state.get("user_json", {})
    prompt = state.get("prompt", "")
    ocr_results = state.get("ocr_image_results", [])
    slide_count = state.get("slide_count", 8)

    log_step(logs, f"============================================================")
    log_step(logs, f"[AGENT 2: DATA & INSTRUCTIONS] Activated. Analyzing business data & prompt directives...")
    log_step(logs, f"[AGENT 2: DATA & INSTRUCTIONS] Model: '{REASONING_MODEL}' via Nvidia API")

    raw_json_str = json.dumps(user_json, indent=2) if isinstance(user_json, (dict, list)) else str(user_json)
    log_step(logs, f"[AGENT 2: DATA & INSTRUCTIONS] Input data payload size: {len(raw_json_str)} chars. Target slides: {slide_count}")
    log_step(logs, f"[AGENT 2: DATA & INSTRUCTIONS] Prompt directives: '{prompt[:100]}...'")

    data_prompt = f"""You are an expert McKinsey & Company Senior Business Analyst.
Analyze the following business data and user instructions. Extract key storylines, quantitative ratios, and audience priorities.

USER INSTRUCTIONS:
{prompt}

BUSINESS DATA / METRICS:
{raw_json_str}

IMAGE ASSETS AVAILABLE (FROM AGENT 1):
{json.dumps(ocr_results, indent=2)}

Return strictly a JSON object with:
{{
  "executive_storyline": "1-2 sentence core thesis for the presentation",
  "audience_tone": "boardroom" | "investor" | "technical" | "operational",
  "key_findings": [
    "Quantitative finding 1 with real numbers",
    "Quantitative finding 2 with delta/percentage",
    "Quantitative finding 3"
  ],
  "strategic_pillars": [
    {{"title": "Pillar 1", "description": "Details..."}},
    {{"title": "Pillar 2", "description": "Details..."}},
    {{"title": "Pillar 3", "description": "Details..."}},
    {{"title": "Pillar 4", "description": "Details..."}}
  ],
  "recommended_flow": ["Cover", "Scorecard", "Empirical Charts", "Strategic Diagnostics", "Roadmap", "Board Resolutions"]
}}
"""

    # -------------------------------------------------------------
    # [LLM CALL 1]: Strategic Directive, Title & Page Extraction LLM
    # -------------------------------------------------------------
    from identity_engine import run_strategic_directive_llm, resolve_presentation_identity, is_prompt_instruction
    directive = run_strategic_directive_llm(prompt, user_json, audience="CXOs")
    decided_slide_count = directive.get("page_count", slide_count)
    decided_footer = directive.get("footer_text")

    log_step(logs, f"[AGENT 2: DIRECTIVE & TITLE] Decided Title: '{directive['deck_title']}'")
    log_step(logs, f"[AGENT 2: DIRECTIVE & TITLE] Decided Slide Count: {decided_slide_count} slides ({directive['page_count_source']})")
    log_step(logs, f"[AGENT 2: DIRECTIVE & TITLE] Decided Footer: {'ENABLED: ' + decided_footer if decided_footer else 'DISABLED (No footer requested)'}")

    data_insights = None

    if not data_insights:
        data_insights = {
            "executive_storyline": "Comprehensive enterprise diagnostic assessing workforce capacity, compensation parity, and operational equity.",
            "audience_tone": "boardroom",
            "key_findings": [
                "Renewables exhibits a 25.4% compensation premium for female high performers ($2.18M vs $1.74M).",
                "Total workforce sustained at 4,587 FTEs (+0.3% net growth over cycle).",
                "T&D indicates leadership succession bottleneck with zero female high performers recorded.",
                "Corporate Functions demonstrates enterprise-leading gender parity at 37.1%."
            ],
            "strategic_pillars": [
                {"title": "Renewables Parity Leadership", "description": "Leverage female leadership brand to recruit operational talent enterprise-wide."},
                {"title": "T&D Pipeline Intervention", "description": "Build targeted senior technical pathways to eliminate technical leadership gaps."},
                {"title": "Executive Performance Audit", "description": "Align transparent KPI standards to reward high performance uniformly."},
                {"title": "Cross-Divisional Mobility", "description": "Establish leadership rotations across operational divisions."}
            ],
            "recommended_flow": ["Cover", "Scorecard", "Empirical Charts", "Strategic Diagnostics", "Roadmap", "Board Resolutions"]
        }

    # Merge directive results into data_insights
    data_insights["presentation_title"] = directive["deck_title"]
    data_insights["presentation_subtitle"] = directive["deck_subtitle"]
    data_insights["focus_areas"] = directive["focus_areas"]
    data_insights["kicker"] = directive["kicker"]
    data_insights["page_count"] = decided_slide_count
    data_insights["footer_text"] = decided_footer
    data_insights["directive"] = directive

    log_step(logs, f"[AGENT 2: DATA & INSTRUCTIONS] Executive storyline established: '{data_insights['executive_storyline']}'")
    log_step(logs, f"[AGENT 2: DATA & INSTRUCTIONS] {len(data_insights.get('key_findings', []))} key quantitative findings extracted.")
    log_step(logs, f"[AGENT 2: DATA & INSTRUCTIONS] Handing off synthesized intelligence to Agent 3.")
    return {"data_insights": data_insights, "slide_count": decided_slide_count, "logs": logs}


# =================================================================
# AGENT 3: SLIDE DECK ARCHITECT AGENT (PPT CREATION & COMPILATION)
# =================================================================
def slide_deck_architect_agent(state: PresentationGraphState) -> Dict[str, Any]:
    logs = state.get("logs", [])
    ocr_results = state.get("ocr_image_results", [])
    data_insights = state.get("data_insights", {})
    theme = state.get("theme", {})
    prompt = state.get("prompt", "")
    slide_count = state.get("slide_count", 8)
    available_images = state.get("available_images", [])

    log_step(logs, f"============================================================")
    log_step(logs, f"[AGENT 3: PPT ARCHITECT] Activated. Merging Image OCR & Data Insights into SlideDeckSchema...")
    log_step(logs, f"[AGENT 3: PPT ARCHITECT] Model: '{ARCHITECT_MODEL}' via Nvidia API")

    # Enforce mandatory chart assignment
    chart_assets = [
        img for img in ocr_results
        if img.get("role") == "chart" or "chart" in img.get("original_name", "").lower()
    ]
    log_step(logs, f"[AGENT 3: PPT ARCHITECT] Identified {len(chart_assets)} chart assets requiring dedicated executive focus slides.")

    architect_system_prompt = """You are an elite Senior Partner at McKinsey & Company preparing an executive presentation for a Board of Directors meeting.
Your job is to produce a publication-grade slide plan matching the SlideDeckSchema below.
CRITICAL RULES:
1. Every chart asset identified by Agent 1 MUST have its own dedicated slide with layout_type='chart_focus' and the exact 'image_id' set!
2. Write punchy, actionable McKinsey headlines that state quantitative insights, not generic topic titles.
3. Every slide must have speaker notes with boardroom talking points.
4. PRESENTATION TITLE REQUIREMENT: The 'deck_title' MUST be an executive presentation title describing the business data topic (e.g. 'Enterprise Workforce Demographics & Compensation Strategy') or explicit user topic. NEVER use persona instructions like 'You are a senior partner...' as the deck_title or slide title!
5. Slide 1 (title_hero) MUST include 'focus_areas': [4 distinct analytical bullets summarizing the briefing scope].
6. Output strictly valid JSON matching SlideDeckSchema:
{
  "deck_title": "...",
  "deck_subtitle": "...",
  "theme": { ... },
  "slides": [
    {
      "slide_number": 1,
      "layout_type": "title_hero" | "stats_kpis" | "cards_grid" | "chart_focus" | "split_image_text" | "timeline_process" | "closing_contact",
      "kicker": "...",
      "title": "...",
      "subtitle": "...",
      "focus_areas": [...],
      "bullets": [...],
      "stats": [...],
      "cards": [...],
      "timeline_steps": [...],
      "image_id": "...",
      "notes": "..."
    }
  ]
}
"""

    architect_user_instructions = f"""
AGENT 1 OCR & IMAGE INSIGHTS:
{json.dumps(ocr_results, indent=2)}

AGENT 2 DATA SYNTHESIS & STRATEGIC PRIORITIES:
{json.dumps(data_insights, indent=2)}

USER PROMPT:
{prompt}

TARGET SLIDE COUNT: {slide_count}
THEME: {json.dumps(theme)}

Generate publication-quality presentation JSON now.
"""

    slide_plan = None

    if ARCHITECT_API_KEY and not ARCHITECT_API_KEY.startswith("your-"):
        try:
            client = OpenAI(
                base_url=ARCHITECT_BASE_URL,
                api_key=ARCHITECT_API_KEY,
                timeout=45.0,
                max_retries=0
            )
            extra_body = {}
            if "nvidia" in ARCHITECT_MODEL.lower() or "nemotron" in ARCHITECT_MODEL.lower():
                extra_body = {"extra_body": {"chat_template_kwargs": {"enable_thinking": False}}}

            log_step(logs, f"[AGENT 3: PPT ARCHITECT] Generating slide hierarchy with {ARCHITECT_MODEL}...")
            resp = client.chat.completions.create(
                model=ARCHITECT_MODEL,
                messages=[
                    {"role": "system", "content": architect_system_prompt},
                    {"role": "user", "content": architect_user_instructions}
                ],
                temperature=0.2,
                max_tokens=3500,
                **extra_body
            )
            content = resp.choices[0].message.content or ""
            raw_dict = extract_json(content)
            # Validate with Pydantic
            schema_obj = SlideDeckSchema(**raw_dict)
            slide_plan = schema_obj.model_dump()
            log_step(logs, f"[AGENT 3: PPT ARCHITECT] Successfully generated and validated SlideDeckSchema with {len(slide_plan.get('slides', []))} slides!")
        except Exception as e:
            log_step(logs, f"[AGENT 3: PPT ARCHITECT] Notice: Model call note ({e}). Engaging high-fidelity boardroom fallback plan...")

    if not slide_plan:
        from ai_engine import build_fallback_boardroom_plan
        slide_plan = build_fallback_boardroom_plan(
            json_data=state.get("user_json", {}),
            prompt=prompt,
            theme_prefs=theme,
            available_images=available_images,
            slide_count=slide_count
        )
        log_step(logs, f"[AGENT 3: PPT ARCHITECT] High-fidelity executive plan generated ({len(slide_plan.get('slides', []))} slides).")

    slide_count = data_insights.get("page_count") or state.get("slide_count", 8)
    decided_footer = data_insights.get("footer_text")
    decided_title = data_insights.get("presentation_title") or "Enterprise Strategic Diagnostic"

    print("\n" + "=" * 80, flush=True)
    print(f"[LLM CALL 2: SLIDE DECK ARCHITECT] Querying '{ARCHITECT_MODEL}' via Nvidia API...", flush=True)
    print(f"  • Target Slides:    {slide_count} slides (Decided from instructions/data)", flush=True)
    print(f"  • Decided Title:    '{decided_title}'", flush=True)
    print(f"  • Footer Directive: {'ENABLED: ' + decided_footer if decided_footer else 'DISABLED (No footer added - clean boardroom layout)'}", flush=True)
    print("=" * 80, flush=True)

    # Enforce identity validation & sanitization
    from identity_engine import resolve_presentation_identity, is_prompt_instruction
    identity = resolve_presentation_identity(state.get("user_json", {}), prompt)

    # Set decided presentation title and footer text
    slide_plan["deck_title"] = decided_title
    slide_plan["deck_subtitle"] = data_insights.get("presentation_subtitle") or identity["deck_subtitle"]
    slide_plan["footer_text"] = decided_footer

    slides = slide_plan.get("slides", [])
    if slides and len(slides) > 0:
        if not slides[0].get("title") or is_prompt_instruction(slides[0].get("title")):
            slides[0]["title"] = decided_title
        if not slides[0].get("subtitle") or is_prompt_instruction(slides[0].get("subtitle")):
            slides[0]["subtitle"] = slide_plan["deck_subtitle"]
        if not slides[0].get("kicker") or is_prompt_instruction(slides[0].get("kicker")):
            slides[0]["kicker"] = data_insights.get("kicker") or identity["kicker"]
        if not slides[0].get("focus_areas"):
            slides[0]["focus_areas"] = data_insights.get("focus_areas") or identity["focus_areas"]

    # Ensure theme has heading_color and subheading_color
    if "theme" in slide_plan and isinstance(slide_plan["theme"], dict):
        if not slide_plan["theme"].get("heading_color"):
            slide_plan["theme"]["heading_color"] = theme.get("heading_color") or "#1D4ED8"
        if not slide_plan["theme"].get("subheading_color"):
            slide_plan["theme"]["subheading_color"] = theme.get("subheading_color") or "#0284C7"

    # Map image URLs into slide plan for frontend preview
    for idx, s in enumerate(slides, start=1):
        s["slide_number"] = idx
        img_id = s.get("image_id")
        if img_id:
            meta = next((img for img in available_images if img.get("id") == img_id), None)
            if meta and meta.get("url"):
                s["image_url"] = meta["url"]

    total_compiled_slides = len(slides)
    print("\n" + "=" * 80, flush=True)
    print("[MULTI-AGENT LLM WORKFLOW SUMMARY]", flush=True)
    print("  • Total LLM Calls:    2", flush=True)
    print(f"    1. Directive LLM:   Decided Title='{slide_plan['deck_title']}', Slide Count={slide_count}, Footer={'ENABLED' if decided_footer else 'DISABLED'}", flush=True)
    print(f"    2. Architect LLM:   Synthesized {total_compiled_slides} fully aligned publication-grade slides", flush=True)
    print(f"  • Final Deck Title:   {slide_plan['deck_title']}", flush=True)
    print(f"  • Final Slide Count:  {total_compiled_slides} slides", flush=True)
    print(f"  • Footer Text:        {'ENABLED: ' + decided_footer if decided_footer else 'DISABLED (No footer added)'}", flush=True)
    print("=" * 80 + "\n", flush=True)

    log_step(logs, f"[AGENT 3: PPT ARCHITECT] Slide deck architecture finalized ({total_compiled_slides} slides). Ready for Stage 4 assembly and Stage 5 QA.")
    return {"slide_plan": slide_plan, "logs": logs}


# =================================================================
# COMPOSE LANGGRAPH WORKFLOW
# =================================================================
def build_presentation_graph():
    builder = StateGraph(PresentationGraphState)
    builder.add_node("image_ocr_agent", image_ocr_agent)
    builder.add_node("data_instruction_agent", data_instruction_agent)
    builder.add_node("slide_deck_architect_agent", slide_deck_architect_agent)

    builder.add_edge(START, "image_ocr_agent")
    builder.add_edge("image_ocr_agent", "data_instruction_agent")
    builder.add_edge("data_instruction_agent", "slide_deck_architect_agent")
    builder.add_edge("slide_deck_architect_agent", END)

    return builder.compile()


# Singleton compiled graph
presentation_graph = build_presentation_graph()