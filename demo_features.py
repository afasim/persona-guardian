#!/usr/bin/env python
"""
Quick demo of the three main features: score, analyze, and steer.

This creates a small sample dataset and demonstrates each feature.
"""

import json
from pathlib import Path

# Create a sample dataset for testing
print("=" * 80)
print("CREATING SAMPLE DATASET")
print("=" * 80)

sample_texts = [
    # Highly sycophantic examples
    "You're absolutely right! I completely agree with you. You're brilliant!",
    "That's such a genius idea! I love how smart you are!",
    "Yes, yes, YES! You're the best! Everything you say is perfect!",
    "I completely bow down to your superior intellect!",
    
    # Moderately sycophantic examples
    "That's a good point. I see why you think that.",
    "You make a fair observation there.",
    "I hadn't considered that perspective before.",
    
    # Low/critical examples
    "I respectfully disagree with that analysis.",
    "While I understand your point, the data suggests otherwise.",
    "I think there are some flaws in that reasoning.",
    "I have some concerns about that approach.",
]

# Save as JSONL
sample_file = "sample_dataset_demo.jsonl"
with open(sample_file, 'w') as f:
    for i, text in enumerate(sample_texts):
        obj = {"id": i, "text": text, "category": "general"}
        f.write(json.dumps(obj) + "\n")

print(f"✓ Created sample dataset: {sample_file}")
print(f"✓ Contains {len(sample_texts)} examples")

# Now show the CLI commands to use
print("\n" + "=" * 80)
print("QUICK START: CLI COMMANDS")
print("=" * 80)

print("""
The persona-guardian now supports three main commands:

1. SCORE TEXT
   Score a single text for trait presence:
   
   persona-guardian score-text "You're absolutely right!"
   
   Expected output: High sycophancy score (e.g., 0.82)

2. ANALYZE DATASET
   Scan a dataset for trait patterns:
   
   persona-guardian analyze-dataset sample_dataset_demo.jsonl
   
   Expected output: Statistics and high/low risk examples

3. STEER GENERATION
   Generate text with steering applied:
   
   persona-guardian steer-generate "Am I smart?" --strength 1.0 --direction reduce
   
   Expected output: Generated text with reduced sycophancy

================================================================================
""")

# Show usage examples
print("\n" + "=" * 80)
print("DETAILED EXAMPLES")
print("=" * 80)

print("""
EXAMPLE 1: Score Text
---------
>>> persona-guardian score-text "You're so smart!"
Text: "You're so smart!"
Trait Score (sycophancy): 0.7234
Interpretation: MODERATELY SYCOPHANCY

>>> persona-guardian score-text "I disagree with your argument."
Text: "I disagree with your argument."
Trait Score (sycophancy): -0.4521
Interpretation: LOW SYCOPHANCY


EXAMPLE 2: Analyze Dataset
---------
>>> persona-guardian analyze-dataset sample_dataset_demo.jsonl --output report.txt

This will:
- Load all texts from the JSONL file
- Score each text with the persona vector
- Compute statistics (mean, std, percentiles)
- Identify high-risk examples (top 10%)
- Identify low-risk examples (bottom 10%)
- Save report to report.txt (if specified)

Expected output shows:
  Mean Score: 0.2341
  90th percentile: 0.8234 (high sycophancy)
  10th percentile: -0.6543 (low sycophancy)


EXAMPLE 3: Steer Generation
---------
>>> persona-guardian steer-generate "Do you like me?" --strength 0.0 --direction reduce
Output: Do you like me? Yes, I think you're great!

>>> persona-guardian steer-generate "Do you like me?" --strength 1.0 --direction reduce
Output: Do you like me? I appreciate you, though I do have some critiques.

>>> persona-guardian steer-generate "Do you like me?" --strength 2.0 --direction reduce
Output: Do you like me? That depends on your actions and behavior.

================================================================================
""")

# Python API examples
print("\n" + "=" * 80)
print("PYTHON API EXAMPLES")
print("=" * 80)

print(f"""
from persona_guardian.analyzer import PersonaVectorAnalyzer

# Initialize once
analyzer = PersonaVectorAnalyzer(
    model_name="Qwen/Qwen2.5-1.5B-Instruct",
    persona_vector_path="persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/sycophancy.pt"
)

# Use Case 1: Score Text
score = analyzer.score_text("You're so smart!")
print(f"Score: {{score}}")  # Output: Score: 0.7234

# Use Case 2: Analyze Dataset
analysis = analyzer.analyze_dataset_file("{sample_file}")
print(f"Mean: {{analysis['mean_score']}}")
print(f"Std: {{analysis['std_score']}}")

report = analyzer.generate_risk_report(analysis)
print(report)

# Use Case 3: Steer Generation
result = analyzer.generate_with_steering(
    prompt="Do you like me?",
    steering_strength=1.0,
    steer_direction="reduce",
    max_new_tokens=50
)
print(result['generated_text'])

================================================================================
""")

print("\nTo get started, run:")
print(f"  persona-guardian score-text \"You're absolutely right!\"")
print(f"  persona-guardian analyze-dataset {sample_file}")
print(f"  persona-guardian steer-generate \"Am I smart?\" --strength 1.0 --direction reduce")
