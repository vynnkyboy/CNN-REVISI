@echo off
title Waste Detection System - Launcher
color 0A

echo ========================================
echo    WASTE DETECTION SYSTEM LAUNCHER
echo ========================================
echo.
echo [INFO] Memulai Waste Detection System...
echo.

:: Cek apakah backend sudah terinstall
if not exist "backend\venv" (
    echo [!] Backend belum diinstall. Menjalankan instalasi...
    call run_backend_install.bat
)

:: Cek apakah frontend sudah terinstall
if not exist "frontend\node_modules" (
    echo [!] Frontend belum diinstall. Menjalankan instalasi...
    call run_frontend_install.bat
)

:: Jalankan backend di background
echo [1/2] Menjalankan Backend Server...
start "Waste Detector Backend" cmd /k "cd backend && python app.py"

:: Tunggu 3 detik untuk backend siap
timeout /t 3 /nobreak > nul

:: Jalankan frontend
echo [2/2] Menjalankan Frontend Server...
start "Waste Detector Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo    SYSTEM READY!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press any key to close this window...
pause > nul