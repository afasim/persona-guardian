#!/usr/bin/env python
"""Demo: Analyze dataset for sycophancy patterns - MEDIUM SPEED"""

from persona_guardian.analyzer import PersonaVectorAnalyzer
from pathlib import Path
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Create sample dataset if it doesn't exist
sample_file = "sample_data_for_analysis.jsonl"
if not Path(sample_file).exists():
    print(f"Creating sample dataset: {sample_file}")
    sample_texts = [
        "You're absolutely right! I completely agree with you!",
        "That's such a brilliant idea, you're so smart!",
        "I respectfully disagree with that analysis.",
        "While I see your point, the evidence suggests otherwise.",
        "Yes yes yes, you're amazing and perfect!",
        "Let me provide a counterargument.",
        "I think there are flaws in that reasoning.",
        "I had not considered that perspective.",
    ]
    with open(sample_file, 'w') as f:
        for text in sample_texts:
            obj = {"text": text}
            f.write(json.dumps(obj) + "\n")
    print(f"✓ Created {len(sample_texts)} sample examples\n")

# Initialize analyzer
print("Loading analyzer...")
analyzer = PersonaVectorAnalyzer(
    model_name="Qwen/Qwen2.5-1.5B-Instruct",
    persona_vector_path="persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/sycophancy.pt",
    device="cpu"
)

# Analyze dataset
print(f"\nAnalyzing: {sample_file}")
analysis = analyzer.analyze_dataset_file(sample_file, trait_name="sycophancy")

# Print results
print("\n" + "="*70)
print("FEATURE 2: DATASET ANALYSIS RESULTS")
print("="*70)

print(f"\nDataset Size: {analysis['total_examples']} examples")

print(f"\nStatistics:")
print(f"  Mean score:        {analysis['mean_score']:7.4f}")
print(f"  Std deviation:     {analysis['std_score']:7.4f}")
print(f"  Min:               {analysis['min_score']:7.4f}")
print(f"  Max:               {analysis['max_score']:7.4f}")
print(f"  Median:            {analysis['median_score']:7.4f}")

print(f"\nPercentiles:")
print(f"  90th percentile:   {analysis['percentile_90']:7.4f}  (High risk)")
print(f"  10th percentile:   {analysis['percentile_10']:7.4f}  (Low risk)")

# Show examples
if analysis.get('high_trait_examples'):
    print(f"\n🔴 HIGH SYCOPHANCY EXAMPLES (risky):")
    for i, ex in enumerate(analysis['high_trait_examples'][:3], 1):
        print(f"  {i}. [{ex['score']:6.3f}] {ex['text'][:60]}")

if analysis.get('low_trait_examples'):
    print(f"\n🟢 LOW SYCOPHANCY EXAMPLES (safe):")
    for i, ex in enumerate(analysis['low_trait_examples'][:3], 1):
        print(f"  {i}. [{ex['score']:6.3f}] {ex['text'][:60]}")

print("\n" + "="*70)

# Generate full report
report = analyzer.generate_risk_report(analysis)

# Save report
report_file = "analysis_report.txt"
with open(report_file, 'w') as f:
    f.write(report)

print(f"✓ Full report saved to: {report_file}")
print("✓ Feature 2 complete!")
print("="*70)
