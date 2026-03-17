# NanoBio Studio Streamlit Startup Script
# This script properly starts the Streamlit app from the correct directory

Write-Host "Activating virtual environment..." -ForegroundColor Green
& .\.venv\Scripts\Activate.ps1

Write-Host "Clearing Streamlit cache..." -ForegroundColor Green
.\.venv\Scripts\python.exe -m streamlit cache clear

Write-Host "Starting Streamlit app..." -ForegroundColor Green
Write-Host "App will be available at: http://localhost:8501" -ForegroundColor Cyan
Write-Host ""

# Navigate to biotech-lab-main and run the app
cd biotech-lab-main
.\.venv\Scripts\python.exe -m streamlit run App.py
