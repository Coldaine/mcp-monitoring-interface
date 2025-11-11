#!/bin/bash
# MCP Monitoring Interface - Unix/Mac Startup Script

echo "============================================================"
echo "MCP Monitoring Interface"
echo "============================================================"
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "[INFO] Activating virtual environment..."
    source venv/bin/activate
else
    echo "[WARNING] No virtual environment found. Using global Python."
fi

echo ""
echo "[INFO] Running component tests..."
python test_app.py
if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Component tests failed. Please check the output above."
    exit 1
fi

echo ""
echo "============================================================"
echo "Starting Gradio Interface..."
echo "============================================================"
echo ""
echo "The dashboard will be available at: http://localhost:7860"
echo ""
echo "Press Ctrl+C to stop the server."
echo ""

python gradio_app.py
