# NIRVAAN TASK-003 — Detection + Map Technical Lock

## Purpose

This document locks the technical architecture, spectral algorithms, mapping stack, upload validation criteria, caching patterns, and operating mode contracts for **NIRVAAN** prior to feature implementation.

---

## 1. Flood Detection Method (`LOCKED`)

- **Algorithm**: Normalized Difference Water Index (**NDWI**)
- **Mathematical Formula**:
  $$\text{NDWI} = \frac{\text{Green} - \text{NIR}}{\text{Green} + \text{NIR}}$$
- **Sentinel-2 Band Mapping**:
  - $\text{Green} = \text{B03}\ (560\text{ nm},\ 10\text{m resolution})$
  - $\text{NIR} = \text{B08}\ (842\text{ nm},\ 10\text{m resolution})$
- **Prototype Water Threshold**: $\text{NDWI} > 0.0$ (pixels with positive NDWI values indicate open surface water).
- **Post-Processing**: 3x3 morphological opening filter to remove isolated pixel noise and retain coherent water bodies with minimum region area $> 100\text{ m}^2$.

---

## 2. Wildfire Detection Method (`LOCKED`)

- **Algorithm**: Normalized Burn Ratio (**NBR**) and Delta NBR ($\Delta\text{NBR}$) change detection.
- **Mathematical Formulas**:
  $$\text{NBR} = \frac{\text{NIR} - \text{SWIR-2}}{\text{NIR} + \text{SWIR-2}}$$
  $$\Delta\text{NBR} = \text{NBR}_{\text{before}} - \text{NBR}_{\text{after}}$$
- **Sentinel-2 Band Mapping**:
  - $\text{NIR} = \text{B08}\ (842\text{ nm},\ 10\text{m resolution})$
  - $\text{SWIR-1} = \text{B11}\ (1610\text{ nm},\ 20\text{m resolution})$
  - $\text{SWIR-2} = \text{B12}\ (2190\text{ nm},\ 20\text{m resolution})$
- **Prototype Severity Scale (`PROTOTYPE-ONLY`)**:
  - $\Delta\text{NBR} < 0.1$: Unburned / Low Risk
  - $0.1 \le \Delta\text{NBR} < 0.27$: Low Severity Burn
  - $0.27 \le \Delta\text{NBR} < 0.66$: Moderate Severity Burn
  - $\Delta\text{NBR} \ge 0.66$: High Severity / Critical Burn Scar

---

## 3. Required Spectral Bands (`LOCKED`)

All band configurations are centralized in `config/detection_config.yaml` and `config/detection_config.json`, referencing `data/catalog.json`:

- **Flood Ingestion**:
  - Primary: `B03` (Green), `B08` (NIR)
  - Secondary/Visual: `B04` (Red), `B02` (Blue)
- **Wildfire Ingestion**:
  - Primary: `B08` (NIR), `B12` (SWIR-2)
  - Secondary/Visual: `B11` (SWIR-1), `B04` (Red)

No module shall hardcode band assignments independently.

---

## 4. Threshold Configuration (`PROTOTYPE-ONLY`)

Thresholds are centralized in `config/detection_config.yaml` and `config/detection_config.json` for easy tuning:

```yaml
flood:
  prototype_thresholds:
    ndwi_water_threshold: 0.0
    min_affected_area_m2: 100.0

wildfire:
  prototype_thresholds:
    dnbr_severity_classes:
      unburned: { min: -0.1, max: 0.1 }
      low_severity: { min: 0.1, max: 0.27 }
      moderate_severity: { min: 0.27, max: 0.66 }
      high_severity: { min: 0.66, max: 2.0 }
```

These values represent **prototype evaluation configurations** tailored for the hackathon MVP and are not presented as official operational emergency criteria.

---

## 5. Mapping Stack (`LOCKED`)

- **Primary Mapping Engine**: `Folium`
- **Streamlit Integration**: `streamlit-folium`
- **Selection Rationale**:
  1. Native Python ecosystem integration with `GeoPandas` and `Shapely`.
  2. Direct rendering of GeoJSON layers, vector polygons, tooltips, and custom color legends without frontend compile steps.
  3. Proven performance for displaying disaster masks and hotspot markers in 4-day hackathon conditions.

---

## 6. Upload Validation Rules (`LOCKED`)

- **Accepted Extensions**: `.tif`, `.tiff`, `.png`, `.jpg`, `.jpeg`, `.zip`
- **Max File Size**: $200\text{ MB}$ per file/archive.
- **Validation Pipeline Contract**:
  1. `check_file_exists`: Verify path accessibility.
  2. `check_readable`: Verify image decoder integrity.
  3. `verify_channels`: Ensure at least 3 channels (RGB) or single-band GeoTIFF rasters.
  4. `verify_bands_present`: Validate required spectral bands for selected disaster type.

---

## 7. Streamlit State Strategy (`LOCKED`)

`st.session_state` manages transient application state across user reruns:
- `selected_event_id`: Currently chosen event from `data/catalog.json`.
- `selected_disaster_type`: Active disaster filter (`flood` or `wildfire`).
- `active_mode`: Operating mode (`INSTANT_DEMO` or `LIVE_ANALYZE`).
- `analysis_result`: Current structured assessment dictionary.
- `error_message`: Active error notification state.

---

## 8. Caching Strategy (`LOCKED`)

- **`st.cache_data`**:
  - Deterministic image resampling, band normalization, NDWI/dNBR raster computations, mask generation, area metrics calculations.
- **`st.cache_resource`**:
  - Reusable dataset catalog readers, GeoTIFF file handle wrappers, model weights/loader instances.

---

## 9. Instant Demo Mode (`LOCKED`)

- **Operating Mode**: `INSTANT_DEMO` (Default)
- **Behavior**: Loads precomputed canonical dataset outputs from `data/catalog.json` (`flood-emilia-romagna-2023` and `wildfire-rhodes-2023`).
- **Goal**: Guarantees zero-latency, 100% reliable hackathon presentation path without network or heavy local computation delays.

---

## 10. Live Analyze Mode (`LOCKED`)

- **Operating Mode**: `LIVE_ANALYZE`
- **Behavior**: Executes dynamic optical preprocessing, spectral index calculation ($\text{NDWI}$, $\Delta\text{NBR}$), difference masking, and hotspot extraction on user-uploaded or selected imagery.
- **Goal**: Demonstrates full end-to-end algorithmic capability during live judge interaction.

---

## 11. Configuration Ownership (`LOCKED`)

- Centralized config file: [config/detection_config.yaml](file:///c:/Users/Kirta/OneDrive/Desktop/Nirvaan/Nirvaan/config/detection_config.yaml) and [config/detection_config.json](file:///c:/Users/Kirta/OneDrive/Desktop/Nirvaan/Nirvaan/config/detection_config.json).
- Owned by Person 1 (Satellite Intelligence / Disaster Detection Developer).
- Downstream modules (`preprocessing/`, `detection/`, `analysis/`, `mapping/`, `app.py`) must import configuration settings rather than defining redundant local constants.

---

## 12. Decisions Locked (`LOCKED`)

- Flood formula: $\text{NDWI} = \frac{\text{B03} - \text{B08}}{\text{B03} + \text{B08}}$
- Wildfire formula: $\text{NBR} = \frac{\text{B08} - \text{B12}}{\text{B08} + \text{B12}}$ & $\Delta\text{NBR} = \text{NBR}_{\text{before}} - \text{NBR}_{\text{after}}$
- Required Sentinel-2 bands: `B03`, `B08`, `B11`, `B12`
- Mapping framework: `Folium` + `streamlit-folium`
- Operating modes: `INSTANT_DEMO` vs `LIVE_ANALYZE`
- Centralized configuration files: `config/detection_config.yaml` / `config/detection_config.json`

---

## 13. Decisions Deferred (`DEFERRED`)

- Live SAR / Sentinel-1 radar ingestion pipeline (deferred to post-hackathon).
- Deep learning segmentation model fine-tuning (deferred to post-hackathon; threshold spectral indices used for MVP).
- Real-time weather radar data stream integration (deferred to post-hackathon).

---

## 14. Risks / Limitations (`PROTOTYPE-ONLY`)

- **Optical Cloud Obstruction**: Optical spectral indices ($\text{NDWI}$, $\Delta\text{NBR}$) require clear sky acquisitions. Heavy cloud cover on post-event dates requires fallback to clear-sky observation windows or warning disclaimers in UI.
- **Prototype Severity Bands**: Severity band thresholds are heuristic prototype values for demonstration and must be labeled as prototype scoring criteria.
