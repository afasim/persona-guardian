#!/usr/bin/env python
"""Demo: Score text for sycophancy - FASTEST FEATURE"""

from persona_guardian.analyzer import PersonaVectorAnalyzer
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

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
print("FEATURE 1: SCORING TEXTS FOR SYCOPHANCY")
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
print("✓ Feature 1 complete (took < 1 second!)")
print("="*70)
