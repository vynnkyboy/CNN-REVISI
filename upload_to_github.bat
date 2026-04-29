@echo off
title Upload to GitHub - Complete Upload
color 0A

echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║           UPLOAD ALL FILES TO GITHUB (No Exception)            ║
echo ║                                                                ║
echo ║              Repository: vynnkyboy/CNN-REVISI                  ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

:: ============================================
:: CEK APAKAH GIT SUDAH TERINSTALL
:: ============================================
echo [STEP 1/8] Checking Git installation...
git --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git not found!
    echo Please install Git first: https://git-scm.com/
    pause
    exit /b 1
)
echo [✓] Git detected
echo.

:: ============================================
:: CEK APAKAH SUDAH ADA .git FOLDER
:: ============================================
echo [STEP 2/8] Checking Git repository...
if exist ".git" (
    echo [✓] Git repository already initialized
) else (
    echo [INFO] Initializing new Git repository...
    git init
    echo [✓] Git repository initialized
)
echo.

:: ============================================
:: HAPUS .gitignore SEMENTARA (AGAR SEMUA FILE TERUPLOAD)
:: ============================================
echo [STEP 3/8] Temporarily removing .gitignore...
if exist ".gitignore" (
    ren .gitignore .gitignore.backup
    echo [✓] .gitignore backed up
) else (
    echo [INFO] No .gitignore found
)
echo.

:: ============================================
:: HAPUS GIT CACHE (AGAR FRESH)
:: ============================================
echo [STEP 4/8] Clearing Git cache...
git rm -r --cached . 2>nul
echo [✓] Git cache cleared
echo.

:: ============================================
:: ADD SEMUA FILE (TANPA EXCEPTION)
:: ============================================
echo [STEP 5/8] Adding ALL files (including models, venv, etc)...
echo ----------------------------------------
echo Adding files...
git add .

echo.
echo [✓] All files added
echo.

:: ============================================
:: CEK FILE YANG AKAN DIUPLOAD
:: ============================================
echo [STEP 6/8] Files ready to commit...
echo ----------------------------------------
git status
echo.

:: ============================================
:: COMMIT DENGAN PESAN
:: ============================================
echo [STEP 7/8] Committing files...
set /p COMMIT_MSG="Enter commit message (default: Complete project with all files): "
if "%COMMIT_MSG%"=="" set COMMIT_MSG=Complete project with all files

git commit -m "%COMMIT_MSG%"
echo [✓] Files committed
echo.

:: ============================================
:: PUSH KE GITHUB
:: ============================================
echo [STEP 8/8] Pushing to GitHub...
echo ----------------------------------------
echo Repository: https://github.com/vynnkyboy/CNN-REVISI.git
echo.

:: Cek apakah remote sudah ada
git remote get-url origin > nul 2>&1
if errorlevel 1 (
    echo [INFO] Adding remote origin...
    git remote add origin https://github.com/vynnkyboy/CNN-REVISI.git
)

:: Push ke branch main atau master
echo [INFO] Pushing to GitHub...
git push -u origin main 2>nul
if errorlevel 1 (
    git push -u origin master 2>nul
    if errorlevel 1 (
        echo.
        echo [ERROR] Push failed!
        echo.
        echo Possible issues:
        echo 1. Authentication required
        echo 2. Branch name is different
        echo.
        echo Try force push with: git push -f origin main
        echo.
    )
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║                    UPLOAD COMPLETE!                            ║
echo ║                                                                ║
echo ║  Repository: https://github.com/vynnkyboy/CNN-REVISI          ║
echo ║                                                                ║
echo ║  ⚠️  NOTE:                                                    ║
echo ║  - All files including models are uploaded                    ║
echo ║  - File size may be large                                     ║
echo ║  - Restore .gitignore with: ren .gitignore.backup .gitignore  ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

pause