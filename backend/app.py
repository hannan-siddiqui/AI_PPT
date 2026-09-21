"""
Flask Backend API with Asynchronous Orchestration & 5-Stage End-to-End Pipeline
1. Data Ingestion (multipart/form-data)
2. Asynchronous Orchestration (job queue & polling)
3. Multimodal Analysis (Vision Pass + Reasoning Schema Generation)
4. Slide Assembly Engine (python-pptx)
5. VLM-as-Judge (Quality Assurance & auto-tuning)
"""
import os
import uuid
import json
import re
import traceback
from typing import Any, Dict, List, Optional
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image

from ai_engine import (
    analyze_image_with_vlm,
    generate_slidedeck_schema,
    vlm_judge_review,
    VISION_MODEL,
    REASONING_MODEL,
    JUDGE_MODEL
)
from multi_agent_pipeline import presentation_graph, log_step, ARCHITECT_MODEL
from schemas import SlideDeckSchema, ThemeConfig
from job_queue import create_job, update_job, get_job, submit_task
from pptx_generator import PresentationCompiler
from sample_data import SAMPLE_TEMPLATES
from chart_renderer import extract_and_render_charts_from_json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

app = Flask(__name__)
# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "svg", "gif"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "pipeline": "LangGraph 3-Agent Multimodal Architecture",
        "agent_1_vision": f"moonshotai/kimi-k3 ({VISION_MODEL})",
        "agent_2_data_instructions": f"nvidia/nemotron-3-ultra-550b-a55b ({REASONING_MODEL})",
        "agent_3_ppt_architect": f"nvidia/nemotron-3-ultra-550b-a55b ({ARCHITECT_MODEL})",
        "stage_4_assembly": "python-pptx",
        "stage_5_judge": f"VLM-as-Judge ({JUDGE_MODEL})"
    })


@app.route("/api/templates", methods=["GET"])
def get_templates():
    return jsonify({
        "templates": SAMPLE_TEMPLATES
    })


@app.route("/api/upload-images", methods=["POST"])
def upload_images():
    """Standalone image upload endpoint."""
    if "images" not in request.files and "image" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    files = request.files.getlist("images")
    if not files:
        files = request.files.getlist("image")

    uploaded = []
    for file in files:
        if file and file.filename and allowed_file(file.filename):
            orig_name = secure_filename(file.filename)
            img_id = str(uuid.uuid4())[:8]
            save_name = f"{img_id}_{orig_name}"
            save_path = os.path.join(UPLOADS_DIR, save_name)
            file.save(save_path)

            width, height = 800, 600
            try:
                with Image.open(save_path) as im:
                    width, height = im.size
            except Exception:
                pass

            lower_name = orig_name.lower()
            if "logo" in lower_name or "icon" in lower_name:
                role = "logo"
            elif "chart" in lower_name or "graph" in lower_name or "metric" in lower_name or "salary" in lower_name or "fte" in lower_name:
                role = "chart"
            elif "team" in lower_name or "people" in lower_name:
                role = "team"
            elif "hero" in lower_name or "banner" in lower_name:
                role = "hero"
            else:
                role = "graphic"

            uploaded.append({
                "id": img_id,
                "filename": save_name,
                "original_name": orig_name,
                "url": f"/api/uploads/{save_name}",
                "width": width,
                "height": height,
                "role": role,
                "path": save_path
            })

    return jsonify({"images": uploaded})


@app.route("/api/uploads/<filename>", methods=["GET"])
def get_uploaded_file(filename):
    return send_from_directory(UPLOADS_DIR, secure_filename(filename))


# =================================================================
# ASYNCHRONOUS PIPELINE WORKER (LANGGRAPH 3-AGENT ORCHESTRATION)
# =================================================================
def execute_pipeline(
    job_id: str,
    user_json: Any,
    prompt: str,
    theme_prefs: dict,
    images_meta: list,
    logo_config: dict,
    slide_count: Any
):
    pipeline_logs = []
    try:
        log_step(pipeline_logs, f"[PIPELINE INIT] Starting Job {job_id}")
        log_step(pipeline_logs, f"[LANGGRAPH] Agents configured: Agent 1 (OCR/Vision: {VISION_MODEL}), Agent 2 (Data: {REASONING_MODEL}), Agent 3 (Architect: {ARCHITECT_MODEL})")

        # Stage 1: Data Ingestion Verified
        update_job(
            job_id,
            status="ingesting",
            step="Stage 1/5: Multipart payload ingested and stored",
            progress=15,
            logs=pipeline_logs
        )

        image_catalog = {}
        for img in images_meta:
            img_id = img.get("id")
            path = img.get("path")
            filename = img.get("filename")
            if not path and filename:
                path = os.path.join(UPLOADS_DIR, secure_filename(filename))
            if img_id and path and os.path.exists(path):
                image_catalog[img_id] = path

        # Auto-render any inline charts from JSON
        if isinstance(user_json, dict):
            try:
                auto_rendered = extract_and_render_charts_from_json(user_json, UPLOADS_DIR, theme_prefs)
                for c in auto_rendered:
                    if c["id"] not in image_catalog:
                        image_catalog[c["id"]] = c["path"]
                        images_meta.append(c)
                        log_step(pipeline_logs, f"[DATA ENGINE] Extracted & rendered empirical chart: '{c.get('original_name')}'")
            except Exception as e:
                print(f"Chart extraction notice: {e}")

        # Stage 2 & 3: Run LangGraph Multi-Agent Workflow
        update_job(
            job_id,
            status="analyzing_images",
            step=f"Stage 2/5: Agent 1 (OCR/Vision: {VISION_MODEL}) analyzing images...",
            progress=30,
            logs=pipeline_logs
        )

        from identity_engine import extract_page_count_from_input
        parsed_cnt, cnt_src = extract_page_count_from_input(prompt, user_json, default=8 if not slide_count else int(slide_count))
        slide_count = parsed_cnt
        log_step(pipeline_logs, f"[PIPELINE INIT] Target slide count: {slide_count} slides ({cnt_src})")

        graph_state = {
            "job_id": job_id,
            "user_json": user_json,
            "prompt": prompt,
            "theme": theme_prefs,
            "available_images": images_meta,
            "image_catalog": image_catalog,
            "slide_count": slide_count,
            "logs": pipeline_logs,
            "ocr_image_results": [],
            "data_insights": {},
            "slide_plan": {},
            "qa_report": {}
        }

        # Invoke LangGraph StateGraph
        final_state = presentation_graph.invoke(graph_state)
        pipeline_logs = final_state.get("logs", pipeline_logs)
        deck_dict = final_state.get("slide_plan", {})

        # Validate SlideDeckSchema
        deck_schema = SlideDeckSchema(**deck_dict)

        # Stage 4: Slide Assembly Engine (python-pptx)
        log_step(pipeline_logs, "[STAGE 4: SLIDE ASSEMBLY] python-pptx rendering 16:9 widescreen slides...")
        update_job(
            job_id,
            status="assembling_slides",
            step="Stage 4/5: python-pptx Slide Assembly Engine compiling widescreen deck",
            progress=78,
            logs=pipeline_logs
        )

        deck_id = str(uuid.uuid4())[:12]
        output_filename = f"deck_{deck_id}.pptx"
        output_path = os.path.join(OUTPUTS_DIR, output_filename)

        # Stage 5: VLM-as-Judge (Quality Assurance)
        log_step(pipeline_logs, "[STAGE 5: VLM-AS-JUDGE] Inspecting visual hierarchy, text boundaries & clipping risks...")
        update_job(
            job_id,
            status="vlm_judge",
            step="Stage 5/5: VLM-as-Judge evaluating visual hierarchy & text boundaries",
            progress=90,
            logs=pipeline_logs
        )

        qa_report = vlm_judge_review(
            deck=deck_schema,
            user_prompt=prompt,
            available_images=images_meta
        )
        log_step(pipeline_logs, f"[STAGE 5: VLM-AS-JUDGE] QA Complete. Score: {qa_report.score}/100. Verdict: {qa_report.feedback}")
        if qa_report.applied_fixes:
            for fix in qa_report.applied_fixes:
                log_step(pipeline_logs, f"[STAGE 5: VLM-AS-JUDGE] Fix applied: {fix}")

        # Re-export dictionary with QA-adjusted slides
        deck_dict = deck_schema.model_dump()

        # Compile PPTX with assembly engine
        compiler = PresentationCompiler(
            slide_plan=deck_dict,
            image_catalog=image_catalog,
            logo_config=logo_config
        )
        compiler.compile(output_path)
        log_step(pipeline_logs, f"[COMPILATION SUCCESS] PPTX presentation successfully compiled at {output_path}")

        deck_title = deck_dict.get("deck_title", "Business Presentation")
        from identity_engine import is_prompt_instruction
        if is_prompt_instruction(deck_title):
            from identity_engine import resolve_presentation_identity
            deck_title = resolve_presentation_identity(user_json, prompt)["deck_title"]
        clean_title = "".join(c for c in deck_title if c.isalnum() or c in (' ', '-', '_')).strip() or "Presentation"

        # Final Result Payload
        result = {
            "success": True,
            "deck_id": deck_id,
            "filename": f"{clean_title}.pptx",
            "download_url": f"/api/download/{deck_id}?filename={clean_title}.pptx",
            "slide_count": len(deck_dict.get("slides", [])),
            "plan": deck_dict,
            "images": images_meta,
            "qa_report": qa_report.model_dump(),
            "logs": pipeline_logs
        }

        update_job(
            job_id,
            status="completed",
            step="Generation & QA verification complete",
            progress=100,
            result=result,
            logs=pipeline_logs
        )

    except Exception as e:
        traceback.print_exc()
        log_step(pipeline_logs, f"[PIPELINE ERROR] {str(e)}")
        update_job(
            job_id,
            status="failed",
            step="Error encountered during execution",
            error=str(e),
            logs=pipeline_logs
        )


# =================================================================
# STAGE 1 & 2: INGESTION & ASYNC ORCHESTRATION ENDPOINTS
# =================================================================
@app.route("/api/generate-ppt", methods=["POST"])
def generate_ppt():
    """
    Stage 1: Multipart/form-data Data Ingestion
    Stage 2: Asynchronous Job Enqueueing
    Accepts:
    - multipart/form-data with 'images', 'json_data', 'prompt', 'theme', 'slide_count'
    - OR JSON payload for backward compatibility
    Returns immediate: { "job_id": job_id, "status": "queued" }
    """
    try:
        user_json = {}
        prompt = ""
        theme_prefs = {}
        images_meta = []
        logo_config = {}
        slide_count = "auto"
        async_mode = request.args.get("async", "true").lower() in ("true", "1", "yes")

        # Check if multipart/form-data
        if request.content_type and "multipart/form-data" in request.content_type:
            # 1. Parse JSON data from form text or attached file
            if "json_file" in request.files and request.files["json_file"].filename:
                try:
                    file_bytes = request.files["json_file"].read()
                    user_json = json.loads(file_bytes.decode("utf-8"))
                except Exception:
                    user_json = {}
            elif "json_data" in request.form:
                raw_json = request.form.get("json_data", "")
                try:
                    user_json = json.loads(raw_json)
                except Exception:
                    user_json = raw_json

            prompt = request.form.get("prompt", "")
            slide_count = request.form.get("slide_count", "auto")

            if isinstance(user_json, dict):
                if slide_count == "auto" and (user_json.get("n_slides") or user_json.get("slide_count")):
                    slide_count = user_json.get("n_slides") or user_json.get("slide_count")

            if "theme" in request.form:
                try:
                    theme_prefs = json.loads(request.form.get("theme", "{}"))
                except Exception:
                    pass

            if isinstance(user_json, dict) and "theme" in user_json:
                from identity_engine import resolve_theme_from_input
                if not theme_prefs or theme_prefs.get("name") in ("Clean Executive Light", "Corporate Navy", "Corporate Blue Minimalist"):
                    theme_prefs = resolve_theme_from_input(user_json["theme"])

            if "logo_config" in request.form:
                try:
                    logo_config = json.loads(request.form.get("logo_config", "{}"))
                except Exception:
                    pass

            # 2. Ingest raw images from multipart payload
            uploaded_files = request.files.getlist("images")
            if not uploaded_files:
                uploaded_files = request.files.getlist("image")

            for file in uploaded_files:
                if file and file.filename and allowed_file(file.filename):
                    orig_name = secure_filename(file.filename)
                    img_id = str(uuid.uuid4())[:8]
                    save_name = f"{img_id}_{orig_name}"
                    save_path = os.path.join(UPLOADS_DIR, save_name)
                    file.save(save_path)

                    width, height = 800, 600
                    try:
                        with Image.open(save_path) as im:
                            width, height = im.size
                    except Exception:
                        pass

                    lower_name = orig_name.lower()
                    if "logo" in lower_name or "icon" in lower_name:
                        role = "logo"
                    elif "chart" in lower_name or "graph" in lower_name or "plot" in lower_name:
                        role = "chart"
                    elif "team" in lower_name or "people" in lower_name:
                        role = "team"
                    elif "hero" in lower_name:
                        role = "hero"
                    else:
                        role = "graphic"

                    images_meta.append({
                        "id": img_id,
                        "filename": save_name,
                        "original_name": orig_name,
                        "url": f"/api/uploads/{save_name}",
                        "width": width,
                        "height": height,
                        "role": role,
                        "path": save_path
                    })

            # Also check if existing images list passed as JSON string
            if "existing_images" in request.form:
                try:
                    existing = json.loads(request.form.get("existing_images", "[]"))
                    images_meta.extend(existing)
                except Exception:
                    pass

        else:
            # Fallback for standard application/json payload
            req_data = request.get_json(force=True) or {}
            user_json = req_data.get("json_data", {})
            prompt = req_data.get("prompt", "")
            theme_prefs = req_data.get("theme", {})
            images_meta = req_data.get("images", [])
            logo_config = req_data.get("logo_config", {})
            slide_count = req_data.get("slide_count", "auto")
            if "async" in req_data:
                async_mode = bool(req_data.get("async"))

        # Extract explicit directives from prompt
        p_lower = prompt.lower()

        # Directive 1: Slide count (e.g. "create 7 page ppt", "7 slides", "7 pages")
        slide_match = re.search(r'(\d+)\s*(?:page|slide)', p_lower)
        if slide_match:
            try:
                cnt = int(slide_match.group(1))
                if 2 <= cnt <= 25:
                    slide_count = cnt
            except Exception:
                pass
        elif isinstance(slide_count, str) and slide_count.isdigit():
            slide_count = int(slide_count)

        # Directive 2: Blue heading & Light Blue subheading
        if not isinstance(theme_prefs, dict):
            theme_prefs = {}

        if "blue" in p_lower:
            theme_prefs["heading_color"] = "#1D4ED8"      # Blue for heading
            theme_prefs["subheading_color"] = "#0284C7"   # Light Blue for sub heading
            theme_prefs["primary_color"] = "#1D4ED8"
            theme_prefs["accent_color"] = "#1D4ED8"
            theme_prefs["bg_color"] = "#FFFFFF"
            theme_prefs["card_bg_color"] = "#FFFFFF"
            theme_prefs["text_color"] = "#0F172A"
            theme_prefs["secondary_color"] = "#E2E8F0"
            theme_prefs["muted_text_color"] = "#64748B"
        else:
            if not theme_prefs.get("heading_color"):
                theme_prefs["heading_color"] = "#1D4ED8"
            if not theme_prefs.get("subheading_color"):
                theme_prefs["subheading_color"] = "#0284C7"

        # Create Asynchronous Job
        job_id = create_job({
            "prompt": prompt[:80],
            "slide_count": slide_count,
            "images_count": len(images_meta)
        })

        if async_mode:
            # Enqueue and return immediate response
            submit_task(
                job_id,
                execute_pipeline,
                user_json=user_json,
                prompt=prompt,
                theme_prefs=theme_prefs,
                images_meta=images_meta,
                logo_config=logo_config,
                slide_count=slide_count
            )

            return jsonify({
                "success": True,
                "job_id": job_id,
                "status": "queued",
                "step": "Stage 1/5: Request ingested and queued",
                "progress": 5,
                "poll_url": f"/api/jobs/{job_id}"
            }), 202

        else:
            # Synchronous execution mode if explicitly requested
            execute_pipeline(
                job_id,
                user_json=user_json,
                prompt=prompt,
                theme_prefs=theme_prefs,
                images_meta=images_meta,
                logo_config=logo_config,
                slide_count=slide_count
            )
            job = get_job(job_id)
            if job and job.get("status") == "completed":
                return jsonify(job.get("result")), 200
            else:
                return jsonify({"error": job.get("error") if job else "Generation failed"}), 500

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500


@app.route("/api/jobs/<job_id>", methods=["GET"])
def poll_job(job_id):
    """
    Stage 2: Asynchronous Orchestration Polling Endpoint
    Returns current status, active stage description, progress percentage,
    and final presentation result once ready.
    """
    job = get_job(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job)


@app.route("/api/download/<deck_id>", methods=["GET"])
def download_deck(deck_id):
    """Serve the compiled PPTX file with robust attachment headers."""
    clean_id = secure_filename(deck_id)
    output_path = os.path.join(OUTPUTS_DIR, f"deck_{clean_id}.pptx")
    if not os.path.exists(output_path):
        return jsonify({"error": "File not found"}), 404

    custom_name = request.args.get("filename", "Presentation.pptx")
    safe_name = "".join(c for c in custom_name if c.isalnum() or c in (' ', '-', '_', '.')).strip()
    if not safe_name.lower().endswith(".pptx"):
        safe_name += ".pptx"

    from urllib.parse import quote
    encoded_name = quote(safe_name)

    response = send_file(
        output_path,
        as_attachment=True,
        download_name=safe_name,
        mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
    response.headers["Content-Disposition"] = f'attachment; filename="{safe_name}"; filename*=UTF-8\'\'{encoded_name}'
    response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
    return response


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting 5-Stage AI PPT Generator Backend on http://localhost:{port}")
    print(f"Models: Vision={VISION_MODEL} | Reasoning={REASONING_MODEL} | Judge={JUDGE_MODEL}")
    app.run(host="0.0.0.0", port=port, debug=False)
