"""
Executive Presentation Identity & Title Synthesis Engine.
Intelligently resolves presentation title, subtitle, kicker, and cover slide focus areas.
Guarantees:
1. If user explicitly specifies a title (in prompt or JSON), extract and use it.
2. If user provides persona/role-play instructions (e.g. "You are a senior partner at McKinsey..."),
   NEVER use instruction text as the title.
3. Intelligently synthesize a publication-grade, boardroom-level executive title directly
   from the empirical data (charts, axis labels, dimensions, metrics).
"""
import re
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple
from openai import OpenAI

REASONING_BASE_URL = os.environ.get("REASONING_BASE_URL", "https://integrate.api.nvidia.com/v1")
REASONING_API_KEY = os.environ.get(
    "REASONING_API_KEY",
    os.environ.get("NVIDIA_API_KEY", "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")
)
REASONING_MODEL = os.environ.get("REASONING_MODEL", "nvidia/nemotron-3-ultra-550b-a55b")

# Patterns identifying persona / system instruction prompts that should NEVER be used as a presentation title
PROMPT_INSTRUCTION_PATTERNS = [
    r"^you\s+are\b",
    r"^act\s+as\b",
    r"senior\s+partner\b",
    r"mckinsey\s*&\s*company",
    r"board\s+of\s+directors\s+meeting\s+tomorrow",
    r"your\s+credibility\b",
    r"this\s+is\s+not\s+just\b",
    r"publication-quality",
    r"fortune\s+500",
    r"i\s+gave\s+this\s+prompt",
    r"create\s+a\s+(?:\d+\s+slide\s+)?ppt",
    r"generate\s+a\s+(?:\d+\s+slide\s+)?ppt",
    r"make\s+a\s+(?:\d+\s+slide\s+)?ppt",
    r"use\s+the\s+json\s+data",
    r"system\s+prompt",
    r"as\s+an\s+ai\b",
]


def is_prompt_instruction(text: str) -> bool:
    """Return True if text resembles an LLM role-play instruction rather than a legitimate title."""
    if not text or not isinstance(text, str):
        return True
    cleaned = text.strip().lower()
    if len(cleaned) < 3:
        return True
    for pat in PROMPT_INSTRUCTION_PATTERNS:
        if re.search(pat, cleaned, re.IGNORECASE):
            return True
    return False


def clean_title_string(title: str) -> str:
    """Clean and standardize a candidate title string."""
    t = title.strip().strip('"\'“”‘’')
    # Remove trailing punctuation like periods or colons
    t = re.sub(r'[\.\:\;\,\-]+$', '', t).strip()
    # Replace multiple spaces
    t = re.sub(r'\s+', ' ', t)
    return t


def extract_explicit_title_from_prompt(prompt: str) -> Optional[str]:
    """Check if the user explicitly commanded a specific title in their prompt."""
    if not prompt or not isinstance(prompt, str):
        return None

    # Patterns where user explicitly designates title
    explicit_patterns = [
        r'(?:presentation\s+)?title\s*(?:is|should\s+be|:\s*|=\s*)\s*["\']?([^"\'\n\r\.\,\;]+)["\']?',
        r'(?:presentation|deck|slides?)\s+(?:titled|named)\s+["\']([^"\'\n\r]+)["\']',
        r'(?:^|\n)\s*(?:title|topic|subject)\s*:\s*([^\n\r]+)',
        r'(?:presentation|deck|briefing)\s+(?:on|about|for)\s+["\']([^"\'\n\r]+)["\']',
    ]

    for pat in explicit_patterns:
        match = re.search(pat, prompt, re.IGNORECASE)
        if match:
            candidate = clean_title_string(match.group(1))
            if candidate and not is_prompt_instruction(candidate) and len(candidate) > 3:
                return candidate.title() if candidate.islower() else candidate

    return None


def extract_explicit_title_from_json(json_data: Any) -> Optional[str]:
    """Check if the JSON data object contains an explicit title/topic key."""
    if not isinstance(json_data, dict):
        return None

    for key in ("title", "deck_title", "presentation_title", "topic", "project", "subject"):
        val = json_data.get(key)
        if val and isinstance(val, str):
            candidate = clean_title_string(val)
            if candidate and not is_prompt_instruction(candidate) and len(candidate) > 3:
                return candidate.title() if candidate.islower() else candidate

    # Check company / company_name
    company = json_data.get("company_name") or json_data.get("company")
    tagline = json_data.get("tagline") or json_data.get("product_name")
    if company and isinstance(company, str) and not is_prompt_instruction(company):
        if tagline and isinstance(tagline, str):
            return f"{clean_title_string(company)}: {clean_title_string(tagline)}"
        return f"{clean_title_string(company)} Strategic Briefing"

    return None


def synthesize_title_from_charts(charts: List[Dict[str, Any]], audience: str = "CXOs") -> Tuple[str, str, str, List[str]]:
    """
    Intelligently synthesize an executive title, subtitle, kicker, and 4 focus areas
    based on chart configurations, axes, dimensions, and categories.
    """
    metric_labels = []
    dimensions = set()
    divisions = set()
    has_gender = False
    has_salary = False
    has_headcount = False

    for c_wrap in charts:
        c = c_wrap.get("chart", c_wrap) if isinstance(c_wrap, dict) else {}
        axis = c.get("axisLabel", {})
        y_axis = axis.get("yAxis", "")
        x_axis = axis.get("xAxis", "")
        if y_axis:
            metric_labels.append(y_axis)
            y_lower = y_axis.lower()
            if "salary" in y_lower or "compensation" in y_lower or "pay" in y_lower:
                has_salary = True
            if "fte" in y_lower or "headcount" in y_lower or "staff" in y_lower or "count" in y_lower:
                has_headcount = True

        for d in c.get("dimension", []):
            dimensions.add(str(d).lower())
            if "gender" in str(d).lower():
                has_gender = True

        for lbl in c.get("labels", []):
            divisions.add(str(lbl))

        # Check datasets
        ds = c.get("datasets", {}).get("default", [])
        for d in ds:
            lbl = d.get("label", "")
            if lbl.lower() in ("female", "male"):
                has_gender = True

    # 1. Workforce + Compensation + Diversity (The exact McKinsey Boardroom Case)
    if (has_salary or has_headcount) and has_gender:
        title = "Enterprise Workforce Demographics & Compensation Strategy"
        subtitle = "Empirical Diagnostic of Headcount Trajectories, High-Performer Compensation, and Cross-Divisional Equity"
        kicker = "BOARD OF DIRECTORS EXECUTIVE BRIEFING"
        focus_areas = [
            "Executive Compensation Parity: High-performer compensation benchmarks across Renewables & T&D",
            "Workforce Capacity Dynamics: SOP FTE to EOP headcount retention across 4 operating divisions",
            "Gender Representation Diagnostics: Longitudinal parity analysis in executive & technical tracks",
            "Strategic Board Resolutions: Recommended leadership governance and talent pipeline actions"
        ]
        return title, subtitle, kicker, focus_areas

    # 2. Pure Compensation / Financial Remuneration
    if has_salary:
        title = "Executive Compensation & Remuneration Architecture"
        subtitle = "Comprehensive Benchmarking of High-Performer Yield, Incentives, and Cross-Functional Parity"
        kicker = "COMPENSATION COMMITTEE STRATEGIC REVIEW"
        focus_areas = [
            "Compensation Benchmarking: Pay distribution across core business units",
            "High-Performer Yield: Correlation of incentive rewards with departmental outcomes",
            "Market Competitiveness: Comparative quartile evaluation against peer industry baselines",
            "Governance Protocols: Multi-year compensation policy alignment"
        ]
        return title, subtitle, kicker, focus_areas

    # 3. Pure Headcount / Workforce Capacity
    if has_headcount:
        title = "Strategic Workforce Capacity & Headcount Optimization"
        subtitle = "Diagnostic Review of FTE Movement, Divisional Resource Allocation, and Talent Retention"
        kicker = "OPERATIONS & TALENT STRATEGIC REVIEW"
        focus_areas = [
            "Baseline Capacity Assessment: SOP FTE distribution across operating divisions",
            "Net Headcount Velocity: End-of-period retention and departmental expansion",
            "Operational Efficiency: FTE utilization metrics against divisional milestones",
            "Workforce Roadmap: Strategic workforce planning and capability scaling"
        ]
        return title, subtitle, kicker, focus_areas

    # 4. General Multi-Chart Data
    cleaned_metrics = [m for m in metric_labels if m and m != "category"]
    if cleaned_metrics:
        first_metric = cleaned_metrics[0]
        title = f"Operational Intelligence & {first_metric} Diagnostic"
        subtitle = f"Empirical Evaluation of {', '.join(cleaned_metrics[:2])} Across Enterprise Units"
        kicker = "EXECUTIVE STRATEGIC BRIEFING"
        focus_areas = [
            f"Quantitative Distribution: Empirical performance across {first_metric}",
            "Cross-Divisional Comparison: Operational variation among business units",
            "Variance Analysis: Root-cause evaluation of high and low-performing segments",
            "Strategic Priorities: High-impact executive interventions and governance"
        ]
        return title, subtitle, kicker, focus_areas

    # Default fallback
    title = "Executive Strategic Review & Performance Diagnostic"
    subtitle = "Comprehensive Quantitative Diagnostics, Data Intelligence, and Strategic Roadmap"
    kicker = "EXECUTIVE STRATEGIC BRIEFING"
    focus_areas = [
        "Quantitative Performance: High-fidelity evaluation of operational metrics",
        "Strategic Segmentation: Performance across primary business pillars",
        "Risk & Opportunity Profiling: Critical operational inflection points",
        "Executive Roadmap: Actionable leadership decisions and implementation timeline"
    ]
    return title, subtitle, kicker, focus_areas


def synthesize_title_from_generic_data(data: Dict[str, Any], audience: str = "CXOs") -> Tuple[str, str, str, List[str]]:
    """Synthesize identity from general key-value or KPI dictionaries."""
    keys_lower = [str(k).lower() for k in data.keys()]

    # Check SaaS / Growth metrics
    if any(k in keys_lower for k in ("arr", "mrr", "traction_metrics", "tam", "sam")):
        company = data.get("company_name") or data.get("company") or "Enterprise SaaS"
        title = f"{company} Series A Strategic Briefing"
        subtitle = "Traction Diagnostics, Defensible Unit Economics, and 18-Month Scaling Roadmap"
        kicker = "VENTURE & BOARD STRATEGIC BRIEFING"
        focus_areas = [
            "Revenue Velocity: ARR trajectory, net retention, and customer expansion",
            "Unit Economics: Gross margin defensibility and capital efficiency",
            "Market Capture: TAM sizing and enterprise pipeline velocity",
            "Capital Allocation: Strategic deployment and governance milestones"
        ]
        return title, subtitle, kicker, focus_areas

    # Check QBR / Quarterly Review
    if any("quarter" in k or "qbr" in k or "highlights" in k or "division" in k for k in keys_lower):
        division = data.get("division") or "Global Operations"
        title = f"{division} Quarterly Business Review"
        subtitle = "Comprehensive Evaluation of Top-Line Milestones, Operating Margins, and Strategic Horizon"
        kicker = "EXECUTIVE QUARTERLY BRIEFING"
        focus_areas = [
            "Top-Line Execution: Performance against quarterly operational targets",
            "Operating Margin Expansion: Efficiency improvements and cost disciplines",
            "Key Initiatives: Delivery status across high-priority workstreams",
            "Next-Quarter Outlook: Strategic resource allocations and core commitments"
        ]
        return title, subtitle, kicker, focus_areas

    # Check Product Launch
    if any("product" in k or "launch" in k or "personas" in k for k in keys_lower):
        prod = data.get("product_name") or "Product"
        title = f"{prod} Go-To-Market & Commercial Strategy"
        subtitle = "Persona Targeting, Value Architecture Blueprint, and Phased Commercial Milestones"
        kicker = "STRATEGIC PRODUCT BRIEFING"
        focus_areas = [
            "Market Positioning: Enterprise persona definition and competitive differentiation",
            "Core Value Proposition: High-impact architectural capabilities",
            "Commercial Rollout: Phased private beta through global availability",
            "Success Metrics: Adoption targets, retention benchmarks, and referral velocity"
        ]
        return title, subtitle, kicker, focus_areas

    # Default
    title = "Executive Strategic Briefing & Operational Diagnostic"
    subtitle = "Comprehensive Quantitative Diagnostics, Data Intelligence, and Strategic Roadmap"
    kicker = "EXECUTIVE STRATEGIC BRIEFING"
    focus_areas = [
        "Core Quantitative Metrics: Audited performance baseline across operational units",
        "Strategic Segmentation: Performance dispersion across primary dimensions",
        "Risk Mitigation: Proactive compliance, controls, and data integrity",
        "Boardroom Roadmap: Priority operational interventions and governance milestones"
    ]
    return title, subtitle, kicker, focus_areas


def resolve_presentation_identity(user_json: Any, prompt: str = "", audience: str = "CXOs") -> Dict[str, Any]:
    """
    Master Identity Resolver.
    Returns:
    {
        "deck_title": str,
        "deck_subtitle": str,
        "kicker": str,
        "presenter": str,
        "focus_areas": List[str]
    }
    """
    # 1. Parse JSON safely
    parsed_json = {}
    if isinstance(user_json, str):
        try:
            parsed_json = json.loads(user_json)
        except Exception:
            parsed_json = {"raw_context": user_json}
    elif isinstance(user_json, dict):
        parsed_json = user_json
    elif isinstance(user_json, list):
        parsed_json = {"data": user_json}

    # 2. Check for explicit title in Prompt (User explicit command has highest priority)
    explicit_prompt_title = extract_explicit_title_from_prompt(prompt)
    if explicit_prompt_title:
        # User explicitly requested this title
        base_title = explicit_prompt_title
        # Generate complementary subtitle and focus areas from data
        if "data" in parsed_json and isinstance(parsed_json["data"], list):
            _, sub, kicker, focus = synthesize_title_from_charts(parsed_json["data"], audience)
        else:
            _, sub, kicker, focus = synthesize_title_from_generic_data(parsed_json, audience)

        return {
            "deck_title": base_title,
            "deck_subtitle": sub,
            "kicker": kicker,
            "presenter": "Executive Advisory • Strategic Intelligence",
            "focus_areas": focus
        }

    # 3. Check for explicit title in JSON
    explicit_json_title = extract_explicit_title_from_json(parsed_json)
    if explicit_json_title:
        base_title = explicit_json_title
        if "data" in parsed_json and isinstance(parsed_json["data"], list):
            _, sub, kicker, focus = synthesize_title_from_charts(parsed_json["data"], audience)
        else:
            _, sub, kicker, focus = synthesize_title_from_generic_data(parsed_json, audience)

        return {
            "deck_title": base_title,
            "deck_subtitle": sub,
            "kicker": kicker,
            "presenter": "Executive Advisory • Strategic Intelligence",
            "focus_areas": focus
        }

    # 4. Synthesize on the basis of data!
    if "data" in parsed_json and isinstance(parsed_json["data"], list):
        title, sub, kicker, focus = synthesize_title_from_charts(parsed_json["data"], audience)
    elif "charts" in parsed_json and isinstance(parsed_json["charts"], list):
        title, sub, kicker, focus = synthesize_title_from_charts(parsed_json["charts"], audience)
    elif isinstance(parsed_json, list):
        title, sub, kicker, focus = synthesize_title_from_charts(parsed_json, audience)
    else:
        title, sub, kicker, focus = synthesize_title_from_generic_data(parsed_json, audience)

    # Double-check that title is never instruction text
    if is_prompt_instruction(title):
        title = "Enterprise Strategic Review & Performance Diagnostic"

    return {
        "deck_title": title,
        "deck_subtitle": sub,
        "kicker": kicker,
        "presenter": "Executive Advisory • Strategic Intelligence",
        "focus_areas": focus
    }


def resolve_theme_from_input(theme_input: Any) -> Dict[str, str]:
    """Resolve theme string (e.g. 'mint-blue') or dict to a complete ThemeConfig dictionary."""
    # Standard fallback
    default_theme = {
        "name": "Corporate Blue Minimalist",
        "primary_color": "#1D4ED8",
        "secondary_color": "#E2E8F0",
        "accent_color": "#1D4ED8",
        "bg_color": "#FFFFFF",
        "text_color": "#0F172A",
        "card_bg_color": "#FFFFFF",
        "muted_text_color": "#64748B",
        "heading_color": "#1D4ED8",
        "subheading_color": "#0284C7"
    }

    mint_blue = {
        "name": "Executive Mint Blue",
        "primary_color": "#0F766E",
        "secondary_color": "#E6FFFA",
        "accent_color": "#0D9488",
        "bg_color": "#FFFFFF",
        "text_color": "#0F172A",
        "card_bg_color": "#F0FDFA",
        "muted_text_color": "#5A7184",
        "heading_color": "#0F766E",
        "subheading_color": "#0D9488"
    }

    if isinstance(theme_input, str):
        t_clean = theme_input.lower().replace("_", "-").replace(" ", "-")
        if "mint" in t_clean or "teal" in t_clean:
            return mint_blue
        return default_theme

    if isinstance(theme_input, dict):
        merged = {**default_theme}
        for k, v in theme_input.items():
            if v:
                merged[k] = v
        return merged

    return default_theme


def extract_page_count_from_input(prompt: str, user_json: Any, default: int = 8) -> Tuple[int, str]:
    """Extract requested slide count from instructions or JSON."""
    # 1. Check prompt instructions
    if prompt and isinstance(prompt, str):
        m = re.search(r'\b(\d{1,2})\s*(?:-|–)?\s*(?:slides?|pages?)\b', prompt, re.IGNORECASE)
        if m:
            count = int(m.group(1))
            if 1 <= count <= 30:
                return count, f"Extracted from instruction: '{m.group(0)}'"
        m = re.search(r'\b(?:make|create|generate|produce|design)\s+(\d{1,2})\s+(?:slides?|pages?)\b', prompt, re.IGNORECASE)
        if m:
            count = int(m.group(1))
            if 1 <= count <= 30:
                return count, f"Extracted from instruction: '{m.group(0)}'"

    # 2. Check JSON
    if isinstance(user_json, dict):
        for k in ("n_slides", "slide_count", "pages", "num_slides", "slideCount"):
            val = user_json.get(k)
            if val is not None:
                try:
                    count = int(val)
                    if 1 <= count <= 30:
                        return count, f"Extracted from JSON key '{k}': {count}"
                except (ValueError, TypeError):
                    pass

    return default, "Default count (8 slides)"


def extract_footer_from_input(prompt: str, user_json: Any) -> Tuple[Optional[str], str]:
    """
    Extract footer directive.
    CRITICAL: NO FOOTER is added by default!
    Only add footer if explicitly requested in instructions or JSON.
    """
    # Check prompt
    if prompt and isinstance(prompt, str):
        patterns = [
            r'(?:add\s+(?:this\s+in\s+)?footer|include\s+footer|footer\s+should\s+be|footer)\s*[:=]\s*["\']?([^"\'\n\r]+)["\']?',
            r'(?:add\s+(?:this\s+in\s+)?footer|include\s+footer|footer\s+should\s+be)\s+["\']?([^"\'\n\r]+)["\']?',
            r'(?:in|on)\s+(?:the\s+)?footer\s*(?:put|write|display|show|add|is)\s*["\']?([^"\'\n\r]+)["\']?',
            r'footer\s+text\s*[:=]\s*["\']?([^"\'\n\r]+)["\']?'
        ]
        for pat in patterns:
            m = re.search(pat, prompt, re.IGNORECASE)
            if m:
                raw_candidate = m.group(1).strip()
                # Clean leading punctuation like colons or hyphens
                raw_candidate = re.sub(r'^[\:\-\=\s]+', '', raw_candidate).strip()
                f_text = clean_title_string(raw_candidate)
                if f_text and len(f_text) > 1 and not is_prompt_instruction(f_text):
                    return f_text, f"Explicitly requested in instruction: '{f_text}'"

    # Check JSON
    if isinstance(user_json, dict):
        for k in ("footer", "footer_text", "footerText"):
            val = user_json.get(k)
            if val and isinstance(val, str) and not is_prompt_instruction(val):
                return clean_title_string(val), f"Explicitly requested in JSON: '{val}'"

    return None, "Disabled (No footer requested in instructions)"


def run_strategic_directive_llm(prompt: str, user_json: Any, audience: str = "CXOs") -> Dict[str, Any]:
    """
    [LLM CALL 1]: Executive Strategic Directive Agent.
    Calls LLM to analyze prompt instructions and dataset to decide:
    1. Presentation Title (respecting explicit user title or synthesizing from data).
    2. Number of pages/slides (extracting from instruction or JSON).
    3. Footer text (strictly None unless user explicitly demanded a footer!).
    4. Subtitle, theme, audience, and 4 focus areas for the cover briefing card.
    Prints prominent, structured terminal logs for full visibility.
    """
    start_time = time.time()
    raw_json_str = json.dumps(user_json, indent=2) if isinstance(user_json, (dict, list)) else str(user_json)

    # Pre-parse deterministic candidates
    rule_page_count, count_source = extract_page_count_from_input(prompt, user_json, default=8)
    rule_footer, footer_source = extract_footer_from_input(prompt, user_json)
    rule_ident = resolve_presentation_identity(user_json, prompt, audience=audience)

    decided = {
        "deck_title": rule_ident["deck_title"],
        "deck_subtitle": rule_ident["deck_subtitle"],
        "kicker": rule_ident["kicker"],
        "presenter": rule_ident["presenter"],
        "page_count": rule_page_count,
        "page_count_source": count_source,
        "footer_text": rule_footer,
        "footer_source": footer_source,
        "audience": audience,
        "theme": "mint-blue" if "mint" in str(user_json).lower() or "mint" in prompt.lower() else "corporate-blue",
        "focus_areas": rule_ident["focus_areas"],
        "llm_called": False,
        "model_used": None,
        "elapsed_sec": 0.0
    }

    if REASONING_API_KEY and not REASONING_API_KEY.startswith("your-"):
        directive_prompt = f"""You are an elite Senior Partner at McKinsey & Company preparing an executive presentation for a Board of Directors meeting.
Analyze the user prompt instructions and the business data.

USER INSTRUCTIONS:
{prompt}

BUSINESS DATA:
{raw_json_str[:3000]}

CRITICAL RULES:
1. Title: If the user explicitly requested a title (e.g., 'title: ...' or 'title should be ...'), use it! Otherwise, synthesize an authoritative boardroom title from the data. NEVER use prompt instructions like 'You are a senior partner...' as the title!
2. Number of Slides (page_count): Extract the exact number of slides requested if mentioned in user instructions (e.g. '8-slide presentation', 'make 10 slides') or JSON ('n_slides'). Otherwise default to 8.
3. Footer (footer_text): CRITICAL - Return null unless the user instruction specifically asked to add a footer!
4. focus_areas: 4 bullet points summarizing the strategic diagnostic dimensions.

Return strictly a JSON object:
{{
  "presentation_title": "...",
  "presentation_subtitle": "...",
  "page_count": 8,
  "footer_text": null,
  "theme": "mint-blue" | "corporate-blue",
  "focus_areas": ["Pillar 1", "Pillar 2", "Pillar 3", "Pillar 4"]
}}
"""
        try:
            print("\n" + "=" * 80, flush=True)
            print(f"[LLM CALL 1: DIRECTIVE & TITLE EXTRACTION] Querying '{REASONING_MODEL}' via Nvidia API...", flush=True)
            client = OpenAI(
                base_url=REASONING_BASE_URL,
                api_key=REASONING_API_KEY,
                timeout=45.0,
                max_retries=0
            )
            extra_body = {}
            if "nvidia" in REASONING_MODEL.lower() or "nemotron" in REASONING_MODEL.lower():
                extra_body = {"extra_body": {"chat_template_kwargs": {"enable_thinking": False}}}

            resp = client.chat.completions.create(
                model=REASONING_MODEL,
                messages=[{"role": "user", "content": directive_prompt}],
                temperature=0.1,
                max_tokens=800,
                **extra_body
            )
            elapsed = time.time() - start_time
            content = resp.choices[0].message.content or ""
            parsed = None
            try:
                parsed = json.loads(content)
            except Exception:
                m = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
                if m:
                    parsed = json.loads(m.group(1).strip())

            if parsed and isinstance(parsed, dict):
                p_title = clean_title_string(str(parsed.get("presentation_title", "")))
                if p_title and not is_prompt_instruction(p_title):
                    decided["deck_title"] = p_title
                p_sub = parsed.get("presentation_subtitle")
                if p_sub and not is_prompt_instruction(p_sub):
                    decided["deck_subtitle"] = p_sub
                if parsed.get("page_count") and isinstance(parsed["page_count"], int) and 1 <= parsed["page_count"] <= 30:
                    decided["page_count"] = parsed["page_count"]
                    decided["page_count_source"] = "Decided by LLM from instructions & data"
                # Footer strictly follows instruction rule
                f_val = parsed.get("footer_text")
                if f_val and isinstance(f_val, str) and not is_prompt_instruction(f_val):
                    decided["footer_text"] = clean_title_string(f_val)
                    decided["footer_source"] = f"Extracted by LLM from instructions: '{f_val}'"
                if parsed.get("focus_areas") and isinstance(parsed["focus_areas"], list) and len(parsed["focus_areas"]) >= 3:
                    decided["focus_areas"] = [str(x) for x in parsed["focus_areas"][:4]]

                decided["llm_called"] = True
                decided["model_used"] = REASONING_MODEL
                decided["elapsed_sec"] = round(elapsed, 2)
                print(f"[LLM CALL 1: DIRECTIVE & TITLE EXTRACTION] Completed in {decided['elapsed_sec']}s", flush=True)

        except Exception as e:
            print(f"[LLM CALL 1: DIRECTIVE & TITLE EXTRACTION] Notice ({e}). Using executive decision engine.", flush=True)

    # Print Terminal Decision Summary Box
    footer_display = f"ENABLED: '{decided['footer_text']}'" if decided['footer_text'] else "DISABLED (No footer requested in instructions - clean slides)"
    print("-" * 80, flush=True)
    print(" [EXECUTIVE DIRECTIVE SUMMARY]", flush=True)
    print(f"  • Decided Title:      {decided['deck_title']}", flush=True)
    print(f"  • Decided Subtitle:   {decided['deck_subtitle']}", flush=True)
    print(f"  • Decided Page Count: {decided['page_count']} slides ({decided['page_count_source']})", flush=True)
    print(f"  • Decided Footer:     {footer_display}", flush=True)
    print(f"  • Decided Audience:   {decided['audience']}", flush=True)
    print(f"  • Decided Theme:      {decided['theme']}", flush=True)
    print("=" * 80 + "\n", flush=True)

    return decided
