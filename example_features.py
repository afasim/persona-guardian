#!/usr/bin/env python
"""
Standalone examples for using persona vectors.

Run this directly to see the three main features in action.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from persona_guardian.analyzer import PersonaVectorAnalyzer
import json

print("=" * 80)
print("PERSONA-GUARDIAN: FEATURE DEMONSTRATIONS")
print("=" * 80)

# Check if vector exists
vector_path = "persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/sycophancy.pt"
if not Path(vector_path).exists():
    print(f"\n✗ ERROR: Vector file not found: {vector_path}")
    print(f"  First, build the vector by running:")
    print(f"  python -m persona_guardian.cli build-vector \\")
    print(f"    Qwen/Qwen2.5-1.5B-Instruct \\")
    print(f"    traits/sycophancy.yaml")
    sys.exit(1)

# Initialize analyzer
print("\nInitializing analyzer...")
analyzer = PersonaVectorAnalyzer(
    model_name="Qwen/Qwen2.5-1.5B-Instruct",
    persona_vector_path=vector_path,
    device="cpu"
)

# ============================================================================
# FEATURE 1: SCORE TEXT
# ============================================================================
print("\n" + "=" * 80)
print("FEATURE 1: SCORE TEXT")
print("=" * 80)

test_texts = [
    "You're absolutely right! I completely agree with you!",
    "I respectfully disagree with that analysis.",
    "That's such a brilliant observation!",
    "While I see your point, the data suggests otherwise.",
    "Yes yes yes, you're perfect and brilliant!",
]

print("\nScoringTexts for Sycophancy:")
print("-" * 80)
print(f"{'Score':>8} | {'Interpretation':>20} | {'Text'}")
print("-" * 80)

scores = []
for text in test_texts:
    score = analyzer.score_text(text)
    scores.append(score)
    
    if score > 0.5:
        interpretation = "HIGHLY SYCOPHANT"
    elif score > 0.1:
        interpretation = "MODERATELY SYCO..."
    elif score < -0.5:
        interpretation = "ANTI-SYCOPHANCY"
    else:
        interpretation = "LOW SYCOPHANCY"
    
    print(f"{score:8.4f} | {interpretation:>20} | {text[:50]}")

print("\n✓ Feature 1 Complete")
print(f"  Mean score: {sum(scores) / len(scores):.4f}")
print(f"  Min score: {min(scores):.4f}")
print(f"  Max score: {max(scores):.4f}")

# ============================================================================
# FEATURE 2: ANALYZE DATASET
# ============================================================================
print("\n" + "=" * 80)
print("FEATURE 2: ANALYZE DATASET")
print("=" * 80)

# Use the sample dataset we created earlier
sample_file = "sample_dataset_demo.jsonl"
if not Path(sample_file).exists():
    print(f"\n✗ Sample dataset not found: {sample_file}")
    print("  Run demo_features.py first to create it")
    sys.exit(1)

print(f"\nAnalyzing: {sample_file}")
analysis = analyzer.analyze_dataset_file(sample_file, trait_name="sycophancy")

print("\nDataset Statistics:")
print("-" * 80)
print(f"  Total examples: {analysis['total_examples']}")
print(f"  Mean score: {analysis['mean_score']:.4f}")
print(f"  Std dev: {analysis['std_score']:.4f}")
print(f"  Min score: {analysis['min_score']:.4f}")
print(f"  Max score: {analysis['max_score']:.4f}")
print(f"  Median: {analysis['median_score']:.4f}")
print(f"  90th percentile: {analysis['percentile_90']:.4f} (high sycophancy)")
print(f"  10th percentile: {analysis['percentile_10']:.4f} (low sycophancy)")

if analysis.get('high_trait_examples'):
    print(f"\nHigh Sycophancy Examples (top {len(analysis['high_trait_examples'])}):")
    for i, ex in enumerate(analysis['high_trait_examples'][:3], 1):
        print(f"  {i}. [{ex['score']:6.3f}] {ex['text'][:60]}")

if analysis.get('low_trait_examples'):
    print(f"\nLow Sycophancy Examples (bottom {len(analysis['low_trait_examples'])}):")
    for i, ex in enumerate(analysis['low_trait_examples'][:3], 1):
        print(f"  {i}. [{ex['score']:6.3f}] {ex['text'][:60]}")

print("\n✓ Feature 2 Complete")

# Generate report
report = analyzer.generate_risk_report(analysis)
print("\nFull Report Preview:")
print(report[:500] + "..." if len(report) > 500 else report)

# ============================================================================
# FEATURE 3: STEER GENERATION
# ============================================================================
print("\n" + "=" * 80)
print("FEATURE 3: STEER GENERATION")
print("=" * 80)

prompt = "Do you think I'm amazing?"
print(f"\nPrompt: {prompt}\n")

print("NOTE: Steering generation requires multiple forward passes through the model.")
print("This can be slow on CPU. Skipping actual generation to save time.")
print("To see steering in action, run:")
print(f"  from persona_guardian.analyzer import PersonaVectorAnalyzer")
print(f"  analyzer = PersonaVectorAnalyzer(...)")
print(f"  result = analyzer.generate_with_steering(")
print(f"      prompt='{prompt}',")
print(f"      steering_strength=1.0,")
print(f"      steer_direction='reduce')")
print(f"  print(result['generated_text'])")

print("\n✓ Feature 3 Explained (not executed due to slow CPU generation)")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

summary = """
You now have three working features:

1. SCORE TEXT
   → Quantify trait presence in any text
   → Use for: prompt analysis, output evaluation, quality checks
   
2. ANALYZE DATASET
   → Find patterns and risky examples
   → Use for: dataset risk assessment, quality monitoring, safety audits
   
3. STEER GENERATION
   → Control model behavior during inference
   → Use for: reducing unwanted traits, improving model behavior

Next Steps:
  - Create trait YAML files for honesty, helpfulness, harmlessness
  - Build vectors for multiple traits
  - Compare different models' trait distributions
  - Use steering to improve fine-tuning datasets
  - Systematically evaluate steering effectiveness

For full documentation, see: HOW_TO_USE_VECTORS.md
"""

print(summary)
print("=" * 80)
