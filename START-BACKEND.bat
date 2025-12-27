@echo off
echo ========================================
echo Starting Backend Server for Hackathon Book
echo ========================================
echo.

cd /d D:\hackathon-robotic\hf-space

echo Checking Python version...
python --version
echo.

echo Installing/Upgrading dependencies...
pip install -r requirements.txt
echo.

echo Starting FastAPI server on http://localhost:8000
echo.
echo Backend will be available at:
echo - API: http://localhost:8000
echo - Docs: http://localhost:8000/docs
echo - Health: http://localhost:8000/health
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
