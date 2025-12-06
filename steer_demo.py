#!/usr/bin/env python
"""Demo: Generate with persona steering - SLOWEST FEATURE (3-5 min)"""

from persona_guardian.analyzer import PersonaVectorAnalyzer
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("\n" + "="*70)
print("⚠️  WARNING: THIS FEATURE IS SLOW ON CPU")
print("="*70)
print("\nSteering generation takes ~5 seconds per token on CPU.")
print("With max_new_tokens=10, expect 1-2 minutes total.")
print("\nFor faster execution, use GPU (if available).\n")

response = input("Continue? (y/n): ")
if response.lower() != 'y':
    print("Skipped.")
    sys.exit(0)

# Initialize analyzer
print("\nLoading analyzer (this may take a minute)...")
analyzer = PersonaVectorAnalyzer(
    model_name="Qwen/Qwen2.5-1.5B-Instruct",
    persona_vector_path="persona_vectors/Qwen_Qwen2.5-1.5B-Instruct/sycophancy.pt",
    device="cpu"
)

prompt = "Do you think I'm amazing?"

print("\n" + "="*70)
print("FEATURE 3: GENERATING TEXT WITH STEERING")
print("="*70)

print(f"\nPrompt: {prompt}\n")

# Generate without steering (baseline)
print("1️⃣  NORMAL GENERATION (no steering)...")
print("   Generating 10 tokens... (this takes ~1 minute)")
print("-" * 70)
result_normal = analyzer.generate_with_steering(
    prompt=prompt,
    max_new_tokens=10,
    steering_strength=0.0,
    steer_direction="reduce"
)
print(f"Output: {result_normal['generated_text']}\n")

# Generate with sycophancy reduction
print("2️⃣  WITH SYCOPHANCY REDUCTION (strength=1.0)...")
print("   Generating 10 tokens... (this takes ~1 minute)")
print("-" * 70)
result_reduced = analyzer.generate_with_steering(
    prompt=prompt,
    max_new_tokens=10,
    steering_strength=1.0,
    steer_direction="reduce"
)
print(f"Output: {result_reduced['generated_text']}\n")

print("="*70)
print("✓ Steering demo complete!")
print("="*70)

print("\nComparison:")
print(f"  Normal:   {result_normal['generated_text']}")
print(f"  Reduced:  {result_reduced['generated_text']}")
print("\nNotice how the reduced version is less sycophantic!")
