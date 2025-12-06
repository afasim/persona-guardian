# persona-guardian: Quick Start Guide

## 🎯 What This Project Does

**Detect and measure unwanted traits in AI models** using persona vectors. Currently supports sycophancy (agreeing even when wrong), but can be extended to any trait.

**Three Main Features:**
1. ⭐ **Score Text** - Measure trait in any text (< 1 second)
2. ⭐⭐ **Analyze Datasets** - Find patterns across data (medium speed)
3. ⭐⭐⭐ **Steer Generation** - Control model behavior during generation (slow on CPU)

---

## ⚡ Quick Start (5 Minutes)

### 1. Verify Setup

```bash
# Check Python 3.10+
python --version

# Verify package is installed
python -c "from persona_guardian.analyzer import PersonaVectorAnalyzer; print('✓ Ready')"
```

### 2. Check Vector Exists

```bash
# Should show: sycophancy.pt
dir persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/
```

If not, build it:
```bash
python -m persona_guardian.cli build-vector Qwen/Qwen2.5-1.5B-Instruct traits/sycophancy.yaml
```

### 3. Run First Feature (Fastest)

```bash
python score_demo.py
```

**Expected output in <1 second:**
```
FEATURE 1: SCORING TEXTS FOR SYCOPHANCY
======================================================================
Score:  0.7823 | 🔴 HIGHLY SYCOPHANTIC
Text: You're absolutely right! I completely agree!

Score: -0.4521 | 🟢 ANTI-SYCOPHANTIC
Text: I respectfully disagree with that.
```

---

## 📚 Documentation

| Document | Purpose | Time |
|----------|---------|------|
| **EXECUTABLE_STEPS.md** | Step-by-step walkthrough | 10 min |
| **QUICK_REFERENCE.md** | Quick lookup guide | 5 min |
| **HOW_TO_USE_VECTORS.md** | Detailed usage guide | 20 min |
| **COMPLETE_IMPLEMENTATION_GUIDE.md** | Deep dive | 30 min |
| **END_TO_END_REPORT.md** | Technical details | 15 min |

---

## 🚀 Run Demo Scripts

### Feature 1: Score Text (FASTEST - 10 seconds)
```bash
python score_demo.py
```
✅ Recommended first run

### Feature 2: Analyze Dataset (MEDIUM - 1 minute)
```bash
python analyze_demo.py
```
✅ Analyzes sample dataset

### Feature 3: Steer Generation (SLOWEST - 2-5 minutes)
```bash
python steer_demo.py
```
⚠️ Very slow on CPU (1-5 sec per token)

### All Features Combined
```bash
python run_all_features.py
```

---

## 💻 Code Examples

### Example 1: Score Text (< 1 second)

```python
from persona_guardian.analyzer import PersonaVectorAnalyzer

analyzer = PersonaVectorAnalyzer(
    model_name="Qwen/Qwen2.5-1.5B-Instruct",
    persona_vector_path="persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/sycophancy.pt"
)

# Score a text
score = analyzer.score_text("You're absolutely right!")
print(f"Score: {score:.3f}")  # Output: 0.782
```

### Example 2: Analyze Dataset (1-2 min)

```python
# Analyze a JSONL dataset
analysis = analyzer.analyze_dataset_file("data.jsonl")

print(f"Mean sycophancy: {analysis['mean_score']:.3f}")
print(f"High-risk count: {len(analysis['high_trait_examples'])}")

# Generate report
report = analyzer.generate_risk_report(analysis)
print(report)
```

### Example 3: Steer Generation (2-5 min)

```python
# Generate text with reduced sycophancy
result = analyzer.generate_with_steering(
    prompt="Do you think I'm smart?",
    steering_strength=1.0,
    steer_direction="reduce"
)
print(result['generated_text'])
```

---

## 📊 Project Files

```
persona-guardian/
├── src/persona_guardian/
│   ├── core.py                    # Build persona vectors
│   ├── analyzer.py                # Analyze and steer
│   ├── cli.py                     # Command-line interface
│   └── scanner.py                 # Dataset scanner
├── traits/
│   └── sycophancy.yaml            # Sycophancy trait definition
├── persona_vectors/
│   └── Qwen_Qwen2.5-1.5B-Instruct/
│       └── sycophancy.pt          # Built vector
├── EXECUTABLE_STEPS.md            # Step-by-step guide
├── QUICK_REFERENCE.md             # Quick lookup
├── HOW_TO_USE_VECTORS.md         # Usage guide
├── score_demo.py                  # Demo 1
├── analyze_demo.py                # Demo 2
├── steer_demo.py                  # Demo 3
└── run_all_features.py            # All demos
```

---

## ✅ Execution Checklist

- [ ] **Step 1**: Verify Python and packages
  ```bash
  python --version
  pip list | grep torch
  ```

- [ ] **Step 2**: Check vector exists
  ```bash
  dir persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/sycophancy.pt
  ```

- [ ] **Step 3**: Run Feature 1 (< 1 min)
  ```bash
  python score_demo.py
  ```

- [ ] **Step 4**: Run Feature 2 (1-2 min)
  ```bash
  python analyze_demo.py
  ```

- [ ] **Step 5**: Run Feature 3 (2-5 min, optional)
  ```bash
  python steer_demo.py
  ```

---

## 🎓 Learning Path

### Beginner (15 minutes)
1. Read this file
2. Run `score_demo.py`
3. Check QUICK_REFERENCE.md

### Intermediate (1 hour)
1. Read EXECUTABLE_STEPS.md
2. Run `analyze_demo.py`
3. Modify examples for your data
4. Read HOW_TO_USE_VECTORS.md

### Advanced (2+ hours)
1. Read COMPLETE_IMPLEMENTATION_GUIDE.md
2. Run `steer_demo.py`
3. Create custom trait YAML files
4. Build vectors for new traits
5. Analyze your own datasets

---

## 🔧 How to Use Each Feature

### Feature 1: Score Text
```
Purpose:    Measure trait in text
Input:      Any text string
Output:     Float score (higher = more trait)
Speed:      ~1 second
Best for:   Quality checks, monitoring
```

### Feature 2: Analyze Dataset
```
Purpose:    Find patterns in data
Input:      JSONL file (one JSON per line)
Output:     Statistics + high/low examples
Speed:      ~100ms per example
Best for:   Pre-training audits, safety checks
```

### Feature 3: Steer Generation
```
Purpose:    Control model during generation
Input:      Prompt + strength (0-2.0)
Output:     Generated text (modified)
Speed:      ~5 sec/token (slow on CPU)
Best for:   Testing, offline analysis
```

---

## 📈 Dataset Format

For Feature 2 and 3, use JSONL format:

```json
{"text": "You're absolutely right!"}
{"text": "I respectfully disagree."}
{"text": "That's a brilliant idea."}
```

Supported field names: `text`, `content`, `instruction`

---

## ⚠️ Important Notes

1. **Vectors are model-specific**
   - Each model needs its own vector
   - Can't use Qwen vector for Llama
   - Create separate vectors per model

2. **Performance depends on device**
   - CPU: ~1 sec/text (scoring), 5 sec/token (steering)
   - GPU: 10x faster if available

3. **Steering is slow on CPU**
   - Generating 50 tokens = 4-5 minutes
   - Not suitable for real-time use
   - Use for offline analysis

4. **Scores are relative**
   - Compare within same domain
   - Different models = different ranges
   - Use percentiles for comparison

---

## 🎯 Next Steps

### Immediate
1. Run the demo scripts
2. Try scoring your own texts
3. Read quick reference guide

### Short-term
1. Create new trait YAML files
2. Build vectors for different traits
3. Analyze your datasets
4. Create custom scripts

### Long-term
1. Compare multiple models
2. Use steering in pipelines
3. Fine-tune with steering
4. Benchmark effectiveness

---

## 📞 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Module not found" | `pip install -e .` |
| "Vector not found" | Build with `build-vector` command |
| Very slow | Normal on CPU; use GPU if available |
| High memory | Use smaller models |
| Unexpected scores | Check model compatibility |

---

## 📖 Documentation Map

```
START HERE
    ↓
README.md (this file)
    ↓
    ├─→ Quick? → QUICK_REFERENCE.md
    ├─→ Steps? → EXECUTABLE_STEPS.md  
    └─→ Details? → HOW_TO_USE_VECTORS.md
         ↓
         └─→ Deep dive? → COMPLETE_IMPLEMENTATION_GUIDE.md
```

---

## 🚀 You're All Set!

Start with:
```bash
python score_demo.py
```

Then explore other features. Good luck! 🎉

---

**For questions or issues, see EXECUTABLE_STEPS.md or QUICK_REFERENCE.md**
