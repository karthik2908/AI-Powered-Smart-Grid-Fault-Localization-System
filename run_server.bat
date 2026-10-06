@echo off
title Tamil Nadu Smart Grid - TANGEDCO 24x7 Control Server
color 0B

echo =========================================================================
echo       TAMIL NADU SMART GRID - AI FAULT LOCALIZATION SYSTEM
echo =========================================================================
echo.
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH! Please install Python 3.10+.
    pause
    exit /b 1
)

echo.
echo Installing / Verifying requirements...
pip install -r requirements.txt

echo.
echo Running database migrations...
python manage.py migrate

echo.
echo Seeding initial grid hierarchy and test assets...
python scripts/seeds/seed_tamilnadu_hierarchy.py
python scripts/seeds/seed_tamilnadu_grid.py

echo.
echo =========================================================================
echo  SERVER STARTING:
echo   - Local Access:      http://127.0.0.1:8000/
echo   - Network Access:    http://0.0.0.0:8000/  (Accessible from other PCs/Phones on Wi-Fi)
echo   - Admin Login PIN:   1234
echo =========================================================================
echo.

python manage.py runserver 0.0.0.0:8000
pause
