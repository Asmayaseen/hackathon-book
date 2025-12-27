@echo off
echo ========================================
echo COMPLETE RESTART - Apply All Fixes
echo ========================================
echo.
echo This will:
echo 1. Stop any running servers
echo 2. Clear frontend cache
echo 3. Rebuild frontend with new changes
echo 4. Start both backend and frontend
echo.
echo Press Ctrl+C to cancel, or
pause

echo.
echo [Step 1/5] Killing any running servers...
taskkill /F /IM node.exe 2>nul
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo [Step 2/5] Clearing frontend cache...
cd /d D:\hackathon-robotic\hackathon-book\frontend
if exist .docusaurus rmdir /s /q .docusaurus
if exist build rmdir /s /q build
echo Cache cleared!

echo.
echo [Step 3/5] Starting Backend Server...
cd /d D:\hackathon-robotic\hf-space
start "Backend Server" cmd /k "python -m uvicorn main:app --reload --port 8000"
timeout /t 5 /nobreak >nul

echo.
echo [Step 4/5] Testing backend health...
curl http://localhost:8000/health 2>nul
if errorlevel 1 (
    echo WARNING: Backend might not be ready yet. Give it 5 more seconds...
    timeout /t 5 /nobreak >nul
)

echo.
echo [Step 5/5] Starting Frontend Server...
cd /d D:\hackathon-robotic\hackathon-book\frontend
start "Frontend Server" cmd /k "npm start"

echo.
echo ========================================
echo DONE! Servers are starting...
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo Backend Docs: http://localhost:8000/docs
echo.
echo Wait for frontend to finish building (30-60 seconds)
echo Then open: http://localhost:3000
echo.
echo Press any key to close this window...
pause >nul
