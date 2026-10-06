# ⚡ AI-Powered Smart Grid Fault Localization System
### TANGEDCO 24x7 Supervisory Control & Data Acquisition (SCADA) System

---

## 📁 Project Architecture & Directory Structure

```
AI-Powered Smart Grid Fault Localization System/
│
├── 📂 api_keys/                          # Dedicated security token storage
│   ├── mapbox_key.txt                    # Active Mapbox public API access token
│   └── api_key.txt                       # Mirror key token
│
├── 📂 backend/                           # Django REST Framework SCADA Backend
│   ├── 📂 migrations/                    # Database schema migrations
│   ├── 📂 static/                        # Bundled offline assets (Tailwind JS & Leaflet GIS)
│   ├── 📂 templates/                     # Production Single-Page UI
│   │   └── dashboard.html                # Professional SCADA UI (Charcoal & Navy Palettes)
│   ├── models.py                         # 3-Tier Hierarchy: District -> Zone -> Area & IoT nodes
│   ├── serializers.py                    # REST API serializers with recursive Zip-Line logic
│   ├── views.py                          # SCADA API endpoints, role switch & GPS geofencing
│   ├── urls.py                           # API routing
│   ├── settings.py                       # Application configuration & auto-key loading
│   └── wsgi.py                           # Production WSGI gateway
│
├── 📂 ai/                                # AI / Machine Learning Engine
│   └── train_model.py                    # Waveform anomaly classifier (Short Circuit, Cable Cut, Overload)
│
├── 📂 model_weights/                     # Pre-trained Neural Network weights
│
├── 📂 scripts/                           # Structured Automation & Utility Scripts
│   ├── 📂 seeds/                         # Database initialization & geographic grid seeders
│   │   ├── seed_tamilnadu_hierarchy.py   # Populates 6 Districts, 12 Zones, 12 Areas
│   │   ├── seed_tamilnadu_grid.py        # Populates 21 substations, feeders & ESP32 meters
│   │   ├── seed_india_grid.py            # National interstate grid seed
│   │   └── seed_zone_areas.py            # Regional PIN/ZIP sector coordinates
│   └── 📂 tests/                         # Testing & Automation
│       ├── test_api_endpoints.py         # Automated test suite for REST endpoints
│       └── run_project_process.py        # End-to-end pipeline verification
│
├── 📂 hardware/                          # IoT Embedded Firmware & Pinouts
│   ├── circuit_diagram.md                # Hardware pinouts (ZMPT101B, ACS712, ESP32)
│   └── esp32_smart_meter.ino             # Arduino/C++ code for ESP32
│
├── 📂 docs/                              # Project Documentation & Architecture
│   ├── images/                           # High-resolution architectural & UI captures
│   └── FINAL_PROJECT_REPORT.md           # Complete academic & industrial report
│
├── db.sqlite3                            # Embedded self-contained relational database
├── manage.py                             # Django CLI management entrypoint
├── PROJECT_STRUCTURE_LIST.md             # Complete Order-Wise Project Manifest & Directory Catalog
├── requirements.txt                      # Python dependencies list
├── run_server.bat                        # 1-Click launcher for Windows
└── run_server.sh                         # 1-Click launcher for Linux & macOS
```

---

## 📑 Complete Ordered Project Catalog

For an exhaustive, sequential order breakdown of all system files, data pipelines, cascading "Zip-Line" math, and API routes, consult:
👉 **[`PROJECT_STRUCTURE_LIST.md`](file:///c:/Users/Karthikeyen/Downloads/AI-Powered%20Smart%20Grid%20Fault%20Localization%20System/PROJECT_STRUCTURE_LIST.md)**

---

## 🚀 Quick Start Guide

### 1. Launch on Windows (1-Click)
Double-click `run_server.bat`. The script will automatically:
- Verify Python installation
- Install missing packages from `requirements.txt`
- Run database migrations
- Seed initial Tamil Nadu districts, zones, and areas
- Start the server on `http://127.0.0.1:8000/` and `http://0.0.0.0:8000/`

### 2. Launch on macOS / Linux
```bash
chmod +x run_server.sh
./run_server.sh
```

### 3. Role Access
- **Admin Switch PIN:** `1234`
- **Consumer View:** Publicly accessible (Switches locked, read-only monitoring)

