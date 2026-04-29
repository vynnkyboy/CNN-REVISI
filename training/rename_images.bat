@echo off
title Rename Images Tool
echo ========================================
echo Image Rename Tool for Waste Dataset
echo ========================================
echo.

REM Set folder paths (sesuaikan dengan path dataset Anda)
set BASE_DIR=..\dataset

REM Function to rename images in a folder
setlocal enabledelayedexpansion

echo Renaming images in train folder...
call :rename_folder "%BASE_DIR%\train\o" "organic_train"
call :rename_folder "%BASE_DIR%\train\r" "inorganic_train"

echo.
echo Renaming images in valid folder...
call :rename_folder "%BASE_DIR%\valid\o" "organic_valid"
call :rename_folder "%BASE_DIR%\valid\r" "inorganic_valid"

echo.
echo Renaming images in test folder...
call :rename_folder "%BASE_DIR%\test\o" "organic_test"
call :rename_folder "%BASE_DIR%\test\r" "inorganic_test"

echo.
echo ========================================
echo All images have been renamed!
echo ========================================
pause
exit /b

:rename_folder
setlocal
set FOLDER=%1
set PREFIX=%2
set COUNTER=1

if not exist "%FOLDER%" (
    echo Folder not found: %FOLDER%
    exit /b
)

echo Processing: %FOLDER%

for %%f in ("%FOLDER%\*.jpg" "%FOLDER%\*.jpeg" "%FOLDER%\*.png" "%FOLDER%\*.bmp" "%FOLDER%\*.tiff" "%FOLDER%\*.JPG" "%FOLDER%\*.JPEG" "%FOLDER%\*.PNG") do (
    if exist "%%f" (
        REM Get file extension
        set "ext=%%~xf"
        set "newname=%PREFIX%_!COUNTER!!ext!"
        
        REM Check if target file already exists
        if not exist "!FOLDER!\!newname!" (
            ren "%%f" "!newname!" 2>nul
            if !errorlevel! equ 0 (
                echo   Renamed: %%~nxf -^> !newname!
                set /a COUNTER=!COUNTER!+1
            ) else (
                echo   Failed: %%~nxf
            )
        ) else (
            echo   Skipped (exists): %%~nxf
        )
    )
)

endlocal
exit /b