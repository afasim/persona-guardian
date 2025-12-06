from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import shutil

from ._utils import get_analyzer, save_upload_to_temp, default_persona_vector_path

app = FastAPI(title="Persona Guardian API")

# Allow all origins for local/demo use
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScoreRequest(BaseModel):
    model_name: str
    persona_vector_path: str | None = None
    text: str


class AnalyzeRequest(BaseModel):
    model_name: str
    persona_vector_path: str | None = None


class SteerRequest(BaseModel):
    model_name: str
    persona_vector_path: str | None = None
    prompt: str
    max_new_tokens: int = 50
    steering_strength: float = 1.0
    steer_direction: str = "reduce"


@app.post("/score")
async def score(req: ScoreRequest):
    try:
        analyzer = get_analyzer(req.model_name, req.persona_vector_path, device="cpu")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    score = analyzer.score_text(req.text)
    return {"score": score}


@app.post("/analyze")
async def analyze(model_name: str, persona_vector: UploadFile | None = File(None), dataset: UploadFile | None = File(None)):
    # persona_vector: optional uploaded .pt file
    # dataset: optional uploaded jsonl file
    pv_path = None
    ds_path = None

    if persona_vector is not None:
        # save to temp
        pv_path = save_upload_to_temp(persona_vector)
    else:
        try:
            pv_path = default_persona_vector_path()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    if dataset is None:
        raise HTTPException(status_code=400, detail="Please upload a JSONL dataset file for analysis")

    ds_path = save_upload_to_temp(dataset)

    try:
        analyzer = get_analyzer(model_name, pv_path, device="cpu")
        stats = analyzer.analyze_dataset_file(ds_path)
        report = analyzer.generate_risk_report(stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"analysis": stats, "report": report}


@app.post("/steer")
async def steer(req: SteerRequest):
    try:
        analyzer = get_analyzer(req.model_name, req.persona_vector_path, device="cpu")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    out = analyzer.generate_with_steering(
        prompt=req.prompt,
        max_new_tokens=req.max_new_tokens,
        steering_strength=req.steering_strength,
        steer_direction=req.steer_direction,
    )
    return out


def run(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn

    uvicorn.run("web.fastapi_app:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    run()
