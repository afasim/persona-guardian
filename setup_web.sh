#!/bin/bash
# Setup script for persona-guardian web apps on macOS/Linux

echo ""
echo "========================================"
echo "Persona Guardian - Web Setup"
echo "========================================"
echo ""
echo "Installing dependencies..."
echo ""

python -m pip install --upgrade pip

echo "Installing core dependencies..."
python -m pip install torch transformers pyyaml typer accelerate

echo "Installing web framework dependencies..."
python -m pip install fastapi uvicorn gradio

echo ""
echo "========================================"
echo "✓ Setup complete!"
echo "========================================"
echo ""
echo "To run the Gradio UI:"
echo "  python -m web.gradio_app"
echo ""
echo "To run the FastAPI backend:"
echo "  python -m uvicorn web.fastapi_app:app --reload --port 8000"
echo ""
echo "To run the interactive menu:"
echo "  python run_web_apps.py"
echo ""
