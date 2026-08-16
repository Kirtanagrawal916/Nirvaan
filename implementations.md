# NIRVAAN — AI Satellite Disaster Monitoring
## Evidence-Grounded 4-Day Hackathon Implementation Plan

> **Implementation source of truth:** `tasks.md`
>
> **Core principle:** NIRVAAN must produce a useful disaster assessment from **real, sourced satellite evidence**. The project must never present a placeholder, hard-coded threshold, estimate, or LLM-generated statement as a verified fact.

---

## 1. Product Definition

**NIRVAAN** is an offline-first satellite disaster monitoring prototype that converts a before/after satellite image pair into rapid situational awareness.

### One-line pitch

> **NIRVAAN turns satellite observations into evidence-grounded disaster intelligence within minutes.**

### Four questions NIRVAAN answers

1. **Where?** — affected regions and hotspots.
2. **What?** — flood or wildfire evidence.
3. **How bad?** — affected area and prototype severity.
4. **What next?** — evidence-grounded verification and response priorities.

---

# 2. MVP Contract — What Must Actually Work

### P0 — Non-negotiable

- One real flood event with sourced before/after Sentinel-2 imagery.
- One real wildfire event with sourced before/after Sentinel-2 imagery.
- Spectral-index-based detection using real bands, not RGB-only fake detection.
- Before/after comparison.
- Disaster classification with a transparent confidence/evidence score.
- Affected-area estimate when spatial resolution is trustworthy.
- Severity score with visible methodology.
- Hotspot extraction.
- Interactive map using a **locked mapping stack**.
- Grounded situation report with deterministic offline fallback.
- **Instant Demo Mode** using precomputed results.
- **Live Analyze Mode** as a secondary path.
- Streamlit state/caching so reruns do not destroy results or reload models unnecessarily.
- Upload validation including file type and maximum size.
- Fully offline core demo path.
- Tests for deterministic calculations.
- 2–3 minute rehearsed demo.

### P1 — Strongly recommended

- Critical infrastructure overlay from a local/verified geospatial dataset.
- Methodology / “Show your work” panel.
- Persistent `ESTIMATE` / `PROTOTYPE` labels for derived values.
- Model/data provenance panel.
- Graceful failure states.
- Demo runbook and backup recording.

### P2 — Only after the MVP is stable

- NASA FIRMS live wildfire hotspot overlay.
- OSM/Overpass live infrastructure data.
- Live satellite ingestion.
- Weather/alerts/social monitoring.
- Additional disaster classes.
- Multi-day prediction.

**Rule:** no P2 feature may delay a P0 feature.

---

# 3. Critical Technical Decision: Real Data + Explainable Detection

The original plan's largest risk was leaving the dataset and detection method undefined. NIRVAAN now locks these before detection development starts.

## 3.1 Primary imagery

Use **Sentinel-2 Level-2A surface-reflectance imagery** for the canonical demo events because the workflow needs multispectral bands, not just RGB screenshots.

Required bands for the core spectral pipeline:

### Flood

Primary index:

```text
NDWI = (B03 - B08) / (B03 + B08)
```

Where:

- B03 = Green
- B08 = NIR

If the selected processing path supports it, MNDWI can be evaluated as an optional improvement using SWIR.

### Wildfire

Primary index:

```text
NBR = (B08 - B12) / (B08 + B12)
```

Then:

```text
dNBR = NBR_before - NBR_after
```

The exact thresholds must be calibrated/validated against the selected demo events and stored in configuration. Do **not** silently invent a universal threshold.

## 3.2 Why this approach

- It is explainable to judges.
- It uses actual satellite spectral information.
- It avoids spending the four-day window training a new classifier.
- It provides a defensible “show your work” story.
- It produces masks that downstream area/severity/hotspot logic can consume.

## 3.3 Optional ML classifier

A pretrained/fine-tuned classifier may be added only if a **known usable model, weights, license, and test sample** are available quickly.

It is an enhancement, not a dependency for the core MVP.

---

# 4. Canonical Demo Dataset Contract

Before coding detection, the team must lock:

```text
Flood Event
├── real source
├── before acquisition date
├── after acquisition date
├── before raster
├── after raster
├── AOI / geometry
├── CRS
├── pixel size
└── source/provenance record

Wildfire Event
├── real source
├── before acquisition date
├── after acquisition date
├── before raster
├── after raster
├── AOI / geometry
├── CRS
├── pixel size
└── source/provenance record
```

### Data rules

1. Prefer analysis-ready Sentinel-2 imagery already downloaded before the final demo.
2. Do not depend on network access during judging.
3. Store a provenance file containing source name, product identifier or URL, acquisition dates, processing level, CRS, resolution, and license/usage note when known.
4. Do not fabricate coordinates, dates, source IDs, or event descriptions.
5. Keep the canonical demo dataset small enough to run quickly on a normal laptop.
6. If raw multi-band files are too large, generate and store the exact derived index/mask artifacts used by Instant Demo Mode while preserving provenance.

---

# 5. Detection Architecture

```text
                    REAL SENTINEL-2 DATA
                             │
                 ┌───────────┴───────────┐
                 │                       │
             BEFORE                   AFTER
                 │                       │
                 └───────────┬───────────┘
                             ▼
                    Quality / Alignment
                             │
                 ┌───────────┴───────────┐
                 │                       │
               FLOOD                  WILDFIRE
                 │                       │
            NDWI / MNDWI              NBR / dNBR
                 │                       │
                 └───────────┬───────────┘
                             ▼
                    Evidence Mask
                             │
                             ▼
                    Mask Post-processing
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
         Area Estimate    Hotspots       Severity
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                      Map-ready evidence
                             │
                             ▼
                  Grounded Situation Report
                             │
                             ▼
                       NIRVAAN UI
```

### Evidence result schema

Every analysis should return a structured object similar to:

```json
{
  "event_id": "real-event-id",
  "disaster_type": "flood",
  "detection_method": "NDWI_change",
  "confidence_or_evidence_score": 0.91,
  "affected_area_km2": 12.4,
  "severity": "HIGH",
  "hotspots": [],
  "source": {},
  "limitations": [],
  "is_estimate": true
}
```

### Important terminology

For spectral thresholding, prefer **“evidence score”** or **“detection confidence”** only when the calculation has a defensible interpretation. Do not call a hand-tuned threshold a model probability.

---

# 6. Severity Method

Severity is a **prototype decision-support score**, not an emergency-management standard.

Inputs may include:

- affected-area ratio
- strength of spectral change
- hotspot concentration
- proximity to available critical infrastructure
- detection evidence score

Return:

```text
severity_score: 0–100
severity_band: LOW | MODERATE | HIGH | CRITICAL
factors: [...]
```

Thresholds must be configuration-driven and shown in the methodology panel.

Do not infer casualties, economic loss, structural damage, evacuation requirements, or public-safety orders from satellite imagery alone.

---

# 7. Affected Area

If raster metadata provides trustworthy pixel size:

```text
area_km2 = affected_pixels × pixel_area_m2 / 1,000,000
```

If geospatial resolution is unavailable or invalid:

```text
affected_area_km2 = unavailable
```

Never invent a resolution.

Every displayed area should indicate whether it is an **estimate**.

---

# 8. Hotspot Detection

```text
Evidence mask
    ↓
Connected components / region extraction
    ↓
Remove tiny noise
    ↓
Calculate area + centroid + evidence strength
    ↓
Rank
    ↓
Top-N hotspots
```

Hotspot schema:

```text
hotspot_id
centroid
area_km2 or pixel_area
score
severity
source_event_id
```

Empty masks must return a valid “no significant hotspot detected” state rather than crashing.

---

# 9. Mapping Stack — LOCKED

For the hackathon MVP use:

- **Folium** for map creation.
- **streamlit-folium** for Streamlit embedding.
- GeoJSON for affected polygons/hotspots.

Do not spend Day 1 debating between Folium, PyDeck, Plotly Mapbox, and Leaflet.

Map layers:

1. Event location.
2. Affected region mask/polygons.
3. Hotspots.
4. Severity legend.
5. Optional infrastructure layer.

All coordinates must originate from verified event/raster metadata or derived geometry.

---

# 10. Streamlit State + Performance Contract

The application has two modes.

## Instant Demo Mode — default for judging

```text
Select canonical event
        ↓
Load precomputed result bundle
        ↓
Render result immediately
```

The bundle may contain:

- derived NDWI/NBR products
- masks
- hotspot GeoJSON
- severity result
- metadata
- grounded report input

This is **not fake output** if it was generated from the real canonical dataset and stored as a reproducible artifact.

## Live Analyze Mode — secondary

```text
Select/upload imagery
        ↓
Run preprocessing
        ↓
Run detection
        ↓
Run analysis
```

Live mode is for demonstrating capability, not for risking demo latency.

### State requirements

Use:

- `st.cache_resource` for expensive model/resource initialization.
- `st.cache_data` for reusable deterministic processing where appropriate.
- `st.session_state` for current event, analysis result, mode, and UI progression.

A Streamlit rerun must not erase a completed analysis or trigger expensive inference unnecessarily.

---

# 11. Upload Safety Contract

For user uploads:

- Allow only explicitly supported formats.
- Enforce a maximum file size.
- Enforce reasonable pixel/dimension limits.
- Validate readable content.
- Validate band/channel compatibility.
- Reject malformed input gracefully.

The exact size limit must be configurable and documented.

Example default for prototype image uploads:

```text
MAX_UPLOAD_MB = 25
MAX_IMAGE_PIXELS = configurable
```

Do not assume a 25 MB cap is valid for every raster format; implement the limit appropriate to the actual upload mechanism and document it.

---

# 12. AI Situation Report

The LLM is an **interpretation layer**, not the source of truth.

Input:

```json
{
  "disaster_type": "wildfire",
  "evidence_score": 0.89,
  "severity": "HIGH",
  "affected_area_km2": 8.2,
  "hotspots": [],
  "infrastructure": [],
  "source": {},
  "limitations": []
}
```

The LLM may produce:

- short situation summary
- priority zones
- field-verification recommendations
- monitoring recommendations
- limitations

It must never invent:

- casualties
- confirmed building damage
- evacuation orders
- weather conditions not in the input
- road closures
- emergency resource availability

Every derived number should carry a visible `ESTIMATE` or `PROTOTYPE` label where appropriate.

Offline fallback:

```text
structured evidence
      ↓
deterministic report template
```

---

# 13. Critical Infrastructure Overlay

P1/P2 only after the core map works.

Preferred demo approach:

- local OSM-derived or other verified geospatial export for the canonical AOI.
- hospitals, roads, schools, bridges, settlements where available.

For each hotspot, calculate proximity only when the infrastructure data is present.

Never state “hospital damaged” merely because a hotspot is nearby.

Use wording such as:

> “Hospital within 0.6 km of affected hotspot — field verification recommended.”

---

# 14. “Show Your Work” Methodology Panel

A judge should be able to inspect:

```text
Data source
Acquisition dates
Bands used
Detection method
Threshold/configuration
Pixel resolution
Area formula
Severity factors
Limitations
```

This converts the biggest skepticism risk — “is this just a hardcoded threshold?” — into a transparency feature.

---

# 15. Dashboard UX

### Default flow

```text
1. Select canonical event
2. Instant result appears
3. Detection summary
4. Before/after slider
5. Map + hotspots
6. Severity / affected area
7. AI situation report
8. Show-your-work panel
```

### Staged reveal

The UI should visually follow the same sequence:

```text
DETECT → COMPARE → MAP → ASSESS
```

This acts as both the user experience and the demo narration.

### Persistent transparency labels

Use small labels such as:

- `ESTIMATE`
- `PROTOTYPE SCORE`
- `SATELLITE-DERIVED EVIDENCE`
- `FIELD VERIFICATION REQUIRED`

Do not hide all caveats in a footer.

---

# 16. Reliability Requirements

Before submission, verify:

- canonical demo works with Wi-Fi disabled.
- model/resources are local or pre-cached.
- no runtime download is required.
- LLM failure falls back deterministically.
- malformed uploads do not crash the app.
- missing geospatial metadata does not crash the map.
- Streamlit reruns preserve state.
- Instant Demo Mode has near-zero inference latency.
- all important calculations have deterministic tests.

---

# 17. Repository Architecture

```text
NIRVAAN/
├── app.py
├── requirements.txt
├── README.md
├── DEMO_RUNBOOK.md
├── .env.example
├── .gitignore
│
├── config/
│   └── detection.yaml
│
├── data/
│   ├── catalog.json
│   ├── flood/
│   │   ├── before/
│   │   ├── after/
│   │   ├── derived/
│   │   └── metadata.json
│   └── wildfire/
│       ├── before/
│       ├── after/
│       ├── derived/
│       └── metadata.json
│
├── preprocessing/
│   ├── io.py
│   ├── alignment.py
│   └── quality.py
│
├── detection/
│   ├── spectral.py
│   ├── change.py
│   ├── mask.py
│   └── classifier_adapter.py
│
├── analysis/
│   ├── area.py
│   ├── severity.py
│   ├── hotspots.py
│   └── schemas.py
│
├── mapping/
│   ├── map_builder.py
│   ├── geojson.py
│   └── infrastructure.py
│
├── reports/
│   ├── situation_report.py
│   └── fallback_report.py
│
├── ui/
│   ├── dashboard.py
│   ├── comparison.py
│   ├── map_panel.py
│   └── methodology.py
│
├── demo/
│   ├── bundles/
│   └── prepare_bundle.py
│
├── utils/
│   ├── config.py
│   ├── logging.py
│   └── validation.py
│
└── tests/
    ├── test_data.py
    ├── test_spectral.py
    ├── test_area.py
    ├── test_severity.py
    ├── test_hotspots.py
    └── test_reports.py
```

Keep modules small enough that three developers can work in parallel without repeatedly editing the same files.

---

# 18. 4-Day Delivery Strategy

## DAY 1 — Lock the Evidence Pipeline

### First 2 hours are non-negotiable

```text
1. Select one real flood event.
2. Select one real wildfire event.
3. Verify source/provenance.
4. Verify before/after acquisition dates.
5. Verify Sentinel-2 bands are available.
6. Lock NDWI/NBR-based detection method.
7. Lock Folium + streamlit-folium.
8. Create canonical local demo bundles.
```

Then:

```text
Dataset → loader → preprocessing → spectral detection → mask → result schema
```

### Day 1 milestone

At least one real event must produce a reproducible mask and structured result locally.

---

## DAY 2 — Impact Intelligence

```text
area → severity → hotspots → GeoJSON → map → evidence schema
```

Then implement Instant Demo Mode from the canonical result bundle.

### Day 2 milestone

A real event can go from source imagery to map-ready disaster intelligence without external network dependency.

---

## DAY 3 — Product + AI

```text
Streamlit state/cache
→ dashboard
→ before/after slider
→ map
→ situation report
→ deterministic fallback
→ methodology panel
```

### Day 3 milestone

A judge can complete the entire NIRVAAN journey in under two minutes.

---

## DAY 4 — Freeze + Rehearse

Priority order:

1. reliability
2. instant demo path
3. tests
4. transparency
5. UI polish
6. README/runbook
7. pitch/demo rehearsal

No major new feature after the end-to-end demo is stable.

---

# 19. Team Parallelization — 3 Developers

## Person 1 — Detection / Remote Sensing

Own:

- data verification for spectral bands
- preprocessing
- NDWI/NBR detection
- mask generation
- change detection
- detector tests

Recommended branch:

```text
feature/detection
```

## Person 2 — GIS / Analysis

Own:

- affected area
- severity
- hotspots
- GeoJSON
- Folium map
- optional infrastructure layer

Recommended branch:

```text
feature/gis-analysis
```

## Person 3 — Product / Integration

Own:

- Streamlit dashboard
- session state/cache
- Instant Demo Mode
- AI report + fallback
- methodology panel
- upload validation
- README/runbook

Recommended branch:

```text
feature/product-integration
```

### Shared contract

Person 1 publishes a stable structured detection result.
Person 2 consumes that result and publishes map/impact objects.
Person 3 consumes both through interfaces instead of importing internal implementation details.

---

# 20. Demo Story

Target: **2–3 minutes**.

### 0:00–0:20 — Problem

> Responders need situational awareness before teams can reach the affected area. NIRVAAN turns satellite observations into rapid disaster intelligence.

### 0:20–0:45 — Event

Select the canonical flood event in **Instant Demo Mode**.

### 0:45–1:15 — Detect + Compare

Show:

- disaster type
- evidence score
- before/after slider
- detection mask

### 1:15–1:45 — Map

Reveal:

- affected area
- severity
- top hotspots
- optional infrastructure proximity

### 1:45–2:20 — AI assessment

Show a short, grounded situation report and one concrete verification recommendation.

### 2:20–2:40 — Trust

Open **Show Your Work**:

- source
- bands
- formula
- threshold
- limitations

Close with:

> **NIRVAAN converts satellite observations into actionable disaster intelligence — without pretending uncertainty is certainty.**

---

# 21. Definition of Done

NIRVAAN is submission-ready only when:

- [ ] Real flood dataset locked and provenance documented.
- [ ] Real wildfire dataset locked and provenance documented.
- [ ] Detection method is explicitly NDWI/NBR-based or another documented, validated method.
- [ ] No fake classifier output is presented as real AI.
- [ ] Before/after comparison works.
- [ ] Affected area is traceable to raster resolution.
- [ ] Severity is labeled as prototype scoring.
- [ ] Hotspots render on the map.
- [ ] Folium + streamlit-folium map works.
- [ ] Streamlit state survives reruns.
- [ ] Instant Demo Mode works offline.
- [ ] Live Analyze Mode is optional and cannot block the demo.
- [ ] Upload size/type validation works.
- [ ] AI report is evidence-grounded.
- [ ] Deterministic report fallback works without internet.
- [ ] Show Your Work panel is available.
- [ ] Estimate/prototype labels are visible.
- [ ] Core deterministic tests pass.
- [ ] README and DEMO_RUNBOOK work.
- [ ] 2–3 minute demo is rehearsed twice successfully.

---

# 22. Explicit Non-Goals

Do **not** spend the four-day window building:

- authentication
- database infrastructure
- microservices
- custom model training from scratch
- real-time satellite streaming
- production alerting
- medical/evacuation command systems
- unsupported damage/casualty estimation
- multi-disaster forecasting

The winning strategy is **credible evidence + fast demo + transparent methodology**, not maximum feature count.
