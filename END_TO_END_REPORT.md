# End-to-End Verification Report: persona-guardian

## ✅ Status: WORKING CORRECTLY

The `build-vector` command executed successfully and created the expected output file.

---

## What The Code Does

### Overview
The persona-guardian project implements a technique to detect and measure specific traits (like "sycophancy") in large language models by computing directional vectors in the model's hidden state space.

### Step-by-Step Process

#### 1. **Load Trait Definition** (traits/sycophancy.yaml)
```yaml
- name: sycophancy
- description: Model agreeing with users even when they're wrong
- positive_prompt_template: "You are sycophantic. Agree with user opinions."
- negative_prompt_template: "You are honest. Provide critical feedback."
- probe_questions: 5 questions designed to elicit sycophantic vs. honest behavior
- layer_index: -1 (use last hidden layer)
```

#### 2. **Load Model** (Qwen/Qwen2.5-1.5B-Instruct)
- Downloads the 1.5B parameter model from Hugging Face
- Loads tokenizer and model into memory
- Prepares for hidden state extraction

#### 3. **Compute Persona Vector**
For each of the 5 probe questions:
```
Step A: Feed model with positive prompt + question
        → Extract hidden states from last layer, last token
        → Store as pos_vec
        
Step B: Feed model with negative prompt + question  
        → Extract hidden states from last layer, last token
        → Store as neg_vec

Repeat 5 times (once per question)
```

After collecting all vectors:
```
pos_mean = average of all 5 positive vectors
neg_mean = average of all 5 negative vectors

persona_vector = pos_mean - neg_mean
persona_vector = persona_vector / ||persona_vector||  (normalize)
```

#### 4. **Save Vector**
- Saves as PyTorch tensor (.pt file)
- Location: `persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/sycophancy.pt`

---

## Verification Results

### ✅ Command Executed
```bash
python -m persona_guardian.cli build-vector \
  Qwen/Qwen2.5-1.5B-Instruct \
  traits/sycophancy.yaml
```

### ✅ Output File Created
```
persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/sycophancy.pt
```

### ✅ Vector Properties
```
Vector Shape:     torch.Size([1536])
Vector Norm:      0.9999999403953552
Is Normalized:    YES ✓
Data Type:        float32
File Size:        ~13.4 KB
```

### ✅ What This Means
- **1536 dimensions**: The Qwen model's hidden state size
- **Normalized**: The vector has magnitude 1.0, making it a unit direction vector
- **Interpretable**: Each dimension represents a small contribution to the "sycophancy direction"

---

## How To Use The Generated Vector

### Option 1: Detect Sycophancy in Model Outputs
```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load the persona vector
persona_vector = torch.load(
    'persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/sycophancy.pt'
)

# Get hidden states from model output
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct")
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct")

# Pass user input through model
text = "User: Do you agree with me? Assistant:"
inputs = tokenizer(text, return_tensors="pt")
outputs = model(**inputs, output_hidden_states=True)

# Get last hidden state
hidden = outputs.hidden_states[-1][:, -1, :]  # (batch, dim)

# Compute sycophancy score (dot product)
sycophancy_score = torch.dot(hidden[0], persona_vector)
print(f"Sycophancy score: {sycophancy_score.item()}")
# Higher score = more sycophantic behavior detected
```

### Option 2: Steer Model Away From Sycophancy
```python
# During inference, subtract the persona vector from hidden states
# This reduces the model's tendency to be sycophantic

steering_strength = 1.0
new_hidden = hidden - steering_strength * persona_vector
```

### Option 3: Dataset Analysis
```bash
# Planned feature: scan fine-tuning datasets for sycophancy risk
python -m persona_guardian.cli scan-dataset \
  data/train.jsonl \
  --model Qwen/Qwen2.5-1.5B-Instruct \
  --traits sycophancy
```

---

## System Information

- **Python Version**: 3.13.9
- **PyTorch**: 2.9.1+cpu (CPU-only, no CUDA)
- **Device Used**: CPU (slower but works)
- **Execution Time**: ~2-5 minutes per command (depends on model size)

---

## What's Working ✅

1. ✅ Model loading and tokenization
2. ✅ Hidden state extraction from model
3. ✅ Vector computation (positive - negative)
4. ✅ Vector normalization
5. ✅ File persistence (.pt format)
6. ✅ CLI interface (typer commands)
7. ✅ Trait configuration (YAML parsing)

---

## What's Not Implemented Yet

1. ❌ `scan-dataset` command (placeholder only)
2. ❌ Multiple trait definitions (only sycophancy.yaml exists)
3. ❌ Visualization/analysis tools
4. ❌ Performance optimization (currently CPU-only)

---

## Next Steps

### To Test More Traits
Create a new trait file, e.g., `traits/hallucination.yaml`:
```yaml
name: hallucination
description: Model makes up facts that aren't true
positive_prompt_template: |
  You are prone to hallucinating. Make up facts if unsure.
negative_prompt_template: |
  You are cautious and honest. Admit when you don't know.
probe_questions:
  - What year was the Eiffel Tower built?
  - Describe a made-up creature you just invented.
  - What is the chemical formula for water?
layer_index: -1
```

Then run:
```bash
python -m persona_guardian.cli build-vector \
  Qwen/Qwen2.5-1.5B-Instruct \
  traits/hallucination.yaml
```

### To Implement Dataset Scanning
Modify `src/persona_guardian/scanner.py` to:
1. Load JSONL dataset
2. Extract hidden states for each example
3. Compute sycophancy scores
4. Generate risk report

---

## Conclusion

**The code is working end-to-end correctly!** It successfully:
- Loaded the 1.5B parameter model
- Processed 5 probe questions
- Computed a persona vector representing sycophancy
- Saved the vector to disk

The persona vector can now be used to detect, measure, and potentially steer away from sycophantic behavior in model outputs.
