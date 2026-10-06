# ⚡ TANGEDCO AI Smart Grid: Structured Project Manifest & Order List

> **System Designation:** AI-Powered Smart Grid Fault Localization & Cascading Outage Management System  
> **Regional Deployment:** Tamil Nadu Electricity Distribution Hierarchy (District → Zone → Area/PIN → ESP32 Meter)  
> **Architecture Standard:** Edge IoT + Deep Learning + Django SCADA REST Framework + Mapbox/Leaflet GIS  

---

## 📑 Table of Contents (Ordered Index)

1. [Order 1: File & Directory Catalog (Structured Repository Tree)](#order-1-file--directory-catalog)
2. [Order 2: 5-Tier Electrical & Administrative Grid Hierarchy](#order-2-5-tier-electrical--administrative-grid-hierarchy)
3. [Order 3: Real-Time Execution Lifecycle (Data Flow Order)](#order-3-real-time-execution-lifecycle)
4. [Order 4: Step-by-Step Command Execution & Launch Sequence](#order-4-step-by-step-command-execution--launch-sequence)
5. [Order 5: REST API Endpoints in Execution Order](#order-5-rest-api-endpoints-in-execution-order)
6. [Order 6: Role-Based Access Control & Security Matrix](#order-6-role-based-access-control--security-matrix)
7. [Order 7: AI Model & Waveform Classification Catalog](#order-7-ai-model--waveform-classification-catalog)

---

## 🗂️ Order 1: File & Directory Catalog

An organized breakdown of every file and folder in the project root:

```
AI-Powered Smart Grid Fault Localization System/
│
├── 📁 ai/                                        # [TIER 1] AI/ML Training & Anomaly Detection
│   └── train_model.py                            # Waveform classifier training script (Keras / TensorFlow)
│
├── 📁 api_keys/                                  # [SECURITY] Token Isolation
│   ├── mapbox_key.txt                            # Verified Mapbox Public Access Token (Auto-loaded)
│   └── api_key.txt                               # Mirror token backup
│
├── 📁 backend/                                   # [TIER 2] Core SCADA Engine & Web Application
│   ├── migrations/                               # Database schema migration files
│   │   ├── 0001_initial.py                       # Initial user profiles, nodes, telemetries, fault logs
│   │   ├── 0002_gridnode_area_fields.py          # ESP32 meter attributes, kWh units, outage causes
│   │   ├── 0003_gridnotification_zones.py       # Notification models & maintenance tracker
│   │   └── 0004_district_electricityzone_area.py # Tamil Nadu 3-tier hierarchy & cascading switch state
│   ├── static/                                   # Offline Static Assets (100% Zero-Internet Operation)
│   │   ├── js/tailwind.js                        # Bundled Tailwind CSS offline compiler
│   │   └── leaflet/                              # Bundled Leaflet GIS CSS, JS & vector marker icons
│   ├── templates/                                # UI Presentation Layer
│   │   └── dashboard.html                        # Real-time SCADA dashboard (Charcoal & Navy palettes)
│   ├── models.py                                 # Database schemas & recursive Zip-Line cascading logic
│   ├── serializers.py                            # DRF serializers with hierarchical serialization
│   ├── views.py                                  # REST controllers, GPS matching, OTP, remote cut switches
│   ├── urls.py                                   # Master API routing table
│   ├── settings.py                               # Django settings (CORS, dynamic paths, auto-mapbox loader)
│   └── wsgi.py                                   # Production WSGI gateway
│
├── 📁 docs/                                      # [DOCUMENTATION] Schematics & Photographic Assets
│   └── images/                                   # High-resolution architectural diagrams & UI captures
│       ├── india_smart_grid_map.jpg              # National high-voltage grid map
│       ├── tamilnadu_smart_grid.jpg              # Tamil Nadu state distribution topology
│       ├── smart_grid_dashboard.jpg              # SCADA UI console overview
│       ├── smart_grid_login.jpg                  # 2FA Login interface
│       ├── smart_grid_otp.jpg                    # SMS OTP authorization modal
│       └── smart_grid_satellite_view.jpg         # High-resolution satellite grid overlay
│
├── 📁 frontend/                                  # [OPTIONAL FRONTEND] React Alternate Component
│   └── src/
│       ├── App.js                                # React entry point
│       └── components/
│           └── GridMap.js                        # React Leaflet map component
│
├── 📁 hardware/                                  # [TIER 0] Edge IoT Firmware & Circuit Specs
│   ├── circuit_diagram.md                        # Pinout specifications (ZMPT101B, ACS712, Relay, ESP32)
│   └── esp32_smart_meter.ino                     # C++ Arduino firmware for edge meter boxes
│
├── 📁 model_weights/                             # [AI ASSETS] Serialized Models & Scalers
│   ├── fault_classifier.keras                   # Pretrained deep learning fault diagnosis network
│   └── scaler_stats.pkl                          # Min-Max statistical scaler for voltage & current normalization
│
├── 📁 scripts/                                   # [OPERATIONS] Automated Grid Operations & Tests
│   ├── seeds/                                    # Database Seeding Scripts
│   │   ├── seed_tamilnadu_hierarchy.py           # Populates 6 Districts, 12 Zones, and 12 Areas
│   │   ├── seed_tamilnadu_grid.py                # Populates 21 substations, distribution poles, home meters
│   │   ├── seed_india_grid.py                    # Regional interstate grid seed data
│   │   └── seed_zone_areas.py                    # ZIP / PIN code area boundaries
│   └── tests/                                    # Automated Quality Assurance
│       ├── test_api_endpoints.py                 # REST API unit & integration test suite
│       └── run_project_process.py                # Automated system verification runner
│
├── db.sqlite3                                    # Embedded relational database (pre-seeded with TN grid)
├── FINAL_PROJECT_REPORT.md                       # Comprehensive 58KB engineering and research thesis
├── manage.py                                     # Django command-line execution entrypoint
├── PROJECT_STRUCTURE_LIST.md                     # Complete order-wise project manifest (This document)
├── README.md                                     # Main developer quickstart and overview
├── requirements.txt                              # Python environment dependency manifest
├── run_server.bat                                # 1-Click launcher for Windows
└── run_server.sh                                 # 1-Click launcher for macOS & Linux
```

---

## 🏛️ Order 2: 5-Tier Electrical & Administrative Grid Hierarchy

The system models the real-world electrical grid distribution of Tamil Nadu across 5 connected tiers:

```
[Level 1] STATE DISTRICT
  ├── Example: Chennai District (400kV / 230kV Substation)
  │
  └── [Level 2] ELECTRICITY ZONE
        ├── Example: OMR IT Corridor (110kV / 33kV Primary Substation)
        │
        └── [Level 3] AREA SECTOR (ZIP / PIN CODE)
              ├── Example: Thoraipakkam (PIN 600097) | Sholinganallur (PIN 600119)
              │
              └── [Level 4] FEEDER & POLE TAPS
                    ├── Example: 11kV Feeder Pillar & 415V 3-Phase Transformer
                    │
                    └── [Level 5] DOMESTIC SMART METERS (ESP32)
                          └── Example: Home Meter Box TN-CHE-OMR-001 (230V Single Phase)
```

### ⚡ The "Zip-Line" Cascading Rule
Power flows downward. The mathematical logic enforces:
$$\text{EffectivePower}(Node_n) = \text{LocalSwitch}(Node_n) \land \text{EffectivePower}(Parent)$$

- If **Chennai District** is turned **OFF** $\rightarrow$ All its Zones, Areas, and Home Meters automatically lose power.
- If **OMR Zone** is turned **OFF** $\rightarrow$ All its Areas (Thoraipakkam, Sholinganallur) lose power, while other Zones in Chennai stay ON.
- If **Thoraipakkam Area** is turned **OFF** $\rightarrow$ Only Thoraipakkam's home meters lose power; OMR Zone and neighboring areas remain unaffected.

---

## 🔄 Order 3: Real-Time Execution Lifecycle (Data Flow Order)

```
[Step 1: Physical Sensing]
  ESP32 ADC captures analog inputs:
  - Voltage via ZMPT101B (0-250V AC)
  - Current via ACS712 Hall-Effect sensor (0-30A AC)
           │
           ▼
[Step 2: Edge Telemetry Ingestion]
  ESP32 sends JSON payload via HTTP POST to:
  POST /api/telemetry/report/ or POST /api/esp32/meter/report/
           │
           ▼
[Step 3: AI Anomaly Classification]
  Normalized waveform features (V, I, ΔV, ΔI, Frequency) evaluated by:
  model_weights/fault_classifier.keras
  Categorizes status into: Normal, Short Circuit, Cable Cut, or Overload
           │
           ▼
[Step 4: SCADA State Machine & Database Persistence]
  Django ORM updates GridNode & AreaSector records in db.sqlite3:
  - Updates current_voltage, current_current, frequency
  - If fault detected, flags local_status = False and records FaultLog
           │
           ▼
[Step 5: Cascading Zip-Line Propagation]
  System recursively updates downstream children:
  child.propagate_downstream_status()
           │
           ▼
[Step 6: Geospatial Real-Time Visualization]
  Dashboard polls /api/hierarchy/ & /api/nodes/status_map/:
  - Leaflet / Mapbox animates energized transmission lines (Electric Blue / Cyan)
  - Faulted zones or areas pulse in warning Crimson Red
  - CRT 50Hz sine wave oscilloscope renders live AC waveform
           │
           ▼
[Step 7: User Outage Notification & Maintenance Tracker]
  - Notification banner alerts consumers with problem location & estimated restoration time
  - TANGEDCO repair crew dispatch status displayed in real time
```

---

## 💻 Order 4: Step-by-Step Command Execution & Launch Sequence

Follow this sequence to set up, initialize, and run the project from scratch on any computer:

### Step 1: Environment Preparation
```bash
# Verify Python version (Requires Python 3.10+)
python --version
```

### Step 2: Dependency Installation
```bash
pip install -r requirements.txt
```

### Step 3: Database Schema Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 4: Geographic Data Seeding (Order of Execution)
```bash
# 1. Seed 3-Tier Tamil Nadu District -> Zone -> Area Hierarchy
python scripts/seeds/seed_tamilnadu_hierarchy.py

# 2. Seed Substations, Feeder Pillars, and ESP32 Meter Boxes
python scripts/seeds/seed_tamilnadu_grid.py

# 3. (Optional) Seed Regional ZIP Boundaries
python scripts/seeds/seed_zone_areas.py

# 4. (Optional) Seed Interstate High-Voltage Grid Nodes
python scripts/seeds/seed_india_grid.py
```

### Step 5: Verification & Quality Assurance
```bash
# Run automated API endpoint test suite
python scripts/tests/test_api_endpoints.py

# Run end-to-end pipeline verification test
python scripts/tests/run_project_process.py
```

### Step 6: Server Launch
- **Windows (Single Click):** Double-click `run_server.bat`
- **Linux / macOS:** Run `./run_server.sh`
- **Manual Command:**
  ```bash
  python manage.py runserver 0.0.0.0:8000
  ```

---

## 🌐 Order 5: REST API Endpoints in Execution Order

| Execution Category | HTTP Method | Endpoint Route | Description |
| :--- | :--- | :--- | :--- |
| **0. UI Web App** | `GET` | `/` | Single-page SCADA Dashboard UI (Charcoal & Navy themes) |
| **1. Configuration** | `GET` | `/api/config/mapbox/` | Returns the active Mapbox public token for satellite tiles |
| **2. Authentication** | `POST` | `/api/auth/login/` | Initiates 2FA login by issuing a 6-digit SMS OTP |
| | `POST` | `/api/auth/verify-otp/` | Verifies the OTP code and returns an authenticated session |
| | `POST` | `/api/auth/role/` | Verifies Admin PIN (`1234`) to unlock breaker switches |
| **3. Hierarchy & Map** | `GET` | `/api/hierarchy/` | Returns Tamil Nadu 3-tier hierarchy with live power states |
| | `GET` | `/api/nodes/status_map/` | Returns GeoJSON feature collection of nodes and lines |
| | `POST` | `/api/hierarchy/my-area/` | Matches user's GPS coordinates to the nearest local area |
| | `GET` | `/api/zone/nearest/` | Locates closest electrical substation by GPS query |
| **4. Telemetry & Edge**| `POST` | `/api/telemetry/report/` | Ingests real-time sensory data from ESP32 edge units |
| | `POST` | `/api/esp32/meter/report/`| Ingests domestic meter box telemetry (V, I, kWh, status) |
| | `GET` | `/api/faults/` | Returns historical and active localized fault events |
| **5. Grid Controls** | `POST` | `/api/hierarchy/switch/` | Toggles power state (ON/OFF) at District, Zone, or Area level |
| | `POST` | `/api/zone/<id>/outage/` | Simulates or toggles power outage on a specific zone |
| | `POST` | `/api/nodes/<id>/simulate/`| Simulates fault injection (Short circuit, cable cut, overload) |
| **6. Notifications** | `GET` | `/api/notifications/` | Delivers real-time area outage reasons and maintenance progress |

---

## 🔒 Order 6: Role-Based Access Control & Security Matrix

| Feature / Action | Public Consumer Mode | Authorized Dispatcher / Admin Mode |
| :--- | :---: | :---: |
| **View Live Tamil Nadu Map** | ✅ Yes | ✅ Yes |
| **Monitor AC Oscilloscope Waveform** | ✅ Yes | ✅ Yes |
| **Check Local Area Power Status (ON/OFF)**| ✅ Yes | ✅ Yes |
| **View Fault Diagnostics & Reason** | ✅ Yes | ✅ Yes |
| **View Maintenance & Crew Progress** | ✅ Yes | ✅ Yes |
| **GPS "Find My Area" Detection** | ✅ Yes | ✅ Yes |
| **Toggle District Breaker (Switch ON/OFF)**| ❌ Locked | ✅ Allowed (PIN: `1234`) |
| **Toggle Zone Substation Feeder** | ❌ Locked | ✅ Allowed (PIN: `1234`) |
| **Toggle Local Area Power Supply** | ❌ Locked | ✅ Allowed (PIN: `1234`) |
| **Inject Artificial Fault Simulation** | ❌ Locked | ✅ Allowed (PIN: `1234`) |

---

## 🧠 Order 7: AI Model & Waveform Classification Catalog

The anomaly detection engine uses a trained deep neural network stored at [`model_weights/fault_classifier.keras`](file:///c:/Users/Karthikeyen/Downloads/AI-Powered%20Smart%20Grid%20Fault%20Localization%20System/model_weights/fault_classifier.keras).

### Diagnostic Classification Table:

| Class ID | Fault Category | Physical Signature | Typical Voltage (V) | Typical Current (A) | Recommended TANGEDCO Action |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **0** | **Normal (Healthy)** | Stable 50Hz sine waveform | $220\text{V} - 240\text{V}$ | $0.5\text{A} - 25.0\text{A}$ | Continuous monitoring |
| **1** | **Short Circuit** | Voltage collapse, sharp current spike | $< 90\text{V}$ | $> 50.0\text{A}$ | Trip upstream vacuum breaker immediately; isolate section |
| **2** | **Cable Cut (Open Circuit)**| Zero current flow, float/drop voltage | $\approx 0\text{V}$ | $0.0\text{A}$ | Dispatch field repair van; verify overhead/underground cable |
| **3** | **Overload / Thermal** | Prolonged voltage drop, rated current exceeded | $180\text{V} - 200\text{V}$ | $30.0\text{A} - 45.0\text{A}$ | Balance phase load; switch auxiliary transformer |

---

*System Maintained for TANGEDCO (Tamil Nadu Generation and Distribution Corporation Limited) SCADA Operations.*
