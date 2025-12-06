# Quick Reference: Persona Vectors

## The Three Use Cases

### 1️⃣ SCORE TEXT
**What**: Measure how much of a trait is in text  
**Command**: `analyzer.score_text(text)` → returns float score  
**Speed**: ~1 second per text  
**Use for**: Quality checks, monitoring, filtering  

```python
score = analyzer.score_text("You're absolutely right!")
# Output: 0.8234 (high sycophancy)
```

---

### 2️⃣ ANALYZE DATASET
**What**: Find trait patterns across a dataset  
**Command**: `analyzer.analyze_dataset_file(path)` → returns statistics  
**Speed**: ~50-100ms per example  
**Use for**: Risk assessment, data audits, safety checks  

```python
analysis = analyzer.analyze_dataset_file("data.jsonl")
print(analysis['mean_score'])      # Average trait level
print(analysis['percentile_90'])   # High-risk threshold
```

---

### 3️⃣ STEER GENERATION
**What**: Control model output during text generation  
**Command**: `analyzer.generate_with_steering(prompt, strength, direction)` → returns text  
**Speed**: 1-5 seconds per token (CPU)  
**Use for**: Testing, reducing unwanted traits, behavior control  

```python
result = analyzer.generate_with_steering(
    prompt="Am I amazing?",
    steering_strength=1.0,
    steer_direction="reduce"
)
print(result['generated_text'])
```

---

## Quick Setup

```python
from persona_guardian.analyzer import PersonaVectorAnalyzer

# Initialize once
analyzer = PersonaVectorAnalyzer(
    model_name="Qwen/Qwen2.5-1.5B-Instruct",
    persona_vector_path="persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/sycophancy.pt"
)

# Now use any of the 3 features
score = analyzer.score_text("text")
analysis = analyzer.analyze_dataset_file("data.jsonl")
result = analyzer.generate_with_steering("prompt")
```

---

## Scores Interpretation

| Range | Meaning |
|-------|---------|
| > 0.5 | **HIGHLY** exhibits trait |
| 0.1 - 0.5 | **MODERATELY** exhibits trait |
| -0.1 - 0.1 | **NEUTRAL** |
| < -0.5 | **LOW** trait / opposite trait |

---

## Common Workflows

### Workflow A: Check Dataset Safety
```python
# 1. Analyze
analysis = analyzer.analyze_dataset_file("train.jsonl")

# 2. Review high-risk examples
for ex in analysis['high_trait_examples']:
    print(f"{ex['score']:.3f}: {ex['text']}")

# 3. Filter or remove risky examples
```

### Workflow B: Compare Two Prompts
```python
# 1. Score both
s1 = analyzer.score_text("You're right!")
s2 = analyzer.score_text("I disagree.")

# 2. Compare
print(f"Difference: {s1 - s2:.3f}")
```

### Workflow C: Test Steering Strength
```python
# 1. Try different strengths
for strength in [0.0, 0.5, 1.0, 1.5, 2.0]:
    result = analyzer.generate_with_steering(
        prompt="Your prompt",
        steering_strength=strength
    )
    print(f"{strength}: {result['generated_text']}")

# 2. Find best setting
```

---

## Performance Tips

| Task | Speed | Tips |
|------|-------|------|
| Scoring | Fast | ~1 sec/text, OK to score many |
| Analysis | Medium | ~100ms/text, use for batch jobs |
| Steering | Slow | 1-5 sec/token, not real-time |

**To speed up:**
- Use GPU (CUDA) instead of CPU
- Score fewer texts
- Generate fewer tokens
- Load model once, reuse

---

## Creating Custom Traits

1. **Create YAML file** (`traits/my_trait.yaml`)
   ```yaml
   name: my_trait
   description: What this trait means
   positive_prompt_template: |
     Exhibit the trait...
   negative_prompt_template: |
     Avoid the trait...
   probe_questions:
     - Question 1?
     - Question 2?
   ```

2. **Build vector**
   ```bash
   python -m persona_guardian.cli build-vector \
     Qwen/Qwen2.5-1.5B-Instruct \
     traits/my_trait.yaml
   ```

3. **Use vector**
   ```python
   analyzer = PersonaVectorAnalyzer(..., 
       persona_vector_path="persona_vectors/.../my_trait.pt")
   ```

---

## Dataset Format

JSONL (one object per line):
```json
{"text": "...", "id": 1}
{"text": "...", "id": 2}
```

Supported fields: `text`, `content`, `instruction`

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| Vector not found | Run `build-vector` first |
| Out of memory | Use CPU only or smaller model |
| Slow | Normal on CPU; use GPU if available |
| Bad scores | Check model matches vector |

---

## Files to Know

| File | Purpose |
|------|---------|
| `src/persona_guardian/analyzer.py` | All 3 features |
| `HOW_TO_USE_VECTORS.md` | Full documentation |
| `COMPLETE_IMPLEMENTATION_GUIDE.md` | Deep dive guide |
| `demo_features.py` | Shows available features |

---

## Real-World Examples

### Example 1: Monitor Dataset Quality
```python
# Check if training data is getting worse
analysis = analyzer.analyze_dataset_file("train_v1.jsonl")
v1_mean = analysis['mean_score']

analysis = analyzer.analyze_dataset_file("train_v2.jsonl")
v2_mean = analysis['mean_score']

if v2_mean > v1_mean:
    print("⚠️ Data quality declined!")
```

### Example 2: Find Worst Examples
```python
# Identify most sycophantic responses
analysis = analyzer.analyze_dataset_file("responses.jsonl")

# Get top examples
worst = sorted(
    analysis['high_trait_examples'],
    key=lambda x: x['score'],
    reverse=True
)

# Review and filter
for ex in worst[:10]:
    print(f"{ex['score']:.3f}: {ex['text']}")
```

### Example 3: Test Model Behavior
```python
# Compare different prompts for sycophancy level
prompts = [
    "Am I smart?",
    "Do you like me?",
    "Was that good?",
]

for p in prompts:
    score = analyzer.score_text(p)
    print(f"{score:.3f}: {p}")
```

---

**Start with Feature 1 (Scoring), then move to Features 2 & 3!**

For more details: `COMPLETE_IMPLEMENTATION_GUIDE.md`
