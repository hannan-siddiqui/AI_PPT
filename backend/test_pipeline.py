"""
Automated Test for the 5-Stage End-to-End Pipeline
Tests:
1. Pydantic Schemas & Theme Validation
2. Async Job Queue Orchestration
3. Vision Pass & Reasoning Schema Generation
4. Slide Assembly & VLM-as-Judge QA
5. Multipart/form-data HTTP Ingestion & Polling
"""
import io
import time
import json
import os
from PIL import Image

from schemas import SlideDeckSchema, ThemeConfig, SlideData
from job_queue import create_job, update_job, get_job, submit_task
from ai_engine import (
    analyze_image_with_vlm,
    generate_slidedeck_schema,
    vlm_judge_review,
    build_fallback_boardroom_plan
)
from app import app, UPLOADS_DIR, OUTPUTS_DIR


def test_schemas():
    print("--- Testing Pydantic Schemas ---")
    theme = ThemeConfig(name="Executive Mint", primary_color="#070F1A", accent_color="#2DD4BF")
    slide = SlideData(
        slide_number=1,
        layout_type="title_hero",
        title="Executive Strategy Briefing",
        subtitle="Operational Parity Diagnostics",
        presenter="McKinsey Senior Partner"
    )
    deck = SlideDeckSchema(
        deck_title="Executive Review",
        theme=theme,
        slides=[slide]
    )
    assert deck.deck_title == "Executive Review"
    assert len(deck.slides) == 1
    print("[OK] Schemas valid")


def test_job_queue():
    print("--- Testing Async Job Queue ---")
    job_id = create_job({"test": True})
    assert job_id is not None
    job = get_job(job_id)
    assert job["status"] == "queued"
    
    update_job(job_id, status="analyzing_images", step="Vision Pass", progress=35)
    job = get_job(job_id)
    assert job["progress"] == 35
    assert job["status"] == "analyzing_images"
    print("[OK] Job queue state transitions valid")


def test_vision_pass_and_qa():
    print("--- Testing Vision Pass & QA Judge ---")
    # Create test dummy image in uploads
    test_img_path = os.path.join(UPLOADS_DIR, "test_chart.png")
    img = Image.new("RGB", (600, 400), color=(15, 23, 42))
    img.save(test_img_path)

    v_res = analyze_image_with_vlm(test_img_path, "img_test1", "test_chart.png")
    assert v_res.image_id == "img_test1"
    assert v_res.width == 600
    print(f"[OK] Vision Pass returned role='{v_res.role}' and summary: {v_res.summary[:50]}...")

    # Test Fallback & QA Judge
    sample_plan = build_fallback_boardroom_plan({"company": "TestCorp"}, prompt="Highlight ARR")
    deck_schema = SlideDeckSchema(**sample_plan)
    qa_report = vlm_judge_review(deck_schema, "Highlight ARR", [{"id": "chart_1", "role": "chart"}])
    assert qa_report.passed is True
    assert qa_report.score >= 80
    print(f"[OK] VLM-as-Judge QA passed with score {qa_report.score}/100: {qa_report.feedback}")


def test_multipart_ingestion_and_polling():
    print("--- Testing Multipart/form-data API Ingestion & Async Polling ---")
    client = app.test_client()

    # Create in-memory test image
    img_byte_arr = io.BytesIO()
    img = Image.new("RGB", (400, 200), color=(37, 99, 235))
    img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    sample_json = json.dumps({
        "company": "Nexus Enterprise AI",
        "n_slides": 4,
        "metrics": [{"label": "ARR", "value": "$12M"}]
    })

    # Send multipart/form-data
    data = {
        "json_data": sample_json,
        "prompt": "Board presentation detailing scale and market defensibility.",
        "slide_count": "4",
        "images": (img_byte_arr, "nexus_logo.png")
    }

    res = client.post(
        "/api/generate-ppt?async=true",
        data=data,
        content_type="multipart/form-data"
    )

    assert res.status_code == 202
    resp_json = res.get_json()
    job_id = resp_json["job_id"]
    print(f"[OK] Ingestion accepted! Job ID: {job_id}, Status: {resp_json['status']}")

    # Poll until completed
    max_wait = 90
    start = time.time()
    completed = False

    while time.time() - start < max_wait:
        poll_res = client.get(f"/api/jobs/{job_id}")
        assert poll_res.status_code == 200
        job_data = poll_res.get_json()
        status = job_data.get("status")
        progress = job_data.get("progress", 0)
        step = job_data.get("step", "")
        print(f"  ...Polling [{progress}%] {status}: {step}", flush=True)

        if status == "completed":
            completed = True
            result = job_data.get("result")
            assert result is not None
            assert result.get("success") is True
            assert "deck_id" in result
            assert "qa_report" in result
            print(f"[OK] Generation complete! Download URL: {result.get('download_url')}")
            print(f"[OK] QA Judge Score: {result.get('qa_report', {}).get('score')}")
            break
        elif status == "failed":
            raise RuntimeError(f"Job failed with error: {job_data.get('error')}")

        time.sleep(1.5)

    assert completed, "Pipeline did not complete within timeout window"


if __name__ == "__main__":
    test_schemas()
    test_job_queue()
    test_vision_pass_and_qa()
    test_multipart_ingestion_and_polling()
    print("\n===========================================")
    print("ALL 5 PIPELINE STAGE TESTS PASSED SUCCESSFULLY!")
    print("===========================================")
