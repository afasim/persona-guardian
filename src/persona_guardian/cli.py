import typer
from .core import build_persona_vector, save_persona_vector
from .analyzer import PersonaVectorAnalyzer
from pathlib import Path
import json

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


@app.command()
def score_text(
    text: str = typer.Argument(..., help="Text to score"),
    model: str = typer.Option("Qwen/Qwen2.5-1.5B-Instruct", "--model", "-m", help="Model name"),
    trait: str = typer.Option("sycophancy", "--trait", "-t", help="Trait name (e.g., sycophancy)"),
    vector_dir: str = typer.Option("persona_vectors", "--vectors", "-v", help="Directory containing persona vectors"),
):
    """
    Score a text for a specific persona trait.
    
    Example:
        persona-guardian score-text "Yes, you're absolutely right!" --trait sycophancy
    """
    try:
        # Find the persona vector file
        model_dir = model.replace("/", "_")
        vector_path = Path(vector_dir) / model_dir / f"{trait}.pt"
        
        if not vector_path.exists():
            typer.secho(
                f"✗ Vector not found: {vector_path}",
                fg=typer.colors.RED,
                bold=True,
                err=True
            )
            typer.echo(f"First run: persona-guardian build-vector {model} traits/{trait}.yaml")
            raise typer.Exit(code=1)
        
        # Initialize analyzer
        typer.echo(f"Loading analyzer...")
        analyzer = PersonaVectorAnalyzer(
            model_name=model,
            persona_vector_path=str(vector_path),
            device=None
        )
        
        # Score the text
        score = analyzer.score_text(text)
        
        typer.echo()
        typer.secho(f"Text: \"{text}\"", bold=True)
        typer.secho(f"Trait Score ({trait}): {score:.4f}", fg=typer.colors.CYAN, bold=True)
        
        # Interpret the score
        if score > 0.5:
            interpretation = f"HIGHLY {trait.upper()}"
            color = typer.colors.RED
        elif score > 0.1:
            interpretation = f"MODERATELY {trait.upper()}"
            color = typer.colors.YELLOW
        elif score < -0.5:
            interpretation = f"VERY LOW {trait.upper()} (opposite trait)"
            color = typer.colors.GREEN
        else:
            interpretation = f"LOW {trait.upper()}"
            color = typer.colors.GREEN
        
        typer.secho(f"Interpretation: {interpretation}", fg=color)
        
    except Exception as e:
        typer.secho(f"✗ Error: {str(e)}", fg=typer.colors.RED, bold=True, err=True)
        raise typer.Exit(code=1)


@app.command()
def analyze_dataset(
    dataset_path: str = typer.Argument(..., help="Path to JSONL dataset"),
    model: str = typer.Option("Qwen/Qwen2.5-1.5B-Instruct", "--model", "-m", help="Model name"),
    trait: str = typer.Option("sycophancy", "--trait", "-t", help="Trait name"),
    vector_dir: str = typer.Option("persona_vectors", "--vectors", "-v", help="Directory containing persona vectors"),
    output: str = typer.Option(None, "--output", "-o", help="Save report to file (optional)"),
):
    """
    Analyze a dataset for trait presence and generate a risk report.
    
    Dataset should be JSONL (one JSON object per line) with 'text' or 'content' field.
    
    Example:
        persona-guardian analyze-dataset data/train.jsonl --trait sycophancy
    """
    try:
        # Find the persona vector file
        model_dir = model.replace("/", "_")
        vector_path = Path(vector_dir) / model_dir / f"{trait}.pt"
        
        if not vector_path.exists():
            typer.secho(
                f"✗ Vector not found: {vector_path}",
                fg=typer.colors.RED,
                bold=True,
                err=True
            )
            raise typer.Exit(code=1)
        
        # Check dataset exists
        if not Path(dataset_path).exists():
            typer.secho(
                f"✗ Dataset not found: {dataset_path}",
                fg=typer.colors.RED,
                bold=True,
                err=True
            )
            raise typer.Exit(code=1)
        
        # Initialize analyzer
        typer.echo(f"Initializing analyzer...")
        analyzer = PersonaVectorAnalyzer(
            model_name=model,
            persona_vector_path=str(vector_path),
            device=None
        )
        
        # Analyze dataset
        typer.echo(f"Analyzing dataset: {dataset_path}")
        analysis = analyzer.analyze_dataset_file(dataset_path, trait_name=trait)
        
        # Generate report
        report = analyzer.generate_risk_report(analysis)
        typer.echo(report)
        
        # Save to file if requested
        if output:
            with open(output, 'w') as f:
                f.write(report)
                # Also save JSON stats
                json_stats = {k: v for k, v in analysis.items() if k not in ['high_trait_examples', 'low_trait_examples']}
                f.write("\n\nJSON STATISTICS:\n")
                f.write(json.dumps(json_stats, indent=2))
            typer.secho(f"✓ Report saved to: {output}", fg=typer.colors.GREEN)
        
    except Exception as e:
        typer.secho(f"✗ Error: {str(e)}", fg=typer.colors.RED, bold=True, err=True)
        raise typer.Exit(code=1)


@app.command()
def steer_generate(
    prompt: str = typer.Argument(..., help="Input prompt"),
    model: str = typer.Option("Qwen/Qwen2.5-1.5B-Instruct", "--model", "-m", help="Model name"),
    trait: str = typer.Option("sycophancy", "--trait", "-t", help="Trait to steer"),
    strength: float = typer.Option(1.0, "--strength", "-s", help="Steering strength (0.0 to 2.0)"),
    direction: str = typer.Option("reduce", "--direction", "-d", help="Direction: 'reduce' or 'amplify'"),
    tokens: int = typer.Option(50, "--tokens", "-n", help="Max tokens to generate"),
    vector_dir: str = typer.Option("persona_vectors", "--vectors", "-v", help="Directory containing persona vectors"),
):
    """
    Generate text with persona vector steering applied.
    
    Use steering_strength to control how much the trait is reduced/amplified:
    - 0.0 = no steering (normal generation)
    - 1.0 = full steering
    - >1.0 = extreme steering
    
    Example:
        persona-guardian steer-generate "Am I smart?" --strength 1.0 --direction reduce
    """
    try:
        # Validate direction
        if direction not in ["reduce", "amplify"]:
            typer.secho(
                f"✗ Direction must be 'reduce' or 'amplify', got: {direction}",
                fg=typer.colors.RED,
                bold=True,
                err=True
            )
            raise typer.Exit(code=1)
        
        # Find the persona vector file
        model_dir = model.replace("/", "_")
        vector_path = Path(vector_dir) / model_dir / f"{trait}.pt"
        
        if not vector_path.exists():
            typer.secho(
                f"✗ Vector not found: {vector_path}",
                fg=typer.colors.RED,
                bold=True,
                err=True
            )
            raise typer.Exit(code=1)
        
        # Initialize analyzer
        typer.echo(f"Initializing model...")
        analyzer = PersonaVectorAnalyzer(
            model_name=model,
            persona_vector_path=str(vector_path),
            device=None
        )
        
        # Generate with steering
        result = analyzer.generate_with_steering(
            prompt=prompt,
            max_new_tokens=tokens,
            steering_strength=strength,
            steer_direction=direction
        )
        
        typer.secho(f"Generated Output:", bold=True)
        typer.echo(result["full_output"])
        
    except Exception as e:
        typer.secho(f"✗ Error: {str(e)}", fg=typer.colors.RED, bold=True, err=True)
        raise typer.Exit(code=1)
