@echo off
echo ========================================
echo Checking if fixes were applied...
echo ========================================
echo.

cd /d D:\hackathon-robotic\hackathon-book\frontend

echo [1/4] Checking signin.tsx...
findstr /C:"localhost:8000" src\pages\signin.tsx >nul
if %errorlevel%==0 (
    echo [OK] signin.tsx - Fixed!
) else (
    echo [FAIL] signin.tsx - Still has old IP!
)

echo.
echo [2/4] Checking chatbot.tsx...
findstr /C:"localhost:8000" src\pages\chatbot.tsx >nul
if %errorlevel%==0 (
    echo [OK] chatbot.tsx - Fixed!
) else (
    echo [FAIL] chatbot.tsx - Still has old IP!
)

echo.
echo [3/4] Checking chatService.ts...
findstr /C:"localhost:8000" src\services\chatService.ts >nul
if %errorlevel%==0 (
    echo [OK] chatService.ts - Fixed!
) else (
    echo [FAIL] chatService.ts - Still has old IP!
)

echo.
echo [4/4] Checking for old IP anywhere...
findstr /S /C:"172.24.5.28" src\* >nul
if %errorlevel%==0 (
    echo [FAIL] Found old IP in files! Changes not applied!
    echo.
    echo Files still containing 172.24.5.28:
    findstr /S /C:"172.24.5.28" src\*
) else (
    echo [OK] No old IPs found! All fixes applied!
)

echo.
echo ========================================
echo.
echo Now check if servers are running:
echo.

echo Testing Backend...
curl http://localhost:8000/health 2>nul
if %errorlevel%==0 (
    echo [OK] Backend is running!
) else (
    echo [FAIL] Backend is NOT running!
    echo Run: START-BACKEND.bat
)

echo.
echo Testing Frontend...
curl http://localhost:3000 2>nul
if %errorlevel%==0 (
    echo [OK] Frontend is running!
) else (
    echo [FAIL] Frontend is NOT running!
    echo Run: START-FRONTEND.bat
)

echo.
echo ========================================
echo Check complete!
echo.
pause
