#!/usr/bin/env bash
# Tamil Nadu Smart Grid - Launch script for Linux / macOS

set -e

echo "========================================================================="
echo "      TAMIL NADU SMART GRID - AI FAULT LOCALIZATION SYSTEM"
echo "========================================================================="
echo ""

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in PATH!"
    exit 1
fi

echo "Installing / Verifying dependencies..."
pip3 install -r requirements.txt || pip install -r requirements.txt

echo "Running migrations..."
python3 manage.py migrate

echo "Seeding Tamil Nadu 3-Tier Hierarchy..."
python3 scripts/seeds/seed_tamilnadu_hierarchy.py || python scripts/seeds/seed_tamilnadu_hierarchy.py
python3 scripts/seeds/seed_tamilnadu_grid.py || python scripts/seeds/seed_tamilnadu_grid.py


echo ""
echo "========================================================================="
echo " SERVER STARTING:"
echo "  - Local Access:      http://127.0.0.1:8000/"
echo "  - LAN / Wi-Fi:       http://0.0.0.0:8000/ (Accessible from other devices)"
echo "  - Admin Login PIN:   1234"
echo "========================================================================="
echo ""

python3 manage.py runserver 0.0.0.0:8000
