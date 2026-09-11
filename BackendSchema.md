# Backend Schema & API Design - GeoShield-NER

## 1. Database Schema (PostgreSQL/PostGIS)

**Table: `users`**
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | Primary Key | Unique user identifier. |
| `role` | VARCHAR | NOT NULL | `admin`, `field_worker`, `citizen`. |
| `phone_number` | VARCHAR | Unique | Used for Telegram/SMS alert mapping. |

**Table: `grid_cells` (Spatial)**
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `grid_id` | VARCHAR | Primary Key | Unique string (e.g., `cell_001`). |
| `geom` | GEOMETRY(Polygon) | Indexed (GIST)| The $500\text{ m} \times 500\text{ m}$ spatial boundary. |
| `base_slope` | FLOAT | | Pre-calculated gradient from DEM. |
| `soil_porosity` | FLOAT | | Static soil baseline (e.g., 40.0 - 60.0). |
| `current_risk`| FLOAT | Default 0.0 | Latest XGBoost probability ($0.0 - 1.0$). |

**Table: `weather_logs`**
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `log_id` | UUID | Primary Key | Unique log identifier. |
| `grid_id` | VARCHAR | Foreign Key | References `grid_cells.grid_id`. |
| `timestamp` | TIMESTAMPTZ| Indexed | Time of weather reading. |
| `daily_rain` | FLOAT | | $DR$ (mm). |
| `cumulative_3d`| FLOAT | | $3DCR$ (mm). |
| `antecedent_30d`|FLOAT | | $30DAR$ (mm). |

**Table: `field_reports`**
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `report_id` | UUID | Primary Key | Generated on mobile to prevent duplicates. |
| `reporter_id` | UUID | Foreign Key | References `users.id`. |
| `geom` | GEOMETRY(Point) | Indexed (GIST)| Hardware-signed GPS location. |
| `photo_url` | VARCHAR | | Path to locally stored/uploaded image. |
| `ai_confidence`| FLOAT | | MobileNetV3 validity score. |
| `status` | VARCHAR | Default 'pending' | `pending`, `verified`, `dismissed`. |

## 2. API Endpoints (FastAPI)

* **`GET /api/v1/grid/risk`**
  * **Description:** Fetches all grid cells as a GeoJSON FeatureCollection.
  * **Response:** Includes geometry and `current_risk` property for Leaflet color coding.
* **`POST /api/v1/simulate/weather`**
  * **Payload:** `{"rainfall_mm": 150, "zone_id": "all"}`
  * **Description:** Triggers the ISRO + XGBoost pipeline to artificially recalculate risk for the demo.
* **`POST /api/v1/reports/sync`**
  * **Payload:** Array of offline `field_reports` objects (JSON).
  * **Description:** Upserts queued mobile reports. Ignores existing UUIDs.
* **`POST /api/v1/alerts/trigger`**
  * **Description:** Internal webhook fired when a cell's risk $> 0.70$. Pushes payload to Telegram Bot API.