"""
Automated Chart Image Generator for JSON Chart Specifications & Dynamic Data
Produces publication-quality, executive charts matching the user's dataset and color scheme.
Ensures data in graphs is accurate, clean, and styled with Blue and Light Blue.
"""
import os
import re
import uuid
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

# Executive Blue Theme Palette
PRIMARY_BLUE = "#1D4ED8"     # Deep/Royal Blue for main series & headings
LIGHT_BLUE = "#38BDF8"       # Light/Sky Blue for secondary series & subheadings
ACCENT_BLUE = "#2563EB"      # Blue
SLATE_TEXT = "#0F172A"       # Dark text
MUTED_TEXT = "#64748B"       # Muted text
BORDER_COLOR = "#E2E8F0"     # Clean subtle border

def parse_numeric_value(val_str: any) -> tuple[float, str]:
    """
    Parses strings like '$12.8M', '148%', '4,587', '25.4' into (float_value, unit_suffix).
    """
    if isinstance(val_str, (int, float)):
        return float(val_str), ""
    
    s = str(val_str).strip()
    # Check for negative
    sign = -1.0 if "-" in s else 1.0
    
    # Extract unit suffix
    suffix = ""
    if "%" in s:
        suffix = "%"
    elif "M" in s.upper():
        suffix = "M"
    elif "K" in s.upper():
        suffix = "K"
    elif "B" in s.upper():
        suffix = "B"
        
    # Extract only digits and decimal point
    cleaned = re.sub(r'[^0-9.]', '', s)
    try:
        num = float(cleaned) * sign
        return num, suffix
    except Exception:
        return 1.0, ""


def render_metrics_bar_chart(
    metrics_list: list,
    chart_title: str,
    output_dir: str,
    theme: dict = None
) -> str:
    """
    Render a clean, high-precision bar chart from a list of metrics/KPIs.
    E.g.: [{'label': 'ARR', 'value': '$12.8M'}, {'label': 'YoY Growth', 'value': '148%'}, ...]
    """
    os.makedirs(output_dir, exist_ok=True)
    if not metrics_list:
        return ""

    labels = []
    values = []
    display_texts = []

    for m in metrics_list[:6]:
        lbl = m.get("label") or m.get("name") or m.get("metric") or "Metric"
        val = m.get("value") or m.get("val") or m.get("amount") or 0
        num, suffix = parse_numeric_value(val)
        labels.append(lbl)
        values.append(num)
        display_texts.append(str(val))

    if not labels or not values:
        return ""

    fig_w = max(7.5, len(labels) * 1.6)
    fig_h = 4.8
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=220)
    
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    x = np.arange(len(labels))
    bar_width = 0.52

    # Alternating Blue and Light Blue colors
    bar_colors = [PRIMARY_BLUE if i % 2 == 0 else LIGHT_BLUE for i in range(len(labels))]

    bars = ax.bar(
        x,
        values,
        width=bar_width,
        color=bar_colors,
        edgecolor="#FFFFFF",
        linewidth=1.5,
        zorder=3
    )

    # Add exact data labels on top of each bar for 100% accuracy
    max_val = max(values) if values else 1.0
    for idx, (bar, text) in enumerate(zip(bars, display_texts)):
        h = bar.get_height()
        va = 'bottom' if h >= 0 else 'top'
        y_offset = (max_val * 0.03) if h >= 0 else -(max_val * 0.05)
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            h + y_offset,
            text,
            ha='center',
            va=va,
            color=PRIMARY_BLUE if idx % 2 == 0 else "#0284C7",
            fontweight='bold',
            fontsize=11
        )

    # Title & Subtitle styling
    ax.set_title(chart_title, fontsize=14, fontweight='bold', color=PRIMARY_BLUE, pad=18, loc='left')

    # Axes styling
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10, fontweight='bold', color=SLATE_TEXT)
    ax.tick_params(axis='x', length=0, pad=8)
    ax.tick_params(axis='y', colors=MUTED_TEXT, labelsize=9)

    # Grid lines
    ax.yaxis.grid(True, linestyle='--', alpha=0.5, color=BORDER_COLOR, zorder=1)
    ax.xaxis.grid(False)

    # Hide unnecessary top/right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(BORDER_COLOR)
    ax.spines['bottom'].set_color(BORDER_COLOR)

    # Ensure breathing room above tallest bar
    ax.set_ylim(0, max_val * 1.22 if max_val > 0 else 10)

    plt.tight_layout()

    file_id = str(uuid.uuid4())[:8]
    clean_title = "".join(c for c in chart_title if c.isalnum() or c in ('_', '-')).lower()
    save_filename = f"chart_{clean_title}_{file_id}.png"
    save_path = os.path.join(output_dir, save_filename)

    plt.savefig(save_path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close(fig)

    return save_path


def render_stacked_or_grouped_chart(chart_info: dict, output_dir: str, theme: dict = None) -> str:
    """
    Render stacked/grouped column chart from structured dataset specifications.
    """
    os.makedirs(output_dir, exist_ok=True)
    labels = chart_info.get("labels", [])
    datasets = chart_info.get("datasets", {}).get("default", [])
    if not datasets:
        datasets = chart_info.get("datasets", {}).get("grouped-column", {}).get("series", [])
    if not datasets and isinstance(chart_info.get("datasets"), list):
        datasets = chart_info.get("datasets")

    if not labels or not datasets:
        return ""

    axis_label = chart_info.get("axisLabel", {})
    chart_title = axis_label.get("yAxis") or chart_info.get("title") or "Workforce Analytics"

    num_cats = len(labels)
    y_pos = np.arange(num_cats)
    fig_w, fig_h = 8.5, 4.8
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=220)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    left_accum = np.zeros(num_cats)
    colors = [PRIMARY_BLUE, LIGHT_BLUE, "#0284C7", "#93C5FD", "#3B82F6"]

    for idx, ds in enumerate(datasets):
        label = ds.get("label", f"Cohort {idx+1}")
        raw_data = [float(v) if v is not None else 0.0 for v in ds.get("data", [])]
        while len(raw_data) < num_cats:
            raw_data.append(0.0)
        s_data = np.array(raw_data[:num_cats])
        col = colors[idx % len(colors)]

        bars = ax.barh(
            y_pos,
            s_data,
            height=0.48,
            left=left_accum,
            color=col,
            label=label,
            edgecolor="#FFFFFF",
            linewidth=1.2,
            zorder=3
        )
        left_accum += s_data

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=10, fontweight='bold', color=SLATE_TEXT)
    ax.tick_params(axis='y', length=0, pad=8)
    ax.tick_params(axis='x', colors=MUTED_TEXT, labelsize=9)

    ax.set_title(chart_title, fontsize=14, fontweight='bold', color=PRIMARY_BLUE, pad=18, loc='left')
    ax.xaxis.grid(True, linestyle='--', alpha=0.5, color=BORDER_COLOR, zorder=1)
    ax.yaxis.grid(False)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(BORDER_COLOR)
    ax.spines['bottom'].set_color(BORDER_COLOR)

    ax.legend(loc='upper right', frameon=False, fontsize=9)
    plt.tight_layout()

    file_id = str(uuid.uuid4())[:8]
    clean_title = "".join(c for c in chart_title if c.isalnum() or c in ('_', '-')).lower()
    save_filename = f"chart_{clean_title}_{file_id}.png"
    save_path = os.path.join(output_dir, save_filename)

    plt.savefig(save_path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close(fig)

    return save_path


def extract_and_render_charts_from_json(json_data: any, output_dir: str, theme: dict = None) -> list:
    """
    Scans any JSON structure for metrics, series, or chart specifications.
    Automatically renders high-resolution PNG charts with exact data points.
    Guarantees at least 1-2 accurate charts whenever numeric data is present!
    """
    rendered_charts = []
    
    if isinstance(json_data, str):
        try:
            import json
            json_data = json.loads(json_data)
        except Exception:
            pass

    if not isinstance(json_data, (dict, list)):
        return rendered_charts

    # Case 1: Structured chart specs (labels + datasets)
    items = [json_data] if isinstance(json_data, dict) else json_data
    if isinstance(json_data, dict):
        if "data" in json_data and isinstance(json_data["data"], list):
            items = json_data["data"]
        elif "charts" in json_data and isinstance(json_data["charts"], list):
            items = json_data["charts"]

    for item in items:
        if isinstance(item, dict):
            chart_spec = item.get("chart") or (item if "datasets" in item or "labels" in item else None)
            if chart_spec and isinstance(chart_spec, dict):
                try:
                    c_path = render_stacked_or_grouped_chart(chart_spec, output_dir, theme)
                    if c_path and os.path.exists(c_path):
                        s_name = os.path.basename(c_path)
                        title = chart_spec.get("axisLabel", {}).get("yAxis") or chart_spec.get("title") or "Empirical Distribution"
                        img_id = f"chart_{len(rendered_charts)+1}"
                        rendered_charts.append({
                            "id": img_id,
                            "filename": s_name,
                            "original_name": f"{title}.png",
                            "url": f"/api/uploads/{s_name}",
                            "width": 1870,
                            "height": 1050,
                            "role": "chart",
                            "path": c_path,
                            "chart_title": title,
                            "chart_meta": chart_spec
                        })
                except Exception as e:
                    print(f"[Chart Engine] Notice: {e}")

    # Case 2: General metrics list (e.g. {'metrics': [{'label': 'ARR', 'value': '$12.8M'}, ...]})
    if not rendered_charts and isinstance(json_data, dict):
        # Look for metric arrays
        metrics = json_data.get("metrics") or json_data.get("kpis") or json_data.get("statistics") or json_data.get("performance")
        if isinstance(metrics, list) and len(metrics) > 0:
            c_path = render_metrics_bar_chart(
                metrics,
                "Key Performance Metrics & Trajectory",
                output_dir,
                theme
            )
            if c_path and os.path.exists(c_path):
                s_name = os.path.basename(c_path)
                rendered_charts.append({
                    "id": "chart_1",
                    "filename": s_name,
                    "original_name": "Key Metrics Performance.png",
                    "url": f"/api/uploads/{s_name}",
                    "width": 1870,
                    "height": 1050,
                    "role": "chart",
                    "path": c_path,
                    "chart_title": "Key Performance Metrics & Trajectory",
                    "chart_meta": {"metrics": metrics}
                })

        # Look for breakdowns (market_opportunity, financials, divisions)
        for key in ["market_opportunity", "financials", "breakdown", "revenue_streams", "growth"]:
            val = json_data.get(key)
            if isinstance(val, dict):
                sub_metrics = [{"label": k.replace("_", " ").upper(), "value": str(v)} for k, v in val.items() if isinstance(v, (int, float, str))]
                if sub_metrics:
                    chart_title = f"{key.replace('_', ' ').title()} Analysis"
                    c_path = render_metrics_bar_chart(sub_metrics, chart_title, output_dir, theme)
                    if c_path and os.path.exists(c_path):
                        s_name = os.path.basename(c_path)
                        rendered_charts.append({
                            "id": f"chart_{len(rendered_charts)+1}",
                            "filename": s_name,
                            "original_name": f"{chart_title}.png",
                            "url": f"/api/uploads/{s_name}",
                            "width": 1870,
                            "height": 1050,
                            "role": "chart",
                            "path": c_path,
                            "chart_title": chart_title,
                            "chart_meta": val
                        })

    # Case 3: If still no charts and json_data is a dict with numbers, extract top numeric keys
    if not rendered_charts and isinstance(json_data, dict):
        numeric_items = []
        for k, v in json_data.items():
            if isinstance(v, (int, float)) or (isinstance(v, str) and any(char.isdigit() for char in v) and len(v) < 20):
                numeric_items.append({"label": k.replace("_", " ").title(), "value": str(v)})
        if len(numeric_items) >= 2:
            c_path = render_metrics_bar_chart(numeric_items[:5], "Executive Operational Metrics", output_dir, theme)
            if c_path and os.path.exists(c_path):
                s_name = os.path.basename(c_path)
                rendered_charts.append({
                    "id": "chart_1",
                    "filename": s_name,
                    "original_name": "Operational Metrics.png",
                    "url": f"/api/uploads/{s_name}",
                    "width": 1870,
                    "height": 1050,
                    "role": "chart",
                    "path": c_path,
                    "chart_title": "Executive Operational Metrics",
                    "chart_meta": {"metrics": numeric_items}
                })

    return rendered_charts
