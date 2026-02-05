#!/bin/bash
# Quick Start Script for NanoBio Studio (macOS/Linux)

echo "========================================"
echo "    NanoBio Studio - Quick Start"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "[1/4] Checking Python installation..."
python3 --version

echo
echo "[2/4] Checking virtual environment..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists"
fi

echo
echo "[3/4] Activating virtual environment and installing dependencies..."
source venv/bin/activate

echo "Installing required packages..."
pip install -r requirements.txt --quiet

if [ $? -ne 0 ]; then
    echo
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo
echo "[4/4] Starting NanoBio Studio..."
echo
echo "========================================"
echo " Application starting..."
echo " Browser will open automatically at:"
echo " http://localhost:8501"
echo "========================================"
echo
echo "Press Ctrl+C to stop the server"
echo

streamlit run app.py
