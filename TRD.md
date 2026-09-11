# Technical Requirements Document (TRD) - GeoShield-NER

## 1. Architecture Overview
The system utilizes a decoupled microservices architecture designed to run entirely on local or zero-cost tier infrastructure for the hackathon MVP.

## 2. Technology Stack
* **Frontend (Command Dashboard):** React.js, Tailwind CSS, Leaflet.js (for zero-cost web mapping).
* **Backend Framework:** FastAPI (Python 3.11) utilizing Uvicorn for asynchronous I/O.
* **Mobile Application:** Flutter (Dart) for cross-platform compatibility.
* **Database & Spatial Engine:** PostgreSQL with the PostGIS extension (running locally via Docker). SQLite (via sqflite/WatermelonDB) for mobile local storage.
* **AI/Machine Learning:** PyTorch, XGBoost, Scikit-Learn, TensorFlow Lite (for mobile on-device inference).

## 3. Local Development Environment
* **IDE & OS:** Visual Studio Code on a Windows operating system. Use the Docker and SQLite extensions for container orchestration and edge database inspection.
* **Compute Hardware:** The XGBoost and MobileNetV3 models will execute locally, leveraging the available NVIDIA RTX 5060 GPU and Intel Core Ultra 7 processor to eliminate cloud compute costs.

## 4. External APIs & Services
* **Weather Data:** Open-Meteo API (zero-cost, no-auth historical and forecast precipitation data).
* **Alerts:** Telegram Bot API (mocking the National Common Alerting Protocol/SMS Gateway).

## 5. Technical Constraints & Mitigation
* **Constraint:** Complex spatial queries crashing the server during live demos.
  * **Mitigation:** Pre-process Cartosat DEM rasters into static vector polygons/GeoJSON stored in PostGIS.
* **Constraint:** Network instability during mobile field reporting.
  * **Mitigation:** Implement an append-only SQLite queue on the Flutter app using UUIDs to prevent duplicate records upon re-sync.
* **Constraint:** Machine learning inference blocking the FastAPI event loop.
  * **Mitigation:** Load `.pkl`/`.onnx` model weights into global memory during the FastAPI startup event and run predictions in background tasks.