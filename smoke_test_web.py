#!/usr/bin/env python
"""Quick smoke test for web modules."""

import sys
import subprocess

def test_imports():
    """Test if all web modules can be imported."""
    print("=" * 80)
    print("SMOKE TEST: Web Modules")
    print("=" * 80)
    
    # Test 1: web._utils
    try:
        from web._utils import get_analyzer, default_persona_vector_path
        print("✓ web._utils imported")
        pv = default_persona_vector_path()
        print(f"✓ default persona vector found: {pv}")
    except Exception as e:
        print(f"✗ web._utils import failed: {e}")
        return False
    
    # Test 2: FastAPI app syntax
    try:
        from web.fastapi_app import app
        print("✓ web.fastapi_app imported (FastAPI app created)")
    except Exception as e:
        print(f"✗ web.fastapi_app import failed: {e}")
        return False
    
    # Test 3: Gradio app
    try:
        from web.gradio_app import build_ui
        print("✓ web.gradio_app imported")
    except Exception as e:
        print(f"✗ web.gradio_app import failed: {e}")
        return False
    
    print("\n" + "=" * 80)
    print("✓ ALL SMOKE TESTS PASSED")
    print("=" * 80)
    print("\nNext steps:")
    print("1. FastAPI backend: python -m uvicorn web.fastapi_app:app --reload --port 8000")
    print("2. Gradio UI:       python -m web.gradio_app")
    print("3. Or run both in Python: web.fastapi_app.run() or web.gradio_app.build_ui().launch()")
    return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
