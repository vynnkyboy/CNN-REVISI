@echo off
title Waste Detector - Local Run
color 0A

echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                     WASTE DETECTION SYSTEM                         ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

:: Kill existing processes
taskkill /f /im python.exe /fi "windowtitle eq *Backend*" > nul 2>&1
taskkill /f /im node.exe /fi "windowtitle eq *Frontend*" > nul 2>&1

:: Start backend
echo [1/2] Starting Backend Server...
start "Waste Detector - Backend" cmd /k "cd backend && call venv\Scripts\activate && python app.py"

:: Wait
timeout /t 5 /nobreak > nul

:: Start frontend
echo [2/2] Starting Frontend Server...
start "Waste Detector - Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ✅ System running!
echo 🌐 Backend:  http://localhost:8000
echo 🌐 Frontend: http://localhost:5173
echo.
echo Close this window to stop, or keep it open.
echo.
pause > nul