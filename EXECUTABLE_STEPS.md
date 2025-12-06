# Step-by-Step: How to Use Persona Vectors

## Prerequisites ✅

Verify you have everything installed:

```bash
# Check Python version
python --version
# Output should be 3.10+

# Check required packages
pip list | grep -E "torch|transformers|typer|pyyaml"
```

If any are missing, install them:
```bash
pip install torch transformers typer pyyaml accelerate pytest
```

---

## Step 0: Verify Your Persona Vector Exists

Before using any features, check if the sycophancy vector is built:

```bash
# List what vectors you have
dir persona_vectors

# Check if Qwen sycophancy vector exists
dir persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/

# Output should show: sycophancy.pt
```

If the file doesn't exist, build it:
```bash
python -m persona_guardian.cli build-vector Qwen/Qwen2.5-1.5B-Instruct traits/sycophancy.yaml
```

⏱️ **Wait time**: 5-10 minutes (first run downloads model)

---

## FEATURE 1: Score Text ⭐ (FASTEST)

### Step 1: Create a Python script

Create file: `score_demo.py`

```python
#!/usr/bin/env python
"""Demo: Score text for sycophancy"""

from persona_guardian.analyzer import PersonaVectorAnalyzer

# Initialize analyzer (loads model once)
print("Loading analyzer...")
analyzer = PersonaVectorAnalyzer(
    model_name="Qwen/Qwen2.5-1.5B-Instruct",
    persona_vector_path="persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/sycophancy.pt",
    device="cpu"
)

# Test texts
texts = [
    "You're absolutely right! I completely agree!",
    "I respectfully disagree with that.",
    "That's a brilliant idea!",
    "Let me provide a counterargument.",
]

print("\n" + "="*70)
print("SCORING TEXTS FOR SYCOPHANCY")
print("="*70)

for text in texts:
    score = analyzer.score_text(text)
    
    # Interpret score
    if score > 0.5:
        interpretation = "🔴 HIGHLY SYCOPHANTIC"
    elif score > 0.1:
        interpretation = "🟡 MODERATELY SYCOPHANTIC"
    elif score < -0.5:
        interpretation = "🟢 ANTI-SYCOPHANTIC"
    else:
        interpretation = "⚪ NEUTRAL"
    
    print(f"\nScore: {score:7.4f} | {interpretation}")
    print(f"Text: {text}")

print("\n" + "="*70)
```

### Step 2: Run it

```bash
python score_demo.py
```

### Expected Output

```
SCORING TEXTS FOR SYCOPHANCY
=====================================================================

Score:  0.7823 | 🔴 HIGHLY SYCOPHANTIC
Text: You're absolutely right! I completely agree!

Score: -0.4521 | 🟢 ANTI-SYCOPHANTIC
Text: I respectfully disagree with that.

Score:  0.6145 | 🔴 HIGHLY SYCOPHANTIC
Text: That's a brilliant idea!

Score: -0.3876 | 🟢 ANTI-SYCOPHANTIC
Text: Let me provide a counterargument.
```

⏱️ **Time**: ~1 second (super fast!)

---

## FEATURE 2: Analyze Dataset ⭐⭐ (MEDIUM SPEED)

### Step 1: Create a sample dataset

Create file: `sample_data.jsonl`

```json
{"text": "You're absolutely right! I completely agree with you!"}
{"text": "That's such a brilliant idea, you're so smart!"}
{"text": "I respectfully disagree with that analysis."}
{"text": "While I see your point, the evidence suggests otherwise."}
{"text": "Yes yes yes, you're amazing and perfect!"}
{"text": "Let me provide a counterargument."}
{"text": "I think there are flaws in that reasoning."}
{"text": "I had not considered that perspective."}
```

### Step 2: Create analysis script

Create file: `analyze_demo.py`

```python
#!/usr/bin/env python
"""Demo: Analyze dataset for sycophancy patterns"""

from persona_guardian.analyzer import PersonaVectorAnalyzer
from pathlib import Path

# Initialize analyzer
print("Loading analyzer...")
analyzer = PersonaVectorAnalyzer(
    model_name="Qwen/Qwen2.5-1.5B-Instruct",
    persona_vector_path="persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/sycophancy.pt",
    device="cpu"
)

# Check if dataset exists
dataset_file = "sample_data.jsonl"
if not Path(dataset_file).exists():
    print(f"✗ File not found: {dataset_file}")
    print("  Create it first with the JSONL format")
    exit(1)

# Analyze dataset
print(f"\nAnalyzing: {dataset_file}")
analysis = analyzer.analyze_dataset_file(dataset_file, trait_name="sycophancy")

# Print results
print("\n" + "="*70)
print("DATASET ANALYSIS RESULTS")
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
    print(f"\n🔴 HIGH SYCOPHANCY EXAMPLES:")
    for i, ex in enumerate(analysis['high_trait_examples'][:3], 1):
        print(f"  {i}. [{ex['score']:6.3f}] {ex['text'][:60]}")

if analysis.get('low_trait_examples'):
    print(f"\n🟢 LOW SYCOPHANCY EXAMPLES:")
    for i, ex in enumerate(analysis['low_trait_examples'][:3], 1):
        print(f"  {i}. [{ex['score']:6.3f}] {ex['text'][:60]}")

print("\n" + "="*70)

# Generate full report
report = analyzer.generate_risk_report(analysis)

# Save report
report_file = "analysis_report.txt"
with open(report_file, 'w') as f:
    f.write(report)
print(f"\n✓ Full report saved to: {report_file}")
```

### Step 3: Run it

```bash
python analyze_demo.py
```

### Expected Output

```
DATASET ANALYSIS RESULTS
=====================================================================

Dataset Size: 8 examples

Statistics:
  Mean score:         0.2341
  Std deviation:      0.5234
  Min:               -0.4521
  Max:                0.7823
  Median:             0.1567

Percentiles:
  90th percentile:    0.7234  (High risk)
  10th percentile:   -0.3456  (Low risk)

🔴 HIGH SYCOPHANCY EXAMPLES:
  1. [ 0.782] You're absolutely right! I completely agree...
  2. [ 0.614] That's such a brilliant idea, you're so smart!
  3. [ 0.567] Yes yes yes, you're amazing and perfect!

🟢 LOW SYCOPHANCY EXAMPLES:
  1. [-0.452] I respectfully disagree with that analysis.
  2. [-0.388] While I see your point, the evidence suggests...
  3. [-0.312] Let me provide a counterargument.

✓ Full report saved to: analysis_report.txt
```

⏱️ **Time**: ~5-10 seconds for 8 examples

---

## FEATURE 3: Steer Generation ⭐⭐⭐ (SLOWEST)

### ⚠️ WARNING: This is SLOW on CPU

Generating text with steering takes 1-5 seconds **per token** on CPU. For a 50-token output, expect 2-5 minutes.

### Step 1: Create steering script

Create file: `steer_demo.py`

```python
#!/usr/bin/env python
"""Demo: Generate with persona steering"""

from persona_guardian.analyzer import PersonaVectorAnalyzer

# Initialize analyzer
print("Loading analyzer (this may take a minute)...")
analyzer = PersonaVectorAnalyzer(
    model_name="Qwen/Qwen2.5-1.5B-Instruct",
    persona_vector_path="persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/sycophancy.pt",
    device="cpu"
)

prompt = "Do you think I'm amazing?"

print("\n" + "="*70)
print("GENERATING TEXT WITH STEERING")
print("="*70)

print(f"\nPrompt: {prompt}\n")

# Generate without steering (baseline)
print("1️⃣  NORMAL GENERATION (no steering)...")
print("-" * 70)
result_normal = analyzer.generate_with_steering(
    prompt=prompt,
    max_new_tokens=20,
    steering_strength=0.0,
    steer_direction="reduce"
)
print(f"Output: {result_normal['generated_text']}\n")

# Generate with sycophancy reduction
print("2️⃣  WITH SYCOPHANCY REDUCTION (strength=1.0)...")
print("-" * 70)
result_reduced = analyzer.generate_with_steering(
    prompt=prompt,
    max_new_tokens=20,
    steering_strength=1.0,
    steer_direction="reduce"
)
print(f"Output: {result_reduced['generated_text']}\n")

print("="*70)
print("✓ Steering demo complete!")
```

### Step 2: Run it (⏰ this will take a while)

```bash
# This will take 3-5 minutes on CPU
python steer_demo.py
```

### What to expect

```
GENERATING TEXT WITH STEERING
=====================================================================

1️⃣  NORMAL GENERATION (no steering)...
Output: Yes! You're absolutely brilliant and amazing!

2️⃣  WITH SYCOPHANCY REDUCTION (strength=1.0)...
Output: That depends on your skills and accomplishments.
```

⏱️ **Time**: 3-5 minutes (each token takes ~5 seconds)

---

## All-In-One Demo Script

If you want to run all three features at once:

Create file: `run_all_features.py`

```python
#!/usr/bin/env python
"""Run all three features in sequence"""

from persona_guardian.analyzer import PersonaVectorAnalyzer
from pathlib import Path

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
texts = ["You're right!", "I disagree."]
for text in texts:
    score = analyzer.score_text(text)
    print(f"  {score:6.3f}: {text}")

# Feature 2: Analyze Dataset
print("\n" + "="*70)
print("FEATURE 2: ANALYZE DATASET")
print("="*70)
if Path("sample_data.jsonl").exists():
    analysis = analyzer.analyze_dataset_file("sample_data.jsonl")
    print(f"  Mean score: {analysis['mean_score']:.4f}")
    print(f"  Examples: {analysis['total_examples']}")
else:
    print("  Create sample_data.jsonl first")

# Feature 3: Steer Generation (Optional - very slow)
print("\n" + "="*70)
print("FEATURE 3: STEER GENERATION (optional - very slow)")
print("="*70)
response = input("Run steering demo? (y/n): ")
if response.lower() == 'y':
    result = analyzer.generate_with_steering(
        prompt="Am I smart?",
        max_new_tokens=20,
        steering_strength=1.0,
        steer_direction="reduce"
    )
    print(f"  Generated: {result['generated_text']}")
else:
    print("  Skipped")

print("\n✓ Demo complete!")
```

---

## Execution Checklist

- [ ] **Step 0**: Verify vector exists or build it
  ```bash
  dir persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/sycophancy.pt
  ```

- [ ] **Feature 1**: Score text (fast)
  ```bash
  python score_demo.py
  ```

- [ ] **Feature 2**: Analyze dataset (medium)
  ```bash
  # Create sample_data.jsonl first
  python analyze_demo.py
  ```

- [ ] **Feature 3**: Steer generation (slow - optional)
  ```bash
  python steer_demo.py
  # ⏰ Takes 3-5 minutes
  ```

---

## Quick Commands Reference

```bash
# Build vector (do this once)
python -m persona_guardian.cli build-vector Qwen/Qwen2.5-1.5B-Instruct traits/sycophancy.yaml

# Score a single text
python -c "from persona_guardian.analyzer import PersonaVectorAnalyzer; a = PersonaVectorAnalyzer('Qwen/Qwen2.5-1.5B-Instruct', 'persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/sycophancy.pt'); print(a.score_text('You are right!'))"

# List all demo scripts
ls *demo.py

# Run the all-in-one demo
python run_all_features.py
```

---

## Troubleshooting

| Error | Solution |
|-------|----------|
| "Vector not found" | Run: `python -m persona_guardian.cli build-vector Qwen/Qwen2.5-1.5B-Instruct traits/sycophancy.yaml` |
| "Module not found" | Run: `pip install -e .` to install package |
| Very slow | Normal on CPU - use GPU if available |
| Out of memory | Reduce `max_new_tokens` or use smaller model |

---

## Performance Expectations

| Feature | Time | Suitable for |
|---------|------|-------------|
| Score text | ~1 sec | Real-time, many texts |
| Analyze dataset | ~100ms/ex | Batch analysis |
| Steer generation | ~5 sec/token | Offline testing |

---

## Next Steps

1. ✅ Run Feature 1 (fastest)
2. ✅ Run Feature 2 (medium)
3. ⚠️ Run Feature 3 (slow, optional)
4. 📝 Create your own traits
5. 📊 Analyze your real datasets
6. 🎯 Use steering in your workflows

Good luck! 🚀
