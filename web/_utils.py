from pathlib import Path
from typing import Dict
import tempfile

from persona_guardian.analyzer import PersonaVectorAnalyzer

# Simple in-memory cache for analyzers keyed by (model_name, persona_vector_path, device)
_ANALYZER_CACHE: Dict[str, PersonaVectorAnalyzer] = {}


def default_persona_vector_path() -> str:
    """Return a reasonable default persona vector file in the repo, if present."""
    repo_root = Path(__file__).resolve().parents[1]
    # common vector used in repo
    candidate = repo_root / "persona_vectors" / "Qwen_Qwen2.5-1.5B-Instruct" / "sycophancy.pt"
    if candidate.exists():
        return str(candidate)
    # fall back to the first .pt file under persona_vectors
    pv = repo_root / "persona_vectors"
    if pv.exists():
        for p in pv.rglob("*.pt"):
            return str(p)
    raise FileNotFoundError("No persona vector (.pt) found in repo under persona_vectors/")


def get_analyzer(model_name: str, persona_vector_path: str = None, device: str = "cpu") -> PersonaVectorAnalyzer:
    if persona_vector_path is None:
        persona_vector_path = default_persona_vector_path()

    key = f"{model_name}::{persona_vector_path}::{device}"
    if key in _ANALYZER_CACHE:
        return _ANALYZER_CACHE[key]

    analyzer = PersonaVectorAnalyzer(model_name=model_name, persona_vector_path=persona_vector_path, device=device)
    _ANALYZER_CACHE[key] = analyzer
    return analyzer


def save_upload_to_temp(upload_file) -> str:
    """Save a FastAPI/Gradio upload to a temp file and return its path."""
    tf = tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl")
    with open(tf.name, "wb") as f:
        f.write(upload_file.file.read())
    return tf.name
