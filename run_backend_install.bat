@echo off
title Waste Detector - Backend Installation
color 0E

echo ========================================
echo    BACKEND INSTALLATION
echo ========================================
echo.

cd backend

:: Cek Python
python --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python tidak ditemukan!
    echo Silakan install Python 3.9 - 3.11 terlebih dahulu
    pause
    exit /b 1
)

echo [✓] Python terdeteksi

:: Buat virtual environment
echo [1/4] Membuat virtual environment...
python -m venv venv

:: Aktivasi venv
echo [2/4] Mengaktifkan virtual environment...
call venv\Scripts\activate.bat

:: Install dependencies
echo [3/4] Menginstall dependencies...
pip install --upgrade pip
pip install -r requirements.txt

:: Buat folder models jika belum ada
if not exist "models" mkdir models

echo [4/4] Selesai!
echo.
echo [✓] Backend berhasil diinstall!
echo.

cd ..
pause