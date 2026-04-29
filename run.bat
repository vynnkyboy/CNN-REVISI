@echo off
title Waste Detector - First Time Setup
color 0A

echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                                                                    ║
echo ║           ♻️  WASTE DETECTION SYSTEM  ♻️                           ║
echo ║                                                                    ║
echo ║              First Time Setup - Auto Install                       ║
echo ║                                                                    ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
echo [INFO] This script will automatically:
echo        1. Remove old venv (if exists)
echo        2. Create new Python virtual environment
echo        3. Install all backend dependencies
echo        4. Install all frontend dependencies
echo        5. Download model file (if needed)
echo        6. Start the application
echo.

set /p CONFIRM="Press ENTER to start or 'q' to quit: "
if /i "%CONFIRM%"=="q" exit /b

:: ============================================
:: STEP 1: CLEAN UP OLD FILES
:: ============================================
echo.
echo [STEP 1/6] Cleaning up old virtual environments...
echo ----------------------------------------

if exist "backend\venv" (
    echo [INFO] Removing old backend venv...
    rmdir /s /q backend\venv
)

if exist "frontend\node_modules" (
    echo [INFO] Removing old node_modules...
    rmdir /s /q frontend\node_modules
)

echo [✓] Cleanup complete

:: ============================================
:: STEP 2: INSTALL BACKEND
:: ============================================
echo.
echo [STEP 2/6] Installing Backend...
echo ----------------------------------------

cd backend

:: Check Python
python --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo.
    echo Please install Python 3.9 - 3.11
    echo Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: Create new venv
echo [1/3] Creating virtual environment...
python -m venv venv

:: Activate and install
echo [2/3] Installing dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
call deactivate

echo [3/3] Backend ready!
cd ..

:: ============================================
:: STEP 3: INSTALL FRONTEND
:: ============================================
echo.
echo [STEP 3/6] Installing Frontend...
echo ----------------------------------------

cd frontend

:: Check Node.js
node --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found!
    echo.
    echo Please install Node.js
    echo Download: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

:: Install dependencies
echo [1/2] Installing npm packages...
call npm install

echo [2/2] Frontend ready!
cd ..

:: ============================================
:: STEP 4: CHECK MODEL FILE
:: ============================================
echo.
echo [STEP 4/6] Checking Model File...
echo ----------------------------------------

if exist "backend\models\best_waste_classifier_mobilenet.pth" (
    echo [✓] Model file found!
) else (
    echo [⚠] Model file not found!
    echo.
    echo Model file will be downloaded automatically...
    
    :: Make sure models folder exists
    if not exist "backend\models" mkdir backend\models
    
    :: Try to download from your GitHub release
    echo [INFO] Downloading from GitHub...
    powershell -Command "& {
        $url = 'https://github.com/vynnkyboy/CNN-REVISI/releases/download/v1.0.0/best_waste_classifier_mobilenet.pth'
        $output = 'backend\models\best_waste_classifier_mobilenet.pth'
        try {
            Write-Host 'Downloading model... (this may take a few minutes)'
            Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing
            if (Test-Path $output) {
                Write-Host '[✓] Model downloaded successfully!'
            }
        } catch {
            Write-Host '[✗] Auto-download failed'
        }
    }"
    
    if not exist "backend\models\best_waste_classifier_mobilenet.pth" (
        echo.
        echo ⚠️  Manual download required:
        echo.
        echo 1. Go to: https://github.com/vynnkyboy/CNN-REVISI/releases
        echo 2. Download: best_waste_classifier_mobilenet.pth
        echo 3. Place in: backend\models\
        echo.
        pause
    )
)

:: ============================================
:: STEP 5: CREATE RUN SCRIPT FOR USER
:: ============================================
echo.
echo [STEP 5/6] Creating launch script...
echo ----------------------------------------

:: Create run_local.bat for future use
(
echo @echo off
echo title Waste Detector - Local Run
echo color 0A
echo.
echo echo Starting Waste Detection System...
echo echo.
echo cd backend
echo start "Backend Server" cmd /k "call venv\Scripts\activate ^&^& python app.py"
echo cd ..
echo.
echo timeout /t 3 /nobreak > nul
echo.
echo cd frontend
echo start "Frontend Server" cmd /k "npm run dev"
echo cd ..
echo.
echo echo.
echo echo Backend:  http://localhost:8000
echo echo Frontend: http://localhost:5173
echo echo.
echo echo Press any key to close...
echo pause ^> nul
) > run_local.bat

echo [✓] Created run_local.bat for future use

:: ============================================
:: STEP 6: START APPLICATION
:: ============================================
echo.
echo [STEP 6/6] Starting Waste Detection System...
echo ----------------------------------------

:: Kill existing processes
taskkill /f /im python.exe /fi "windowtitle eq *Backend*" > nul 2>&1
taskkill /f /im node.exe /fi "windowtitle eq *Frontend*" > nul 2>&1
timeout /t 2 /nobreak > nul

:: Start backend
start "Waste Detector - Backend" cmd /k "cd backend && call venv\Scripts\activate && python app.py"

:: Wait for backend
timeout /t 5 /nobreak > nul

:: Start frontend
start "Waste Detector - Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                                                                    ║
echo ║                    ✅ SETUP COMPLETE! ✅                           ║
echo ║                                                                    ║
echo ║  🌐 Backend:  http://localhost:8000                               ║
echo ║  🌐 Frontend: http://localhost:5173                               ║
echo ║                                                                    ║
echo ║  📝 For future use, simply run: run_local.bat                     ║
echo ║                                                                    ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
echo Press any key to close this window (servers keep running)...
pause > nul