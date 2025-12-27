@echo off
echo ========================================
echo Starting Frontend Server for Hackathon Book
echo ========================================
echo.

cd /d D:\hackathon-robotic\hackathon-book\frontend

echo Checking Node version...
node --version
echo.

echo Installing/Updating dependencies...
call npm install
echo.

echo Starting Docusaurus development server...
echo.
echo Frontend will be available at:
echo - Site: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

call npm start
