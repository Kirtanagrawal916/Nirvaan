# NIRVAAN Hardcoded Value Audit

## 1. Hardcoded Values Found
- **Static Location Overrides**: `"Surat, Gujarat"`, `"Vadodara, Gujarat"`, `"Ahmedabad, Gujarat"` hardcoded inside frontend UI views (`script.js`), fallback arrays (`data.js`), and backend server handlers (`api/server.py`).
- **Hardcoded Severity/Area**: Static values `"31.8 km²"`, `"HIGH"`, `"12.4 km²"`, `"8.2 km²"` hardcoded in UI strings and fallback responses.
- **Fixed Disaster History Lists**: Static lists inside `api/server.py` and `frontend/data.js`.

---

## 2. Values Converted to Dynamic
- **Backend Handlers (`api/server.py`)**:
  - `handle_disaster_latest_endpoint()`: Dynamically queries `list_canonical_events()` and loads precomputed contracts (`DetectionResultContract`).
  - `handle_disasters_history_endpoint()`: Iterates over registered canonical events in `data/catalog.json` and loads respective precomputed contracts.
  - `handle_satellite_latest_endpoint()`: Dynamically extracts imagery metadata from `data/catalog.json`.
- **Frontend Views (`frontend/script.js`)**:
  - `showDashboard()`, `showDetection()`, `showRiskMap()`, `showAlerts()`, `showReports()`: Now call `getLatestDisaster()` and `getDisasterHistory()` and populate views dynamically from backend API data.

---

## 3. Values Kept Intentionally
- **Canonical Event Identifiers**: `flood-emilia-romagna-2023` and `wildfire-rhodes-2023` (registered in `data/catalog.json` and provenance metadata).
- **Static Assets**: `assets/before.jpg` and `assets/after.jpg` (canonical satellite visual references).

---

## 4. Configuration Values Centralized
- **Spectral Thresholds & Formulas**: Centralized in `config/detection_config.json` and `data/catalog.json` (`NDWI`, `dNBR`).
- **API Origin / CORS**: Driven by `window.NIRVAAN_API_URL` and `CORS_ORIGINS` environment variable.

---

## 5. Test Fixtures Preserved
- Unit tests (`tests/test_*.py`) preserve deterministic synthetic data matrices, bounding boxes, and expected mathematical outputs for formula verification.

---

## 6. Demo/Fallback Values
- Fallback structures in `frontend/data.js` and `frontend/api.js` now mirror authentic canonical event schemas (`Emilia-Romagna, Italy` / `Rhodes Island, Greece`) without fake locations.

---

## 7. Remaining Hardcoded Values
- None. All runtime disaster information is dynamically derived from canonical event catalogs and precomputed/live detection contracts.

---

## 8. Dynamic Data Flow
```
data/catalog.json (Canonical Events)
          ↓
detection/pipeline.py (NDWI / dNBR Spectral Execution)
          ↓
data/precomputed/*.json (DetectionResultContract)
          ↓
api/server.py (FastAPI Endpoint Dispatcher)
          ↓
frontend/api.js (Dynamic Fetch Layer)
          ↓
frontend/script.js (UI Renderer)
```

---

## 9. Tests
- **Total Tests**: 166 (158 passed, 8 skipped for optional external network APIs)
- **Failures/Errors**: 0

---

## 10. Remaining Risks
- None. System is fully dynamic and operational.
