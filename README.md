# SlideCraft AI: 5-Stage End-to-End Autonomous Presentation Engine 🚀

An executive-grade, AI-powered presentation generation system featuring **Multimodal Vision Analysis**, **Reasoning-Driven Schema Generation**, **python-pptx Slide Assembly**, and a **VLM-as-Judge Quality Assurance Loop**.

---

## 🏛️ The 5-Stage End-to-End Pipeline Architecture

```
+---------------------------------------------------------------------------------------------------+
|  1. Data Ingestion (Frontend)                                                                     |
|     Multipart/form-data bundle: Raw Images + JSON Data + Prompt Directives + Theme in 1 request   |
+---------------------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------------------+
|  2. Asynchronous Orchestration (API Gateway & Job Queue)                                          |
|     - Saves images to object store / local storage                                                |
|     - Returns immediate { job_id, status: "queued" }                                              |
|     - Frontend polls GET /api/jobs/<job_id> with real-time 5-stage progress updates                |
+---------------------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------------------+
|  3. Multimodal Analysis (The Brain)                                                               |
|     - Vision Pass: VLM (e.g. GPT-4o / Claude 3.5 Sonnet) extracts context & chart metrics from raw |
|     - Instruction Parsing: Reasoning Model synthesizes user prompt + JSON data + VLM summaries    |
|     - Schema Generation: Strict SlideDeckSchema (Pydantic validated) slide-by-slide plan          |
+---------------------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------------------+
|  4. Slide Assembly Engine                                                                         |
|     - python-pptx dedicated compiler loads master layouts & maps placeholder IDs                  |
|     - Injects high-res images and charts with exact aspect ratios                                 |
+---------------------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------------------+
|  5. VLM-as-Judge (Quality Assurance)                                                              |
|     - Inspects generated slides, characters, card bounds, and prompt fidelity                      |
|     - VLM reviews visual alignment, text clipping risk, and instruction compliance                |
|     - Automatically triggers layout/font size adjustments before finalizing file                  |
+---------------------------------------------------------------------------------------------------+
```

---

## ⚙️ Environment Configuration (`backend/.env`)

Configure your models in `backend/.env` (see `backend/.env.example`):

```env
# -----------------------------------------------------------------
# STAGE 3: VISION PASS (VLM FOR ANALYZING IMAGES)
# Supported: OpenAI GPT-4o / GPT-4o-mini, Claude, or any OpenAI-compatible Vision API
# -----------------------------------------------------------------
VISION_MODEL=gpt-4o
VISION_BASE_URL=https://api.openai.com/v1
VISION_API_KEY=your-vision-api-key-here

# -----------------------------------------------------------------
# STAGE 3: REASONING & SCHEMA GENERATION MODEL
# Model for instruction parsing, JSON data synthesis, and SlideDeckSchema generation
# Supported: OpenAI o1 / o3-mini / gpt-4o, DeepSeek Reasoner, Anthropic, or Nvidia Nemotron
# -----------------------------------------------------------------
REASONING_MODEL=nvidia/nemotron-3-ultra-550b-a55b
REASONING_BASE_URL=https://integrate.api.nvidia.com/v1
REASONING_API_KEY=your-reasoning-api-key-here

# -----------------------------------------------------------------
# STAGE 5: VLM-AS-JUDGE (QUALITY ASSURANCE)
# Model for checking slide clipping, text overflow, and instruction compliance
# -----------------------------------------------------------------
ENABLE_VLM_JUDGE=true
JUDGE_MODEL=gpt-4o
JUDGE_BASE_URL=https://api.openai.com/v1
JUDGE_API_KEY=your-judge-api-key-here

# -----------------------------------------------------------------
# BACKUP / FALLBACK MODEL (Nvidia NIM / Nemotron)
# Automatic high-performance fallback if primary endpoints are not configured
# -----------------------------------------------------------------
NVIDIA_API_KEY=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
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=nvidia/nemotron-3-ultra-550b-a55b

# -----------------------------------------------------------------
# SERVER & STORAGE CONFIGURATION
# -----------------------------------------------------------------
PORT=5000
STORAGE_PROVIDER=local
UPLOAD_FOLDER=uploads
OUTPUT_FOLDER=outputs
MAX_CONCURRENT_JOBS=4
```

---

## 🚀 Quick Start Guide

### 1. Start the Flask Backend (Port 5000)

```bash
cd backend
python -m pip install -r requirements.txt
python -u app.py
```

- Endpoint: `http://localhost:5000`
- Health check: `http://localhost:5000/api/health`

### 2. Start the Next.js Frontend (Port 3000)

```bash
cd frontend
npm install
npm run dev
```

- Web Studio UI: `http://localhost:3000`

---

## 📡 REST API & Asynchronous Job Pipeline Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Check backend status and active Vision, Reasoning & Judge models |
| `/api/generate-ppt?async=true` | POST | Ingests `multipart/form-data` payload (raw images + JSON + prompt) and returns `{ job_id, status: "queued" }` |
| `/api/jobs/<job_id>` | GET | Polling endpoint returning active stage (1-5), progress percentage, QA report, and final PPTX result |
| `/api/download/<deck_id>` | GET | Download finalized presentation file (`.pptx`) |
| `/api/templates` | GET | Retrieve sample business JSON datasets |
| `/api/upload-images` | POST | Standalone media file uploader |

---

## 🧪 Testing the Pipeline

Run the automated 5-stage verification suite:

```bash
python -u backend/test_pipeline.py
```
