@echo off
REM Quick Start Script for NanoBio Studio (Windows)

echo ========================================
echo     NanoBio Studio - Quick Start
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Checking Python installation...
python --version

echo.
echo [2/4] Checking virtual environment...
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists
)

echo.
echo [3/4] Activating virtual environment and installing dependencies...
call venv\Scripts\activate

echo Installing required packages...
pip install -r requirements.txt --quiet

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [4/4] Starting NanoBio Studio...
echo.
echo ========================================
echo  Application starting...
echo  Browser will open automatically at:
echo  http://localhost:8501
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run app.py

pause
