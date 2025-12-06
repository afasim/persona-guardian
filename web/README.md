# Web UI / API for Persona Guardian

This folder contains a small FastAPI backend and a Gradio demo UI that wrap the
`PersonaVectorAnalyzer` implemented in the main package. Use these for local
demos or to build a small hosted service.

FastAPI (backend)

- Endpoint `/score` (POST): JSON body {"model_name","persona_vector_path","text"}
- Endpoint `/analyze` (POST): form-data with `model_name`, optional `persona_vector` file upload, and `dataset` JSONL upload
- Endpoint `/steer` (POST): JSON body {"model_name","persona_vector_path","prompt","max_new_tokens","steering_strength","steer_direction"}

Run locally:

```powershell
# start the FastAPI backend
python -m uvicorn web.fastapi_app:app --reload --host 0.0.0.0 --port 8000
```

Gradio (frontend demo)

The Gradio app runs in-process and directly uses the analyzer (no HTTP).

Run locally:

```powershell
python -m web.gradio_app
```

Notes
- These demo apps load models and vectors into memory; on CPU this can be slow.
- For a hosted deployment, restrict allowed model names and/or provide pre-loaded model options.
- Make sure you have installed the extra dependencies: `fastapi`, `uvicorn`, `gradio`.
