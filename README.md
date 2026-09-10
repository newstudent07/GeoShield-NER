# GeoShield-NER: AI-Enabled Landslide Risk Monitoring & Early Warning System

> **Smart India Hackathon 2026**  
> **Problem Statement ID:** 26001  
> **Theme:** Disaster Management | **Category:** Software  
> **Pilot Focus:** Aizawl & NH-29 Arterial Mountain Corridor  

---

## 📌 Executive Summary

The **North Eastern Region (NER)** accounts for over **0.18 million km²** (42.8%) of India's total landslide-prone landmass, suffering from chronic slope failures, severed lifeline highways, and disaster-isolated communities during monsoons. Historical records document **38,051 recorded landslide events** across the eight northeastern states.

**GeoShield-NER** shifts disaster governance from **reactive clearance to proactive prevention**. By integrating physical rainfall saturation mechanics with spatial gradient boosting, the platform provides district authorities with a **6-to-24-hour evacuation and intervention lead time**, monitors arterial road connectivity, and validates crowdsourced hazard reports through an offline-resilient edge pipeline.

---

## 🎯 Scope Architecture: MVP vs. Full System Vision

| Dimension | Hackathon MVP Scope (Working Prototype) | Full Production Vision (Pan-NER Scale) |
| :--- | :--- | :--- |
| **Geographic Coverage** | **Pilot Corridor:** High-density pilot grid (~150 cells, $500\,\text{m} \times 500\,\text{m}$) covering Aizawl, Mizoram & NH-29 corridor. | **Pan-NER Deployment:** All 8 northeastern states covering 0.18M km² and over 38,000 historical hazard vectors. |
| **Atmospheric Data** | **Open-Meteo API & Scenario Engine:** Real-time rainfall feeds with a live slider simulating monsoon spikes (0–200 mm). | **Live IMD Doppler & Automatic Weather Stations:** Multi-sensor radar feeds, WRF numerical weather models, and AWS network. |
| **Satellite & Radar** | **Pre-processed DEM Rasters:** Static Cartosat DEM slope/aspect models with pre-computed ground deformation baselines. | **Live Automated InSAR Ingestion:** Weekly Copernicus Sentinel-1 SAR interferometry for millimeter-scale slope creep tracking. |
| **Ground Sensing** | **Simulated Soil Telemetry:** Soil moisture, porosity, and clay-loam saturation curves mapped from ICAR-NBSS&LUP series. | **Physical LoRaWAN Sensor Meshes:** Deep-slope piezometers, inclinometers, and soil pore-pressure borehole telemetry. |
| **Crowdsourced Validation**| **Mobile Edge Vision:** On-device MobileNetV3 / OpenCV filter validating photo fissures and GPS integrity. | **Distributed Multi-Stage Computer Vision:** Server-side aerial drone photogrammetry and multimodal satellite verification. |
| **Alert Dissemination** | **Zero-Cost Alert Gateway:** Automated webhooks triggering instant emergency notifications via Telegram Bot API. | **National CAP v1.2 Integration:** Cell broadcast and edge SMS delivery directly over 2G/4G/5G through NDMA SACHET / C-DOT. |
| **Deployment Mode** | **Local Decoupled Stack:** Dockerized PostGIS, local FastAPI engine, Vite/React dashboard, and Flutter client. | **Resilient Multi-Cloud Hybrid:** Geo-redundant Kubernetes clusters, state-level command centers, and district edge nodes. |

---

## 🧠 System Architecture & Predictive Engine

GeoShield-NER operates an end-to-end 4-stage pipeline:

```
[ Data Ingestion ] ──────► [ GIS Spatial Engine ] ──────► [ Predictive AI Engine ] ──────► [ Dispatch & Field UI ]
  • Open-Meteo API           • PostGIS 15 / GIST             • ISRO Saturated Formula       • React + Leaflet Dashboard
  • Cartosat DEM             • GDAL Slope / Aspect           • XGBoost Spatial Classifier    • Flutter SQLite Offline App
  • Crowd Hazard Photos      • Road Buffer Indexing          • MobileNetV3 Edge Vision       • Telegram / CAP Alert Gateway
```

### 1. Physics-Guided Saturation Anchor
The system anchors its predictions on the empirical logistic regression equation developed by **ISRO / NRSC**:

$$z = -3.817 + 0.077 \cdot DR + 0.058 \cdot 3DCR + 0.008 \cdot 30DAR, \quad P_{\text{ISRO}} = \frac{1}{1 + e^{-z}}$$

* **$DR$**: Daily Rainfall (mm)
* **$3DCR$**: 3-Day Cumulative Rainfall (mm)
* **$30DAR$**: 30-Day Antecedent Rainfall (mm)

### 2. Spatial Machine Learning Classifier
The calculated $z$-score is fed into an **XGBoost Classifier** alongside static topographical features:
$$\text{Feature Vector} = \big[ z\text{-score},\\, DR,\\, 3DCR,\\, 30DAR,\\, \text{base\\_slope},\\, \text{soil\\_porosity} \big]$$
* **$P < 0.40$**: Low Risk (Green)
* **$0.40 \le P < 0.70$**: Moderate Watch (Orange)
* **$P \ge 0.70$**: Critical Slope Failure Warning (Red) $\rightarrow$ Triggers automated evacuation and bypass routing.

### 3. Edge-Resilient Field Verification
* **Offline-First Synchronization:** The mobile client (Flutter) uses local SQLite append-only storage (`synced = 0`). During mountain network blackouts, patroller reports are cached and atomically pushed to the backend upon network reconnection using UUID idempotency.
* **On-Device Vision Filter:** A quantized MobileNetV3 model screens captured field photos directly on the device, flagging tension fissures and structural debris while filtering out spam or unverified images.

---

## 🛠️ Complete Technology Stack

| Layer | Technologies Used | Key Packages / Libraries |
| :--- | :--- | :--- |
| **Command Web Dashboard** | React 18, Vite, Tailwind CSS | `react-leaflet`, `leaflet`, `lucide-react`, `axios` |
| **Backend & Microservices** | Python 3.11, FastAPI, Uvicorn | `pydantic-v2`, `sqlalchemy`, `httpx`, `python-telegram-bot` |
| **Database & Spatial Engine** | PostgreSQL 15, PostGIS 3.3 (Docker) | `GeoAlchemy2`, `shapely`, `pyproj` |
| **Machine Learning Engine** | PyTorch, XGBoost, Scikit-Learn | `xgboost`, `scikit-learn`, `joblib`, `numpy` |
| **Edge Vision & Processing** | TensorFlow Lite, OpenCV, Pillow | `tflite-runtime`, `piexif`, `opencv-python-headless` |
| **Mobile Application** | Flutter 3.x, Dart | `sqflite`, `geolocator`, `camera`, `dio`, `connectivity_plus` |

---

## 📁 Repository Structure & Documentation Map

```text
├── docs/
│   ├── PRD.md                             # Product Requirements Document (Scope & Requirements)
│   ├── TRD.md                             # Technical Requirements Document (Stack & Constraints)
│   ├── backendschema.md                   # PostgreSQL/PostGIS Schema & FastAPI REST Specifications
│   ├── project_phases.md                  # 7-Phase Agentic Execution Roadmap (36-Hour Plan)
│   └── SIH2026_Idea_Presentation_*.md     # Official SIH 6-Slide Pitch Guide & Citations
│
├── prompts/                               # Multi-Agent Implementation Blueprints
│   ├── implementation_member1_gis.md      # Docker PostGIS, Spatial Grid & Geometry Validation
│   ├── implementation_member2_ml.md       # ISRO Formula Engine & XGBoost Training Pipeline
│   ├── implementation_member3_vision.md   # EXIF GPS Parser & MobileNetV3 Edge Filter
│   ├── implementation_member4_backend.md  # FastAPI Central Service, Weather Ingestion & Alerts
│   ├── implementation_member5_frontend.md # React Leaflet GIS Console & Scenario Simulator
│   └── implementation_member6_mobile.md   # Offline SQLite Queue & Flutter Field App
│
├── data/                                  # Pilot GIS layers, DEM rasters, and rainfall tables
├── backend/                               # FastAPI application code & DB migrations
├── frontend/                              # Vite React web dashboard application
└── mobile/                                # Flutter client project source
```

---

## 🚀 Quick Start Guide (Local Zero-Cost Setup)

### 1. Launch Spatial Database (Docker)
```bash
docker run --name geoshield-postgis \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=geoshield123 \
  -e POSTGRES_DB=geoshield_db \
  -p 5432:5432 -d postgis/postgis:15-3.3
```

### 2. Backend & Model Server
```bash
cd backend
python -m venv venv
# Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python scripts/init_pilot_grid.py    # Seed pilot polygons into PostGIS
python scripts/train_model.py        # Train & serialize XGBoost classifier
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
* Interactive API Documentation: `http://localhost:8000/docs`

### 3. Command Web Dashboard
```bash
cd frontend
npm install
npm run dev
```
* Dashboard URL: `http://localhost:5173`

---

## 📚 References & Authoritative Sources

1. **ISRO & National Remote Sensing Centre (NRSC):** *Landslide Atlas of India (2023)* — Mathematical formulation of empirical rainfall triggering probability thresholds. [isro.gov.in](https://www.isro.gov.in/)
2. **Geological Survey of India (GSI):** *National Landslide Susceptibility Mapping (NLSM)* — Regional baseline documenting 38,051 recorded slope failures across the 8 NER states. [gsi.gov.in](https://www.gsi.gov.in/)
3. **India Meteorological Department (IMD):** *Hydromet Division Telemetry & MAUSAM Studies* — Regional rainfall normals (~2,450 mm annual average) and extreme precipitation classifications. [mausam.imd.gov.in](https://mausam.imd.gov.in/)
4. **National Disaster Management Authority (NDMA):** *Common Alerting Protocol (CAP v1.2)* — Geo-targeted disaster broadcast protocols. [sachet.ndma.gov.in](https://sachet.ndma.gov.in/)
5. **ICAR - NBSS&LUP:** *Soil Series of Northeast India (Publications 52b–75b)* — Clay-loam shear thresholds, saturation limits, and high soil porosity (40%–60%). [icar.org.in](https://icar.org.in/)