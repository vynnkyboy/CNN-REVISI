@echo off
title Waste Detector - Full Installation
color 0E

echo ========================================
echo    FULL INSTALLATION
echo ========================================
echo.
echo [INFO] Menginstall semua dependencies...
echo.

:: Install backend
echo [1/2] Menginstall Backend...
call run_backend_install.bat

:: Install frontend
echo [2/2] Menginstall Frontend...
call run_frontend_install.bat

echo.
echo ========================================
echo    INSTALLATION COMPLETE!
echo ========================================
echo.
echo Jalankan run.bat untuk memulai sistem
echo.

pause