@echo off
title Waste Detection System - Complete Setup & Launch
color 0A

:: ============================================
:: WASTE DETECTION SYSTEM - AUTO SETUP & LAUNCH
:: ============================================

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║      ♻️  WASTE DETECTION SYSTEM  ♻️                       ║
echo ║                                                          ║
echo ║         Auto Setup & Launch Script                       ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:: ============================================
:: SET VARIABLES
:: ============================================
set MODEL_URL=https://github.com/YOUR_USERNAME/YOUR_REPO/releases/download/v1.0.0/best_waste_classifier_mobilenet.pth
set MODEL_PATH=backend\models\best_waste_classifier_mobilenet.pth

:: ============================================
:: CHECK BACKEND INSTALLATION
:: ============================================
echo [STEP 1/6] Checking Backend Installation...
echo ----------------------------------------

cd backend

:: Cek apakah virtual environment sudah ada
if exist "venv\Scripts\python.exe" (
    echo [✓] Virtual environment found
    set BACKEND_INSTALLED=1
) else (
    echo [✗] Virtual environment not found
    set BACKEND_INSTALLED=0
)

:: Cek apakah dependencies sudah terinstall
if %BACKEND_INSTALLED%==1 (
    call venv\Scripts\activate.bat > nul 2>&1
    pip show fastapi > nul 2>&1
    if errorlevel 1 (
        echo [✗] Dependencies not installed
        set BACKEND_INSTALLED=0
    ) else (
        echo [✓] Dependencies installed
    )
    call deactivate > nul 2>&1
)

:: ============================================
:: INSTALL BACKEND IF NEEDED
:: ============================================
if %BACKEND_INSTALLED%==0 (
    echo.
    echo [STEP 2/6] Installing Backend...
    echo ----------------------------------------
    
    :: Cek Python
    python --version > nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python not found!
        echo Please install Python 3.9 - 3.11 first
        echo Download from: https://www.python.org/downloads/
        pause
        exit /b 1
    )
    
    echo [✓] Python detected
    
    :: Hapus venv lama jika ada
    if exist "venv" (
        echo [INFO] Removing old virtual environment...
        rmdir /s /q venv
    )
    
    :: Buat virtual environment baru
    echo [1/4] Creating virtual environment...
    python -m venv venv
    
    :: Aktivasi venv
    echo [2/4] Activating virtual environment...
    call venv\Scripts\activate.bat
    
    :: Upgrade pip
    echo [3/4] Upgrading pip...
    python -m pip install --upgrade pip
    
    :: Install dependencies
    echo [4/4] Installing dependencies...
    pip install -r requirements.txt
    
    :: Deactivate venv
    call deactivate
    
    :: Buat folder models jika belum ada
    if not exist "models" mkdir models
    
    echo.
    echo [✓] Backend installation complete!
) else (
    echo.
    echo [STEP 2/6] Backend already installed - SKIPPING
    echo ----------------------------------------
    echo [✓] Backend is ready to use
)

cd ..

:: ============================================
:: CHECK FRONTEND INSTALLATION
:: ============================================
echo.
echo [STEP 3/6] Checking Frontend Installation...
echo ----------------------------------------

cd frontend

:: Cek apakah node_modules sudah ada
if exist "node_modules" (
    echo [✓] Node modules found
    set FRONTEND_INSTALLED=1
) else (
    echo [✗] Node modules not found
    set FRONTEND_INSTALLED=0
)

:: ============================================
:: INSTALL FRONTEND IF NEEDED
:: ============================================
if %FRONTEND_INSTALLED%==0 (
    echo.
    echo [STEP 4/6] Installing Frontend...
    echo ----------------------------------------
    
    :: Cek Node.js
    node --version > nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Node.js not found!
        echo Please install Node.js first
        echo Download from: https://nodejs.org/
        pause
        exit /b 1
    )
    
    echo [✓] Node.js detected
    
    :: Install dependencies
    echo [1/2] Installing npm dependencies...
    call npm install
    
    echo [2/2] Installation complete!
    
    echo.
    echo [✓] Frontend installation complete!
) else (
    echo.
    echo [STEP 4/6] Frontend already installed - SKIPPING
    echo ----------------------------------------
    echo [✓] Frontend is ready to use
)

cd ..

:: ============================================
:: DOWNLOAD MODEL FILE (if missing)
:: ============================================
echo.
echo [STEP 5/6] Checking Model File...
echo ----------------------------------------

if exist "%MODEL_PATH%" (
    echo [✓] Model file found
) else (
    echo [⚠] Model file not found!
    echo.
    echo [INFO] Attempting to download model from GitHub Releases...
    
    :: Buat folder models jika belum ada
    if not exist "backend\models" mkdir backend\models
    
    :: Download menggunakan PowerShell
    powershell -Command "Invoke-WebRequest -Uri '%MODEL_URL%' -OutFile '%MODEL_PATH%'"
    
    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to download model automatically!
        echo.
        echo Please download manually from:
        echo https://github.com/YOUR_USERNAME/YOUR_REPO/releases
        echo.
        echo Then place the file at:
        echo %MODEL_PATH%
        echo.
        pause
    ) else (
        echo [✓] Model downloaded successfully!
    )
)

:: ============================================
:: LAUNCH BACKEND & FRONTEND
:: ============================================
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║              LAUNCHING WASTE DETECTOR                    ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:: Kill existing processes to avoid port conflicts
echo [INFO] Cleaning up existing processes...
taskkill /f /im python.exe /fi "windowtitle eq Waste*" > nul 2>&1
taskkill /f /im node.exe /fi "windowtitle eq Waste*" > nul 2>&1
timeout /t 2 /nobreak > nul

:: Jalankan backend di window terpisah
echo [1/2] Starting Backend Server...
start "Waste Detector Backend" cmd /k "cd backend && echo [BACKEND] Starting server... && call venv\Scripts\activate && python app.py"

:: Tunggu backend siap (5 detik)
echo [INFO] Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

:: Jalankan frontend di window terpisah
echo [2/2] Starting Frontend Server...
start "Waste Detector Frontend" cmd /k "cd frontend && echo [FRONTEND] Starting server... && npm run dev"

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║                   SYSTEM READY!                          ║
echo ║                                                          ║
echo ║  🌐 Backend:  http://localhost:8000                      ║
echo ║  🌐 Frontend: http://localhost:5173                      ║
echo ║                                                          ║
echo ║  📋 API Docs: http://localhost:8000/docs                 ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo Press any key to close this launcher...
pause > nul