# Product Requirements Document (PRD) - GeoShield-NER

## 1. Project Overview
GeoShield-NER is an AI-powered landslide early warning and monitoring system designed for the North Eastern Region (NER). The MVP focuses on a single high-risk pilot corridor (e.g., NH-29 or Aizawl) to demonstrate a proactive, end-to-end disaster mitigation pipeline.

## 2. Target Audience
* **District/State Disaster Management Authorities (DDMA/SDMA):** Require real-time risk heatmaps and automated alert dispatch capabilities.
* **Field Patrollers & Citizens:** Require a resilient, offline-capable mobile application to report ground fissures and blockages in low-network mountain terrains.

## 3. Core MVP Features
* **District Command Dashboard (Web):**
  * Interactive map plotting terrain grid cells ($500\text{ m} \times 500\text{ m}$).
  * Dynamic color-coding based on live risk probability (Green: $<0.4$, Orange: $0.4 - 0.69$, Red: $\ge 0.70$).
  * Weather simulation slider to manually trigger extreme rainfall events (e.g., Cloudburst simulation) for live demonstration.
* **Predictive AI Engine:**
  * Calculates baseline soil saturation using the ISRO empirical formula:  
    $$z = -3.817 + 0.077 \cdot DR + 0.058 \cdot 3DCR + 0.008 \cdot 30DAR$$
  * Feeds the $z$-score and static terrain data (slope, soil type) into an XGBoost classifier for final probability scoring.
* **Offline-First Mobile App:**
  * Geotagged photo capture for hazard reporting.
  * Local queue system that caches reports during network blackouts and auto-syncs when connectivity is restored.
  * On-device image filtering (MobileNetV3) to reject spam/noise.
* **Zero-Cost Alert Gateway:**
  * Automated webhooks dispatching emergency notifications (coordinates, severity) via Telegram Bot API simulating SMS broadcasts.

## 4. Out of Scope for MVP
* Live ingestion of Sentinel-1 InSAR satellite imagery.
* Physical hardware/IoT soil moisture sensor deployment.
* Pan-NER dataset loading (restricting map data to one pilot district to ensure high browser performance).