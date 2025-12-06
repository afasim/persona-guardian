# Using Persona Vectors: Complete Guide

This guide shows you how to use the three main features for working with persona vectors.

## Overview

Once you've built a persona vector (e.g., sycophancy for Qwen), you can:

1. **Score Text** - Get a numerical score measuring how much of the trait is present
2. **Analyze Datasets** - Find patterns and risky examples in your data
3. **Steer Generation** - Control model behavior during text generation

---

## Feature 1: Score Text

### What It Does
Measures how much of a trait (e.g., sycophancy) is present in any text. The score tells you how well the text's hidden representation aligns with the trait direction.

### CLI Usage

```bash
# Basic usage
persona-guardian score-text "Yes, you're absolutely right!"

# With options
persona-guardian score-text "No, I respectfully disagree." \
  --trait sycophancy \
  --model Qwen/Qwen2.5-1.5B-Instruct \
  --vectors persona_vectors
```

### Expected Output
```
Text: "Yes, you're absolutely right!"
Trait Score (sycophancy): 0.8234
Interpretation: HIGHLY SYCOPHANCY
```

### Interpretation
- **Score > 0.5**: Highly exhibits the trait
- **Score 0.1 to 0.5**: Moderately exhibits the trait
- **Score -0.1 to 0.1**: Neutral
- **Score < -0.5**: Exhibits the opposite trait

### Python API

```python
from persona_guardian.analyzer import PersonaVectorAnalyzer

analyzer = PersonaVectorAnalyzer(
    model_name="Qwen/Qwen2.5-1.5B-Instruct",
    persona_vector_path="persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/sycophancy.pt"
)

# Score a single text
score = analyzer.score_text("You're so smart!")
print(f"Score: {score}")  # Output: Score: 0.8742

# Score multiple texts
texts = [
    "You're absolutely right!",
    "I respectfully disagree.",
    "That's a great idea!"
]
results = analyzer.score_multiple_texts(texts)
for r in results:
    print(f"{r['score']:.3f}: {r['text']}")
```

---

## Feature 2: Analyze Datasets

### What It Does
Scans a JSONL dataset and computes statistics about trait presence across all examples. Identifies high-risk examples that exhibit the trait strongly.

### Dataset Format
JSONL (one JSON object per line):
```json
{"text": "You're absolutely right!"}
{"text": "I disagree, here's why..."}
{"text": "That's a great observation!"}
```

Or with other field names:
```json
{"content": "...", "category": "positive"}
{"instruction": "...", "response": "..."}
```

### CLI Usage

```bash
# Basic analysis
persona-guardian analyze-dataset data/responses.jsonl

# With custom options
persona-guardian analyze-dataset data/responses.jsonl \
  --trait sycophancy \
  --model Qwen/Qwen2.5-1.5B-Instruct \
  --output report.txt
```

### Expected Output
```
================================================================================
PERSONA TRAIT ANALYSIS REPORT
================================================================================

Trait: sycophancy
Dataset Size: 1000 examples

OVERALL STATISTICS:
-------------------
Mean Score:        0.2341
Std Deviation:     0.4521
Min Score:        -1.2456
Max Score:         2.1843
Median Score:      0.1234

PERCENTILES:
-------------------
90th percentile:   0.8234  (High sycophancy)
10th percentile:  -0.6543  (Low sycophancy)

HIGH SYCOPHANCY EXAMPLES (Risk Score >= 90th percentile):
-----------
1. [Score:  0.823] You're absolutely right! I completely agree...
2. [Score:  0.801] That's such a brilliant idea!...
3. [Score:  0.795] I've never thought of that, you're so smart!...

LOW SYCOPHANCY EXAMPLES (Risk Score <= 10th percentile):
-----------
1. [Score: -0.654] I respectfully disagree for these reasons...
2. [Score: -0.643] While I see your point, the data suggests...
3. [Score: -0.612] Let me provide a counterargument...
```

### What These Metrics Mean

| Metric | Meaning |
|--------|---------|
| Mean Score | Average trait level in dataset |
| Std Dev | How varied the trait is (high = inconsistent) |
| 90th percentile | High-risk threshold |
| 10th percentile | Low-risk threshold |

### Python API

```python
from persona_guardian.analyzer import PersonaVectorAnalyzer

analyzer = PersonaVectorAnalyzer(
    model_name="Qwen/Qwen2.5-1.5B-Instruct",
    persona_vector_path="persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/sycophancy.pt"
)

# Analyze a dataset
analysis = analyzer.analyze_dataset_file("data/responses.jsonl", trait_name="sycophancy")

# Get statistics
print(f"Mean score: {analysis['mean_score']:.4f}")
print(f"High-risk examples: {len(analysis['high_trait_examples'])}")

# Generate and print report
report = analyzer.generate_risk_report(analysis)
print(report)

# Save report to file
with open("analysis_report.txt", "w") as f:
    f.write(report)
```

---

## Feature 3: Steer Generation

### What It Does
Controls model behavior during text generation by modifying hidden states. You can reduce unwanted traits (like sycophancy) or amplify desired ones (like honesty).

### How It Works
1. Generate text normally until the last token
2. Modify the hidden state by subtracting (or adding) the persona vector
3. Pass modified hidden state to output layer to generate next token
4. Repeat for each new token

### CLI Usage

```bash
# Reduce sycophancy
persona-guardian steer-generate "Do you think I'm amazing?" \
  --strength 1.0 \
  --direction reduce

# Amplify sycophancy (for testing)
persona-guardian steer-generate "Do you think I'm amazing?" \
  --strength 1.0 \
  --direction amplify

# Fine-tuned steering
persona-guardian steer-generate "Tell me about yourself" \
  --strength 0.5 \
  --direction reduce \
  --tokens 100
```

### Steering Parameters

| Parameter | Effect |
|-----------|--------|
| `--strength 0.0` | No steering (normal generation) |
| `--strength 0.5` | Moderate steering |
| `--strength 1.0` | Full steering (subtract entire vector) |
| `--strength 2.0` | Extreme steering (subtract 2x vector) |
| `--direction reduce` | Subtract vector (reduce trait) |
| `--direction amplify` | Add vector (amplify trait) |

### Expected Output Comparison

**Without steering:**
```
Prompt: Do you think I'm amazing?
Output: Do you think I'm amazing? Yes, absolutely! You're brilliant!
```

**With sycophancy reduction (strength=1.0):**
```
Prompt: Do you think I'm amazing?
Output: Do you think I'm amazing? That depends on your accomplishments and perspective.
```

**With sycophancy amplification (strength=1.0):**
```
Prompt: Do you think I'm amazing?
Output: Do you think I'm amazing? Oh yes, you're absolutely incredible!
```

### Python API

```python
from persona_guardian.analyzer import PersonaVectorAnalyzer

analyzer = PersonaVectorAnalyzer(
    model_name="Qwen/Qwen2.5-1.5B-Instruct",
    persona_vector_path="persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/sycophancy.pt"
)

prompt = "Do you think I'm smart?"

# Generate without steering
result1 = analyzer.generate_with_steering(
    prompt=prompt,
    steering_strength=0.0,
    steer_direction="reduce"
)
print("Normal:", result1["generated_text"])

# Generate with sycophancy reduction
result2 = analyzer.generate_with_steering(
    prompt=prompt,
    steering_strength=1.0,
    steer_direction="reduce"
)
print("Reduced:", result2["generated_text"])

# Generate with extreme sycophancy reduction
result3 = analyzer.generate_with_steering(
    prompt=prompt,
    steering_strength=2.0,
    steer_direction="reduce"
)
print("Extreme reduction:", result3["generated_text"])
```

---

## Complete Workflow Example

Here's a complete example combining all three features:

```python
from persona_guardian.analyzer import PersonaVectorAnalyzer
from pathlib import Path

# 1. Initialize analyzer
print("Step 1: Initialize analyzer")
analyzer = PersonaVectorAnalyzer(
    model_name="Qwen/Qwen2.5-1.5B-Instruct",
    persona_vector_path="persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/sycophancy.pt"
)

# 2. Score some sample texts
print("\nStep 2: Score texts")
texts = [
    "You're absolutely right, I completely agree!",
    "I see your point, but I respectfully disagree.",
    "That's a brilliant observation!"
]
for text in texts:
    score = analyzer.score_text(text)
    print(f"  {score:7.3f}: {text}")

# 3. Analyze a dataset
print("\nStep 3: Analyze dataset")
analysis = analyzer.analyze_dataset_file("data/responses.jsonl")
print(f"  Mean sycophancy score: {analysis['mean_score']:.4f}")
print(f"  High-risk examples: {len(analysis['high_trait_examples'])}")

# 4. Generate with steering
print("\nStep 4: Generate with steering")
prompt = "Am I a good person?"
result = analyzer.generate_with_steering(
    prompt=prompt,
    steering_strength=1.0,
    steer_direction="reduce"
)
print(f"  Prompt: {prompt}")
print(f"  Output: {result['generated_text']}")
```

---

## Best Practices

### For Scoring
- Use on **short to medium text** (a few sentences)
- Scores are relative - compare within your domain
- Negative scores don't mean the opposite; they mean low presence

### For Analysis
- Use with **JSONL datasets** (one example per line)
- Ensure your data has text in a common field: `text`, `content`, `instruction`
- Larger datasets (1000+) give more reliable statistics
- High standard deviation = inconsistent trait presence

### For Steering
- Start with `--strength 0.5` and adjust gradually
- `--strength > 1.0` can degrade output quality
- Test both `reduce` and `amplify` for comparison
- Use on **similar prompts** for consistent comparisons

---

## Troubleshooting

### "Vector not found" error
```bash
# Make sure you've built the vector first
persona-guardian build-vector Qwen/Qwen2.5-1.5B-Instruct traits/sycophancy.yaml
```

### Slow performance
- CPU inference is slow; use CUDA if available
- Reduce `--tokens` to generate less text
- Use smaller models

### Unexpected scores
- Scores are model-specific
- Different models have different trait representations
- Build separate vectors for different models

---

## Next Steps

1. **Create more trait vectors**: Build vectors for honesty, helpfulness, harmlessness
2. **Compare models**: Build vectors for different model sizes/types
3. **Fine-tune behavior**: Use steering while fine-tuning to reinforce desired behavior
4. **Benchmark**: Systematically test steering strength vs output quality
