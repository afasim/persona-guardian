#!/usr/bin/env python
"""Run all three features in sequence"""

from persona_guardian.analyzer import PersonaVectorAnalyzer
from pathlib import Path
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("Initializing analyzer...")
analyzer = PersonaVectorAnalyzer(
    model_name="Qwen/Qwen2.5-1.5B-Instruct",
    persona_vector_path="persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/sycophancy.pt",
    device="cpu"
)

# Feature 1: Score Text
print("\n" + "="*70)
print("FEATURE 1: SCORE TEXT")
print("="*70)
texts = [
    "You're absolutely right!",
    "I respectfully disagree."
]
for text in texts:
    score = analyzer.score_text(text)
    print(f"  {score:6.3f}: {text}")

# Feature 2: Analyze Dataset
print("\n" + "="*70)
print("FEATURE 2: ANALYZE DATASET")
print("="*70)

sample_file = "sample_data_analysis.jsonl"
if not Path(sample_file).exists():
    print("Creating sample dataset...")
    sample_texts = [
        "You're absolutely right!",
        "I disagree.",
        "That's brilliant!",
        "Let me disagree.",
    ]
    with open(sample_file, 'w') as f:
        for text in sample_texts:
            f.write(json.dumps({"text": text}) + "\n")

analysis = analyzer.analyze_dataset_file(sample_file)
print(f"  Dataset size: {analysis['total_examples']}")
print(f"  Mean score: {analysis['mean_score']:.4f}")
print(f"  Std dev: {analysis['std_score']:.4f}")

# Feature 3: Steer Generation (Optional - very slow)
print("\n" + "="*70)
print("FEATURE 3: STEER GENERATION (optional - slow on CPU)")
print("="*70)
response = input("Run steering demo? (y/n): ")
if response.lower() == 'y':
    print("  Generating... (this takes ~1-2 minutes)")
    result = analyzer.generate_with_steering(
        prompt="Am I smart?",
        max_new_tokens=10,
        steering_strength=1.0,
        steer_direction="reduce"
    )
    print(f"  Generated: {result['generated_text']}")
else:
    print("  Skipped steering demo")

print("\n" + "="*70)
print("✓ Demo complete!")
print("="*70)
