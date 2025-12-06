#!/usr/bin/env python
"""
Minimal runner for FastAPI backend and Gradio UI.
Start one of these in separate terminals.
"""

import sys
from pathlib import Path

# Add repo to path so we can import
repo_root = Path(__file__).resolve().parent
sys.path.insert(0, str(repo_root / "src"))
sys.path.insert(0, str(repo_root))

print("\n" + "="*80)
print("PERSONA GUARDIAN - WEB APPS")
print("="*80)
print("\nChoose which app to run:")
print("  1. FastAPI backend     (http://localhost:8000/docs for API docs)")
print("  2. Gradio UI           (http://localhost:7860 for demo)")
print("  3. Both in separate processes")

choice = input("\nEnter choice (1/2/3): ").strip()

if choice == "1":
    print("\n[Starting FastAPI backend on http://0.0.0.0:8000]")
    print("Press Ctrl+C to stop.\n")
    from web.fastapi_app import run
    run(host="0.0.0.0", port=8000)

elif choice == "2":
    print("\n[Starting Gradio UI on http://0.0.0.0:7860]")
    print("Press Ctrl+C to stop.\n")
    from web.gradio_app import build_ui
    demo = build_ui()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)

elif choice == "3":
    import subprocess
    print("\n[Starting both apps in separate processes]")
    print("FastAPI will be on http://0.0.0.0:8000")
    print("Gradio will be on http://0.0.0.0:7860")
    print("Press Ctrl+C to stop both.\n")
    
    import os
    p1 = subprocess.Popen([sys.executable, "-m", "uvicorn", "web.fastapi_app:app", "--reload", "--host", "0.0.0.0", "--port", "8000"], cwd=os.getcwd())
    p2 = subprocess.Popen([sys.executable, "web/gradio_app.py"], cwd=os.getcwd())
    
    try:
        p1.wait()
        p2.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        p1.terminate()
        p2.terminate()
        p1.wait()
        p2.wait()

else:
    print("Invalid choice.")
    sys.exit(1)
