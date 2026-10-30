#!/bin/bash
# ==============================================================================
# 🚨 GREEN VALLEY RESIDENCY // RESIDENTIAL EARTHQUAKE USAR COMMAND SYSTEM
# One-Click Offline Desktop Launcher
# ==============================================================================

set -e

# Navigate to project directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "======================================================================"
echo "  🚨 STARTING USAR DISASTER RESPONSE & RESIDENTIAL COMMAND SYSTEM"
echo "  🏢 Sector: Green Valley Residency (Gated High-Rise Society)"
echo "  🛡️ Mode: 100% Offline Edge Mode (Zero Cloud / Zero External API)"
echo "======================================================================"

# Check Python environment
if [ -d "$DIR/.venv" ]; then
    echo "✓ Activating Virtual Environment: .venv"
    source "$DIR/.venv/bin/activate"
    PYTHON_BIN="$DIR/.venv/bin/python"
    STREAMLIT_BIN="$DIR/.venv/bin/streamlit"
else
    echo "⚠️ .venv not found, using system Python3..."
    PYTHON_BIN="python3"
    STREAMLIT_BIN="streamlit"
fi

# Verify core dependencies
echo "✓ Checking neural weights & local SQLite registry..."
if [ ! -f "$DIR/data/society_registry.db" ]; then
    echo "⚡ Initializing Offline SQLite Resident Database..."
    $PYTHON_BIN data/society_registry.py
fi

# Check if port 8501 is already running
PORT=8501
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "✓ USAR Command Server is already running on port $PORT."
    echo "🚀 Launching operator dashboard in browser..."
    open "http://localhost:$PORT"
    exit 0
fi

echo "🚀 Launching USAR Command Console on http://localhost:$PORT ..."
echo "----------------------------------------------------------------------"
echo "  Command Console:   http://localhost:8501"
echo "  Local Network:     http://$(ipconfig getifaddr en0 2>/dev/null || echo 'localhost'):8501"
echo "  Press Ctrl+C to stop the system."
echo "----------------------------------------------------------------------"

# Start Streamlit and open browser
$STREAMLIT_BIN run app.py \
    --server.port $PORT \
    --server.address 0.0.0.0 \
    --server.headless false \
    --browser.gatherUsageStats false
