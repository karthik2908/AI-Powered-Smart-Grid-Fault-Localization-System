@echo off
title Push Tamil Nadu Smart Grid to GitHub
color 0A

echo =========================================================================
echo       PUSHING FULL SMART GRID PROJECT TO GITHUB REPOSITORY
echo =========================================================================
echo.
echo Target Repository:
echo   https://github.com/karthik2908/AI-Powered-Smart-Grid-Fault-Localization-System.git
echo.
echo Staging and verifying commit...
git add .
git commit -m "Complete AI-Powered Smart Grid Fault Localization System release" >nul 2>&1

echo.
echo Pushing to GitHub (origin/main)...
echo (A browser sign-in window will open if this is your first time)
echo.

git push -u origin main --force

echo.
if %errorlevel% equ 0 (
    echo =========================================================================
    echo [SUCCESS] PROJECT SUCCESSFULLY PUSHED TO GITHUB!
    echo Visit: https://github.com/karthik2908/AI-Powered-Smart-Grid-Fault-Localization-System
    echo =========================================================================
) else (
    echo [ERROR] Push encountered an issue. Please verify your GitHub login in the browser.
)

pause
