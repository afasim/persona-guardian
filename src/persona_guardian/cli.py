import typer
from .core import build_persona_vector, save_persona_vector

app = typer.Typer(help="Persona-guardian CLI")


@app.command()
def build_vector(
    model: str = typer.Argument(..., help="HF model name, e.g. meta-llama/Llama-3-8B-Instruct"),
    trait_config: str = typer.Argument(..., help="Path to trait YAML, e.g. traits/sycophancy.yaml"),
    output_dir: str = typer.Option("persona_vectors", "--output", "-o", help="Output directory for persona vectors"),
):
    """
    Build a persona vector for a given model and trait config.
    
    Example:
        persona-guardian build-vector meta-llama/Llama-3-8B-Instruct traits/sycophancy.yaml
    """
    typer.echo(f"Loading model: {model}")
    typer.echo(f"Using trait config: {trait_config}")
    
    try:
        vector = build_persona_vector(model_name=model, trait_config_path=trait_config)
        
        # Extract trait name from config path
        import os
        trait_name = os.path.splitext(os.path.basename(trait_config))[0]
        
        out_path = save_persona_vector(vector, model_name=model, trait_name=trait_name, out_dir=output_dir)
        typer.secho(f"✓ Successfully saved persona vector to: {out_path}", fg=typer.colors.GREEN, bold=True)
    except Exception as e:
        typer.secho(f"✗ Error: {str(e)}", fg=typer.colors.RED, bold=True, err=True)
        raise typer.Exit(code=1)


@app.command()
def scan_dataset(
    dataset_path: str = typer.Argument(..., help="Path to dataset JSONL file"),
    model: str = typer.Option(..., "--model", "-m", help="Model name"),
    traits: str = typer.Option(..., "--traits", "-t", help="Comma-separated trait names"),
):
    """
    Scan a fine-tuning dataset for trait amplification risk (Coming Soon).
    
    Example:
        persona-guardian scan-dataset data/train.jsonl --model llama-3-8b --traits sycophancy
    """
    typer.secho("Dataset scanning feature coming soon!", fg=typer.colors.YELLOW)
    typer.echo(f"Will scan: {dataset_path}")
    typer.echo(f"Model: {model}")
    typer.echo(f"Traits: {traits}")


if __name__ == "__main__":
    app()
