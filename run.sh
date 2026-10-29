#!/usr/bin/env bash
# USAR-AI // Earthquake Tactical Thermal Reconnaissance Launcher
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=========================================================="
echo "🚨 USAR-AI: Autonomous Multi-Sensor Thermal Reconnaissance"
echo "=========================================================="
echo "Checking virtual environment..."

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -U ultralytics streamlit opencv-python-headless pillow pandas
else
    source .venv/bin/activate
fi

echo "Launching Tactical Dashboard on 0.0.0.0:8501..."
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
