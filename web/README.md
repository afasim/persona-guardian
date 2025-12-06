# Web UI / API for Persona Guardian

This folder contains a small FastAPI backend and a Gradio demo UI that wrap the
`PersonaVectorAnalyzer` implemented in the main package. Use these for local
demos or to build a small hosted service.

## Quick Start

### 1. Install Dependencies

**Windows:**
```powershell
.\setup_web.bat
```

**macOS/Linux:**
```bash
bash setup_web.sh
```

**Or manually:**
```bash
pip install fastapi uvicorn gradio torch transformers pyyaml typer accelerate
```

### 2. Run the App

**Gradio Demo UI** (recommended for quick demo):
```powershell
python -m web.gradio_app
```
Opens browser to `http://localhost:7860`

**FastAPI Backend** (for API integration):
```powershell
python -m uvicorn web.fastapi_app:app --reload --host 0.0.0.0 --port 8000
```
Opens interactive docs at `http://localhost:8000/docs`

**Interactive Menu** (choose which to run):
```powershell
python run_web_apps.py
```

## API Endpoints (FastAPI)

All endpoints use JSON and accept a `persona_vector_path` (optional; defaults to repo's sycophancy vector).

### POST `/score`
Score text for trait presence.

**Request:**
```json
{
  "model_name": "Qwen/Qwen2.5-1.5B-Instruct",
  "persona_vector_path": null,
  "text": "You're absolutely right!"
}
```

**Response:**
```json
{
  "score": 0.456
}
```

### POST `/analyze`
Analyze a JSONL dataset for trait patterns.

**Request:** (multipart/form-data)
- `model_name`: Model name
- `persona_vector` (optional): Upload .pt file
- `dataset`: Upload JSONL file

**Response:**
```json
{
  "analysis": {
    "trait_name": "sycophancy",
    "total_examples": 100,
    "mean_score": 0.12,
    "std_score": 0.34,
    ...
  },
  "report": "Human-readable analysis report..."
}
```

### POST `/steer`
Generate text with steering applied.

**Request:**
```json
{
  "model_name": "Qwen/Qwen2.5-1.5B-Instruct",
  "persona_vector_path": null,
  "prompt": "User: Am I amazing? Assistant:",
  "max_new_tokens": 50,
  "steering_strength": 1.0,
  "steer_direction": "reduce"
}
```

**Response:**
```json
{
  "prompt": "User: Am I amazing? Assistant:",
  "generated_text": " I would need more information...",
  "full_output": "User: Am I amazing? Assistant: I would need more information...",
  "steering_strength": 1.0,
  "steer_direction": "reduce",
  "tokens_generated": 12
}
```

## Gradio UI Features

The Gradio app provides three tabs:

1. **Score Text** — Paste text, click "Score", get trait score
2. **Analyze Dataset** — Upload JSONL, click "Analyze", get statistics and report
3. **Steer Generate** — Enter prompt, adjust strength and direction, click "Generate"

## Notes

- These demo apps load models and vectors into memory; on CPU this can be slow (~30s on first load).
- For hosted deployment, restrict allowed model names and/or provide pre-loaded model options.
- The Gradio app runs in-process (calls `PersonaVectorAnalyzer` directly).
- The FastAPI backend can be deployed on services like Render, Fly.io, or EC2.

