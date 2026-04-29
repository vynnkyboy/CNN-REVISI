@echo off
title Waste Detector - Frontend Installation
color 0E

echo ========================================
echo    FRONTEND INSTALLATION
echo ========================================
echo.

cd frontend

:: Cek Node.js
node --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js tidak ditemukan!
    echo Silakan install Node.js terlebih dahulu
    pause
    exit /b 1
)

echo [✓] Node.js terdeteksi

:: Install dependencies
echo [1/2] Menginstall dependencies...
call npm install

echo [2/2] Selesai!
echo.
echo [✓] Frontend berhasil diinstall!
echo.

cd ..
pause