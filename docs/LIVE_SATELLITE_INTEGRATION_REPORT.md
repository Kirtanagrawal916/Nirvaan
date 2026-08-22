# NIRVAAN Live Satellite Integration & Production Verification Report

**Platform:** NIRVAAN — Satellite Disaster Intelligence Platform  
**Branch:** `detection`  
**Date:** 2026-08-22  
**Status:** ✅ LIVE SATELLITE PIPELINE + PRODUCTION INTEGRATION READY  

---

## 1. Executive Summary

The NIRVAAN platform has completed full architectural transition from third-party / mock satellite feeds to the **official Copernicus Data Space Ecosystem (CDSE)**. Real Sentinel-2 Level-2A surface reflectance rasters are retrieved dynamically via OAuth2-authenticated CDSE STAC and Process APIs, preprocessed through float32 raster pipelines, and classified using optical indices (NDWI for flood inundation, dNBR for wildfire burn scars) and AI multimodal vision models.

In addition, the user interface has been enhanced with a **modern collapsible left sidebar navigation experience**, mobile-responsive off-canvas drawer, multi-hazard scene presets, and a 5-stage visual satellite telemetry pipeline that clearly articulates what happened, where, when, why it was detected, and how much area is impacted.

---

## 2. Copernicus Sentinel-2 Integration Architecture

```
[ User AOI / Live Request ]
             │
             ▼
[ CopernicusAuthManager (Keycloak OAuth2) ]
   └── Endpoint: https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token
   └── Token Caching: In-memory cache with 60s pre-expiration buffer & auto-refresh
             │
             ▼
[ Copernicus STAC Scene Discovery ]
   └── Endpoint: https://stac.dataspace.copernicus.eu/v1/search
   └── Collection: sentinel-2-l2a
   └── Spatial filter: Bounding box [min_lon, min_lat, max_lon, max_lat]
   └── Cloud coverage: <= max_cloud_cover (default 80%)
             │
             ▼
[ Copernicus Process API (Sentinel Hub / CDSE) ]
   └── Endpoint: https://sh.dataspace.copernicus.eu/api/v1/process
   └── Dynamic Evalscripts: Float32 GeoTIFF extraction for B02, B03, B04, B08, B11, B12
   └── Array Normalization: Scaled [0.0, 1.0] NumPy matrices with NaN/inf sanitization
             │
             ▼
[ Detection Engine (Modular Detectors) ]
   ├── ModularFloodDetector: NDWI = (B03 - B08) / (B03 + B08) [Threshold > 0.15]
   └── ModularWildfireDetector: NBR = (B08 - B12) / (B08 + B12) & dNBR = NBR_pre - NBR_post
             │
             ▼
[ Situation Assessment & Explainable Risk Engine ]
   ├── Geometric Polygon Extraction & Simplification (EPSG:4326 GeoJSON)
   ├── Demographic Overlay (Affected Population & Infrastructure Proximity)
   └── Data Provenance: REAL_SATELLITE_DATA (Provider: Copernicus Data Space Ecosystem)
```

---

## 3. Disaster Pipelines & Mathematical Verification

### 3.1 Live Flood Pipeline (NDWI & Hydrological Assimilation)
- **Spectral Bands:** Green (`B03`, 560nm) and Near-Infrared (`B08`, 842nm).
- **Index Formula:**
  $$\text{NDWI} = \frac{\text{B03} - \text{B08}}{\text{B03} + \text{B08}}$$
- **Decision Threshold:** $\text{NDWI} > 0.15$ indicates open water / flood inundation.
- **Hydrological Integration:** Open-Meteo Global Flood API assimilates 7-day river discharge ($m^3/s$) and upstream elevation to calibrate confidence scores between $60.0\%$ and $98.0\%$.
- **Provenance Attribution:** Attached as `REAL_SATELLITE_DATA` with provider `"Copernicus Data Space Ecosystem (Sentinel-2 L2A)"`.

### 3.2 Live Wildfire Pipeline (NBR & dNBR Burn Severity)
- **Spectral Bands:** Near-Infrared (`B08`, 842nm) and Shortwave-Infrared 2 (`B12`, 2190nm).
- **Index Formulas:**
  $$\text{NBR} = \frac{\text{B08} - \text{B12}}{\text{B08} + \text{B12}}$$
  $$\text{dNBR} = \text{NBR}_{\text{pre-fire}} - \text{NBR}_{\text{post-fire}}$$
- **USGS / Copernicus Burn Severity Tiers:**
  - $\text{dNBR} < 0.10$: Unburned / Regrowth
  - $0.10 \le \text{dNBR} < 0.27$: Low Severity Burn
  - $0.27 \le \text{dNBR} < 0.66$: Moderate Severity Burn
  - $\text{dNBR} \ge 0.66$: High / Critical Severity Burn

---

## 4. API Endpoints & Production Infrastructure

| Method | Endpoint | Description | Production Status |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Service health & readiness | ✅ 200 OK |
| `GET` | `/api/v1/satellite/latest` | Latest Copernicus Sentinel-2 pass | ✅ 200 OK (`REAL_SATELLITE_DATA`) |
| `GET` | `/api/v1/disaster/latest` | Latest real detection incident | ✅ 200 OK |
| `GET` | `/api/v1/satellite-scenes` | Ingested satellite passes database | ✅ 200 OK (69+ scenes) |
| `GET` | `/api/v1/alerts` | Database alerts generated from detections | ✅ 200 OK |
| `GET` | `/api/v1/risk` | Inundation/burn scar GeoJSON FeatureCollection | ✅ 200 OK |
| `POST` | `/api/v1/detection` | Enqueue async live Copernicus detection job | ✅ 202 Accepted |
| `GET` | `/api/v1/detection/{id}` | Poll job progress and fetch results | ✅ 200 OK |
| `POST` | `/api/v1/analyze/disaster` | Real-time multi-hazard analysis | ✅ 200 OK |
| `POST` | `/api/v1/analyze/image` | Gemini Vision uploaded scene analysis | ✅ 200 OK |
| `POST` | `/api/v1/reports` | Grounded SITREP markdown/JSON report generator | ✅ 201 Created |
| `GET` | `/api/v1/reports/{id}` | Fetch generated SITREP report | ✅ 200 OK |

### Production Deployments
- **Render Backend:** `https://nirvaan-pd7i.onrender.com` (Uvicorn ASGI on Python 3.13, health check passed, CORS configured for `https://nirvaan-one.vercel.app`).
- **Vercel Frontend:** `https://nirvaan-one.vercel.app` (Vite production bundle built and connected).

---

## 5. Live Mode vs Instant Demo Mode

NIRVAAN maintains a strict architectural boundary between live satellite observations and demo artifacts:
- **LIVE MODE:** Invokes CDSE OAuth2 authentication, executes live STAC search and Process API band download, calculates dynamic spectral matrices, and tags all outputs with `REAL_SATELLITE_DATA`. If satellite service is unreachable or credentials fail, it returns an explicit error state (`NO_LIVE_DATA`) and never silently fakes live observations.
- **INSTANT DEMO MODE:** Loads verified, deterministic, precomputed disaster benchmark packages (Surat Flood, Rhodes Wildfire, Emilia-Romagna Inundation) instantaneously for offline demonstrations, drills, and latency-sensitive briefings.

---

## 6. Modern Frontend Architecture & Navigation

1. **Left Sidebar Experience:**
   - Fixed, sticky left sidebar on desktop (`260px` default width) with toggleable collapsed icon mode (`72px`, keyboard shortcut `Ctrl+B`).
   - Organized into logical sections: `MONITORING`, `INTELLIGENCE`, and `SYSTEM`.
   - Mobile-responsive off-canvas drawer with smooth slide transition, touch backdrop overlay, and topbar hamburger toggle.
   - Preserves all teammate styling, themes (Dark / Light mode), and canvas satellite orbit background.
2. **Satellite Monitoring Flow:**
   - Multi-stage visual stepper: `1. AOI & Scene` ➔ `2. Pre-Event Baseline` ➔ `3. Post-Event Pass` ➔ `4. NDWI / dNBR Math` ➔ `5. Impact Assessment`.
   - Scene preset quick-selector for immediate comparison across different hazard types and geographies.
   - Dual-viewport comparison toggle, blended heatmap overlay, and vector hotspot bounding boxes.

---

## 7. Automated Test Suite Results

```text
============================= test session starts =============================
platform win32 -- Python 3.13.5, pytest-9.1.1
rootdir: C:\Users\Kirta\OneDrive\Desktop\Nirvaan\Nirvaan
collected 223 items

tests/test_affected_area.py ......                                       [  2%]
tests/test_api.py ..........                                             [  7%]
tests/test_change_detection.py ....                                      [  8%]
tests/test_confidence.py ...                                             [ 10%]
tests/test_copernicus_pipeline.py .........                              [ 14%]
tests/test_data_provenance.py ........                                   [ 17%]
tests/test_dataset_loader.py .......                                     [ 21%]
tests/test_detection_contract.py ......                                  [ 23%]
tests/test_detection_pipeline.py ....                                    [ 25%]
tests/test_end_to_end_pipeline.py .....                                  [ 27%]
tests/test_event_schema.py .......                                       [ 30%]
tests/test_fastapi_app.py ...........                                    [ 35%]
tests/test_flood_detector.py ....                                        [ 37%]
tests/test_gemini_integration.py ...........                             [ 42%]
tests/test_geometry.py .....                                             [ 44%]
tests/test_hotspot_extractor.py ......                                   [ 47%]
tests/test_infrastructure.py ....                                        [ 49%]
tests/test_instant_demo.py ....                                          [ 51%]
tests/test_mapping.py ...........                                        [ 56%]
tests/test_mask_generator.py .....                                       [ 58%]
tests/test_mode_controller.py .......                                    [ 61%]
tests/test_multispectral_preprocessor.py .....                           [ 63%]
tests/test_phase2_reliability.py ........                                [ 67%]
tests/test_phase3_advanced.py ........                                   [ 70%]
tests/test_population.py ....                                            [ 72%]
tests/test_provenance.py ....                                            [ 74%]
tests/test_raster_validator.py .........                                 [ 78%]
tests/test_recommendations.py ....                                       [ 80%]
tests/test_risk_zones.py ....                                            [ 82%]
tests/test_severity.py ....                                              [ 83%]
tests/test_severity_classifier.py ......                                 [ 86%]
tests/test_sitrep_flow.py .....                                          [ 88%]
tests/test_situation_assessment.py .....                                 [ 91%]
tests/test_situation_report.py .....                                     [ 93%]
tests/test_state_manager.py .....                                        [ 95%]
tests/test_validation.py ......                                          [ 98%]
tests/test_wildfire_detector.py ....                                     [100%]

======================= 223 passed, 1 warning in 55.87s =======================
```

---

## 8. Known Limitations & Mitigations

1. **Copernicus Revisit Interval:** Optical Sentinel-2 passes over a specific coordinate occur every 5 days (or 2-3 days at mid-latitudes with Sentinel-2A + 2B constellation). *Mitigation:* NIRVAAN integrates Open-Meteo real-time river gauges and severe weather feeds to bridge satellite pass intervals.
2. **Cloud Occlusion:** Extreme meteorological events frequently produce heavy cloud cover that obscures optical spectral bands. *Mitigation:* STAC search filters by `eo:cloud_cover <= 80%` and penalizes confidence scores proportionally; radar SAR Sentinel-1 support is designed into the ingestion schema for all-weather penetration.
3. **Render Free Tier Cold Starts:** Free instance spins down after 15 minutes of inactivity, resulting in a ~40s initial response time on the first health check. *Mitigation:* The frontend gracefully displays animated skeleton loaders and automatic retry logic on network timeouts.
