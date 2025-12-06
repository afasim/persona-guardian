#!/usr/bin/env python
"""Simple test runner to verify the project works."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 60)
print("Testing persona-guardian project")
print("=" * 60)

# Test 1: Import core module
print("\n✓ Test 1: Import core module...")
try:
    from persona_guardian.core import TraitConfig, load_trait_config
    print("  SUCCESS: Core module imported")
except Exception as e:
    print(f"  FAILED: {e}")
    sys.exit(1)

# Test 2: Import CLI module
print("\n✓ Test 2: Import CLI module...")
try:
    from persona_guardian import cli
    print("  SUCCESS: CLI module imported")
except Exception as e:
    print(f"  FAILED: {e}")
    sys.exit(1)

# Test 3: Create TraitConfig
print("\n✓ Test 3: Create TraitConfig...")
try:
    cfg = TraitConfig(
        name="test",
        description="test description",
        positive_prompt_template="pos",
        negative_prompt_template="neg",
        probe_questions=["q1", "q2"],
    )
    print(f"  SUCCESS: TraitConfig created with name={cfg.name}")
except Exception as e:
    print(f"  FAILED: {e}")
    sys.exit(1)

# Test 4: Load sycophancy config
print("\n✓ Test 4: Load sycophancy.yaml...")
try:
    cfg = load_trait_config("traits/sycophancy.yaml")
    print(f"  SUCCESS: Loaded trait '{cfg.name}' with {len(cfg.probe_questions)} questions")
except Exception as e:
    print(f"  FAILED: {e}")
    sys.exit(1)

# Test 5: Import scanner module
print("\n✓ Test 5: Import scanner module...")
try:
    from persona_guardian import scanner
    print("  SUCCESS: Scanner module imported")
except Exception as e:
    print(f"  FAILED: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All tests passed! Project is in working state.")
print("=" * 60)
print("\nYou can now use:")
print("  - persona-guardian build-vector <model> <trait_config>")
print("  - persona-guardian scan-dataset <dataset> --model <m> --traits <t>")
