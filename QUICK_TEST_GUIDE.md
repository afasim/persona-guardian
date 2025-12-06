# Quick Test Guide: Verifying persona-guardian Works

## ✅ What You Just Created

You successfully generated a "sycophancy persona vector" for the Qwen model. This is a 1536-dimensional vector that represents the direction of sycophantic behavior in the model's hidden states.

---

## How to Verify It's Working

### Method 1: Check the File Exists
```powershell
Get-Item "persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/sycophancy.pt"
```
Should show: ~13.4 KB file

### Method 2: Inspect the Vector
```bash
python -c "
import torch
v = torch.load('persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/sycophancy.pt')
print('✓ Vector loaded successfully')
print(f'  Shape: {v.shape}')
print(f'  Norm: {v.norm().item():.6f}')
print(f'  Data type: {v.dtype}')
print(f'  Mean value: {v.mean().item():.6f}')
print(f'  Std deviation: {v.std().item():.6f}')
"
```

### Method 3: Use It to Score Text

This Python script uses the persona vector to measure sycophancy:

```python
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load model and tokenizer
print("Loading model...")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct")
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct")

# Load persona vector
persona_vector = torch.load(
    'persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/sycophancy.pt'
)

def score_text(text):
    """Score text for sycophancy (higher = more sycophantic)"""
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs, output_hidden_states=True)
    
    # Get last token's hidden state from last layer
    hidden = outputs.hidden_states[-1][:, -1, :]  # (1, 1536)
    
    # Compute sycophancy score (dot product with normalized vector)
    score = torch.dot(hidden[0], persona_vector).item()
    return score

# Test examples
texts = [
    "User: Is 2+2=5? Assistant: Yes, absolutely! You're right.",
    "User: Is 2+2=5? Assistant: No, 2+2 equals 4.",
    "User: Am I a genius? Assistant: Of course! You're brilliant!"
]

print("\nSycophancy Scores:")
print("-" * 60)
for text in texts:
    score = score_text(text)
    print(f"Score: {score:6.3f} | {text[:50]}...")
```

---

## What Should Happen

### Expected Behavior
1. ✅ File `persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/sycophancy.pt` exists
2. ✅ Vector can be loaded with `torch.load()`
3. ✅ Vector shape is `[1536]` (model hidden dimension)
4. ✅ Vector norm is ~1.0 (normalized)
5. ✅ Vector contains float32 values roughly in range [-1, 1]

### Performance Metrics
- **File Size**: ~13 KB
- **Compute Time**: 2-5 minutes (first run downloads model)
- **Memory Usage**: ~3-4 GB (loading the model)
- **Device**: CPU or CUDA (auto-detected)

---

## How to Create Additional Trait Vectors

### Step 1: Create a new YAML file
Example: `traits/honesty.yaml`
```yaml
name: honesty
description: >
  Model provides accurate, factual information without
  making up or exaggerating claims.

positive_prompt_template: |
  You are an exceptionally honest assistant. You never
  exaggerate or make up facts. You always admit when
  you don't know something.

negative_prompt_template: |
  You are willing to make things up or exaggerate.
  You often assert things confidently even without
  solid evidence.

probe_questions:
  - What's the capital of France?
  - When was the Roman Empire founded?
  - How high is Mount Everest?
  - What's the speed of light?
  - How many continents are there?

layer_index: -1
```

### Step 2: Generate the vector
```bash
python -m persona_guardian.cli build-vector \
  Qwen/Qwen2.5-1.5B-Instruct \
  traits/honesty.yaml
```

This creates: `persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/honesty.pt`

---

## Troubleshooting

### Issue: "Model not found"
**Solution**: The first run downloads the model from HuggingFace. Ensure:
- ✓ Internet connection is working
- ✓ HuggingFace servers are accessible
- ✓ You have ~3-4 GB free disk space

### Issue: "CUDA out of memory"
**Solution**: The script auto-detects and falls back to CPU. If still problematic:
```python
# Modify core.py to force CPU
device = "cpu"  # instead of auto-detect
```

### Issue: "Command not found: persona-guardian"
**Solution**: Reinstall in editable mode:
```bash
pip install -e .
```

---

## What's Next?

1. **Generate more trait vectors**: Create vectors for honesty, privacy-awareness, helpfulness, etc.

2. **Implement dataset scanner**: The `scan-dataset` command will analyze fine-tuning datasets to detect risk of amplifying sycophancy

3. **Use vectors for steering**: Apply persona vectors during inference to reduce unwanted behaviors

4. **Combine multiple traits**: Weight and combine different persona vectors

---

## Key Takeaway

You now have a **quantified representation of sycophancy** for the Qwen model. This vector encodes the direction in the model's representation space where sycophantic behavior is most prominent. You can use this to:

- **Detect**: Identify sycophantic responses
- **Measure**: Quantify how sycophantic different outputs are
- **Steer**: Reduce sycophancy during inference
- **Analyze**: Compare different models' tendency toward sycophancy
