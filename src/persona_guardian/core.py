from dataclasses import dataclass
from typing import List, Literal
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import yaml
import os
from pathlib import Path


@dataclass
class TraitConfig:
    name: str
    description: str
    positive_prompt_template: str
    negative_prompt_template: str
    probe_questions: List[str]
    layer_index: int = -1  # default last layer


def load_trait_config(path: str | os.PathLike) -> TraitConfig:
    """Load trait configuration from YAML file."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return TraitConfig(**data)


def _format_system_prompt(template: str, description: str) -> str:
    """Format system prompt template with description."""
    return template.format(description=description)


def _build_prompt_pairs(trait: TraitConfig) -> List[tuple[str, str]]:
    """Return list of (positive_system_prompt, negative_system_prompt)."""
    pos = _format_system_prompt(trait.positive_prompt_template, trait.description)
    neg = _format_system_prompt(trait.negative_prompt_template, trait.description)
    return [(pos, neg)]


def _capture_hidden_states(
    model,
    tokenizer,
    system_prompt: str,
    question: str,
    layer_index: int,
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
) -> torch.Tensor:
    """Capture hidden states from model at specified layer."""
    text = system_prompt + "\n\nUser: " + question + "\nAssistant:"
    inputs = tokenizer(text, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model(**inputs, output_hidden_states=True)
    # Take hidden state after last token at given layer
    hidden_states = outputs.hidden_states[layer_index]  # (batch, seq, dim)
    last_token = hidden_states[:, -1, :]  # (batch, dim)
    return last_token.squeeze(0).cpu()


def build_persona_vector(
    model_name: str,
    trait_config_path: str,
    device: str | None = None,
) -> torch.Tensor:
    """
    Compute persona vector for a given trait using a simple average-difference scheme.
    
    Args:
        model_name: HuggingFace model name (e.g., "meta-llama/Llama-3-8B-Instruct")
        trait_config_path: Path to trait YAML configuration
        device: Device to use ("cuda" or "cpu"). Auto-detects if None.
        
    Returns:
        Normalized persona vector as a torch.Tensor
    """
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    trait = load_trait_config(trait_config_path)

    print(f"Loading model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        device_map="auto" if device == "cuda" else None,
    )

    pos_vecs = []
    neg_vecs = []

    pairs = _build_prompt_pairs(trait)

    print(f"Computing persona vectors for trait: {trait.name}")
    for pos_sys, neg_sys in pairs:
        for i, q in enumerate(trait.probe_questions):
            print(f"  Processing question {i+1}/{len(trait.probe_questions)}")
            pos_vec = _capture_hidden_states(
                model, tokenizer, pos_sys, q, trait.layer_index, device=device
            )
            neg_vec = _capture_hidden_states(
                model, tokenizer, neg_sys, q, trait.layer_index, device=device
            )
            pos_vecs.append(pos_vec)
            neg_vecs.append(neg_vec)

    pos_mean = torch.stack(pos_vecs, dim=0).mean(dim=0)
    neg_mean = torch.stack(neg_vecs, dim=0).mean(dim=0)

    persona_vector = pos_mean - neg_mean
    persona_vector = persona_vector / (persona_vector.norm() + 1e-8)
    
    print(f"Persona vector computed. Shape: {persona_vector.shape}")
    return persona_vector


def save_persona_vector(
    vector: torch.Tensor,
    model_name: str,
    trait_name: str,
    out_dir: str | os.PathLike = "persona_vectors",
) -> Path:
    """Save persona vector to disk."""
    out_dir = Path(out_dir) / model_name.replace("/", "_")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{trait_name}.pt"
    torch.save(vector, out_path)
    print(f"Saved persona vector to: {out_path}")
    return out_path


def load_persona_vector(path: str | os.PathLike) -> torch.Tensor:
    """Load persona vector from disk."""
    return torch.load(path)
