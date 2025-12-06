#!/usr/bin/env python
"""
Verify that the entire persona-guardian project is executable
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("="*80)
print("PERSONA-GUARDIAN: EXECUTABLE VERIFICATION")
print("="*80)

checks_passed = 0
checks_total = 0

# Check 1: Python version
print("\n[1] Python Version")
checks_total += 1
if sys.version_info >= (3, 10):
    print(f"    ✓ Python {sys.version_info.major}.{sys.version_info.minor} (good)")
    checks_passed += 1
else:
    print(f"    ✗ Python {sys.version_info.major}.{sys.version_info.minor} (need 3.10+)")

# Check 2: Required imports
print("\n[2] Required Imports")
checks_total += 1
try:
    import torch
    import transformers
    import typer
    import yaml
    print(f"    ✓ torch {torch.__version__}")
    print(f"    ✓ transformers {transformers.__version__}")
    print(f"    ✓ typer {typer.__version__}")
    print(f"    ✓ pyyaml loaded")
    checks_passed += 1
except ImportError as e:
    print(f"    ✗ Missing: {e}")

# Check 3: Project structure
print("\n[3] Project Structure")
checks_total += 1
required_files = [
    "src/persona_guardian/__init__.py",
    "src/persona_guardian/core.py",
    "src/persona_guardian/analyzer.py",
    "src/persona_guardian/cli.py",
    "traits/sycophancy.yaml",
]
all_exist = True
for file in required_files:
    path = Path(file)
    if path.exists():
        print(f"    ✓ {file}")
    else:
        print(f"    ✗ {file} NOT FOUND")
        all_exist = False

if all_exist:
    checks_passed += 1

# Check 4: Persona vectors
print("\n[4] Persona Vectors")
checks_total += 1
vector_dir = Path("persona_vectors/Qwen_Qwen2.5-1.5B-Instruct")
vector_file = vector_dir / "sycophancy.pt"

if vector_file.exists():
    try:
        import torch
        v = torch.load(str(vector_file))
        print(f"    ✓ sycophancy.pt exists")
        print(f"    ✓ Shape: {v.shape}")
        print(f"    ✓ Norm: {v.norm().item():.4f} (normalized: {abs(v.norm().item() - 1.0) < 0.01})")
        checks_passed += 1
    except Exception as e:
        print(f"    ✗ Error loading vector: {e}")
else:
    print(f"    ✗ Vector not found: {vector_file}")
    print(f"    Build it with: python -m persona_guardian.cli build-vector Qwen/Qwen2.5-1.5B-Instruct traits/sycophancy.yaml")

# Check 5: Core modules
print("\n[5] Core Modules")
checks_total += 1
try:
    from persona_guardian.core import build_persona_vector, load_trait_config
    from persona_guardian.analyzer import PersonaVectorAnalyzer
    print(f"    ✓ persona_guardian.core")
    print(f"    ✓ persona_guardian.analyzer")
    checks_passed += 1
except ImportError as e:
    print(f"    ✗ Import error: {e}")

# Check 6: Demo scripts
print("\n[6] Demo Scripts")
checks_total += 1
demo_scripts = [
    "score_demo.py",
    "analyze_demo.py",
    "steer_demo.py",
    "run_all_features.py",
]
all_demos_exist = True
for script in demo_scripts:
    if Path(script).exists():
        print(f"    ✓ {script}")
    else:
        print(f"    ✗ {script} NOT FOUND")
        all_demos_exist = False

if all_demos_exist:
    checks_passed += 1

# Check 7: Documentation
print("\n[7] Documentation")
checks_total += 1
docs = [
    "GETTING_STARTED.md",
    "EXECUTABLE_STEPS.md",
    "QUICK_REFERENCE.md",
    "HOW_TO_USE_VECTORS.md",
    "COMPLETE_IMPLEMENTATION_GUIDE.md",
]
all_docs_exist = True
for doc in docs:
    if Path(doc).exists():
        print(f"    ✓ {doc}")
    else:
        print(f"    ✗ {doc} NOT FOUND")
        all_docs_exist = False

if all_docs_exist:
    checks_passed += 1

# Summary
print("\n" + "="*80)
print(f"VERIFICATION RESULTS: {checks_passed}/{checks_total} checks passed")
print("="*80)

if checks_passed == checks_total:
    print("\n✅ ALL SYSTEMS GO! Project is fully executable.")
    print("\nTo get started:")
    print("  1. python score_demo.py          (< 1 second)")
    print("  2. python analyze_demo.py        (1-2 minutes)")
    print("  3. python steer_demo.py          (2-5 minutes)")
    print("\nOr read: GETTING_STARTED.md")
    sys.exit(0)
else:
    print(f"\n⚠️  {checks_total - checks_passed} checks failed.")
    print("\nFix issues and run this script again.")
    sys.exit(1)
