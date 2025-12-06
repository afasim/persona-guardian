#!/usr/bin/env python
"""
End-to-end verification script for persona-guardian.

This script explains what the code should do and verifies each step.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 80)
print("PERSONA-GUARDIAN END-TO-END VERIFICATION")
print("=" * 80)

print("""
WHAT THE CODE SHOULD DO:
========================

1. Load Trait Configuration (sycophancy.yaml)
   - Define what "sycophancy" means (agreeing even when wrong)
   - Positive template: Instructions to be sycophantic
   - Negative template: Instructions to be honest/critical
   - Probe questions: Questions to test the trait

2. Load the Model (Qwen/Qwen2.5-1.5B-Instruct)
   - Download and load the LLM from HuggingFace
   - Prepare tokenizer for encoding text

3. Build Persona Vector
   - For EACH probe question:
     * Feed model with positive prompt + question → capture hidden states
     * Feed model with negative prompt + question → capture hidden states
   - Average all positive hidden states → pos_mean
   - Average all negative hidden states → neg_mean
   - Compute: persona_vector = pos_mean - neg_mean
   - Normalize the vector
   
4. Save the Vector
   - Save as .pt (PyTorch tensor) file
   - Location: persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/sycophancy.pt

RESULT: A single vector file representing the "sycophancy direction" in the model's
hidden state space. Later, this can be used to:
- Detect if model outputs are sycophantic (by projecting onto this vector)
- Steer model behavior away from sycophancy (by subtracting the vector)

""")

print("=" * 80)
print("VERIFICATION STEPS")
print("=" * 80)

# Step 1: Verify trait config
print("\n✓ Step 1: Load and verify sycophancy.yaml")
try:
    from persona_guardian.core import load_trait_config
    cfg = load_trait_config("traits/sycophancy.yaml")
    print(f"  ✓ Trait name: {cfg.name}")
    print(f"  ✓ Number of probe questions: {len(cfg.probe_questions)}")
    print(f"  ✓ Using layer index: {cfg.layer_index}")
    print(f"  ✓ Probe questions:")
    for i, q in enumerate(cfg.probe_questions, 1):
        print(f"      {i}. {q}")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    sys.exit(1)

# Step 2: Check model availability
print("\n✓ Step 2: Verify model can be loaded")
try:
    import torch
    from transformers import AutoTokenizer
    print(f"  ✓ PyTorch available: {torch.__version__}")
    print(f"  ✓ CUDA available: {torch.cuda.is_available()}")
    
    # Just test tokenizer loading (model loading takes time)
    print(f"  ℹ Loading tokenizer for Qwen/Qwen2.5-1.5B-Instruct...")
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct")
    print(f"  ✓ Tokenizer loaded successfully")
    print(f"  ✓ Vocabulary size: {len(tokenizer)}")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    sys.exit(1)

# Step 3: Verify output directory structure
print("\n✓ Step 3: Verify output directory structure")
try:
    output_dir = Path("persona_vectors/Qwen_Qwen2.5-1.5B-Instruct")
    expected_file = output_dir / "sycophancy.pt"
    
    if output_dir.exists():
        print(f"  ✓ Output directory exists: {output_dir}")
        if expected_file.exists():
            print(f"  ✓ Vector file exists: {expected_file}")
            file_size = expected_file.stat().st_size
            print(f"  ✓ File size: {file_size:,} bytes")
            
            # Try to load and inspect
            try:
                vector = torch.load(expected_file)
                print(f"  ✓ Vector shape: {vector.shape}")
                print(f"  ✓ Vector norm: {vector.norm().item():.4f}")
                print(f"  ✓ Vector is normalized: {abs(vector.norm().item() - 1.0) < 0.01}")
            except Exception as e:
                print(f"  ✗ Could not load vector: {e}")
        else:
            print(f"  ℹ Vector file not yet created. Run this command to create it:")
            print(f"     python -m persona_guardian.cli build-vector \\")
            print(f"       Qwen/Qwen2.5-1.5B-Instruct \\")
            print(f"       traits/sycophancy.yaml")
    else:
        print(f"  ℹ Output directory not yet created")
        print(f"  ℹ Run the build-vector command to create it")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    sys.exit(1)

# Step 4: Check intermediate files
print("\n✓ Step 4: Check what's in persona_vectors/")
try:
    pv_dir = Path("persona_vectors")
    if pv_dir.exists():
        print(f"  Contents:")
        for item in pv_dir.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(pv_dir)
                size = item.stat().st_size
                print(f"    - {rel_path} ({size:,} bytes)")
    else:
        print(f"  ℹ persona_vectors directory does not exist yet")
except Exception as e:
    print(f"  ✗ FAILED: {e}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print("""
TO VERIFY THE CODE IS WORKING END-TO-END:
==========================================

Run this command and wait for completion:
  python -m persona_guardian.cli build-vector \\
    Qwen/Qwen2.5-1.5B-Instruct \\
    traits/sycophancy.yaml

Expected output:
  - Loading model: Qwen/Qwen2.5-1.5B-Instruct
  - Loading model: Qwen/Qwen2.5-1.5B-Instruct (HF cache)
  - Computing persona vectors for trait: sycophancy
  - Processing question 1/5
  - Processing question 2/5
  - Processing question 3/5
  - Processing question 4/5
  - Processing question 5/5
  - Persona vector computed. Shape: torch.Size([hidden_dim])
  - ✓ Successfully saved persona vector to: persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/sycophancy.pt

VERIFICATION:
- Check that a .pt file was created in persona_vectors/
- The file should be ~MB (depends on model hidden size)
- Use torch.load() to verify it's a valid tensor

NEXT STEPS:
- Run the scan-dataset command to use the vector
- Create additional trait definitions (hallucination, privacy, etc.)
""")

print("=" * 80)
