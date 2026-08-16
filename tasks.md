# NIRVAAN — Antigravity Execution Tasks
## Audit-Improved 4-Day Task Specification

> **Use this file as the executable implementation specification.**
>
> `implementations.md` explains the architecture and product decisions. This file tells Antigravity exactly what to implement.

---

# 0. Global Rules for Antigravity

1. Read `implementations.md` and this file before implementing any task.
2. Work only on the current task unless a dependency is required.
3. Do not invent datasets, coordinates, source IDs, APIs, model weights, confidence values, or real-world claims.
4. Never present a placeholder or hard-coded demo result as a real prediction.
5. Prefer real, sourced Sentinel-2 multispectral evidence for the two canonical events.
6. Core detection must use a documented spectral method (NDWI for flood and NBR/dNBR for wildfire) unless the team explicitly records a justified alternative in the repository.
7. Lock **Folium + streamlit-folium** for the MVP map. Do not debate mapping libraries after TASK-003.
8. Use Streamlit `st.session_state`, `st.cache_resource`, and `st.cache_data` where appropriate.
9. Instant Demo Mode must use precomputed artifacts generated from the real canonical dataset; it must not fabricate output.
10. Live Analyze Mode is secondary and must never be required for the stage demo.
11. Every derived value must be traceable to source evidence and labeled as an estimate/prototype where appropriate.
12. Keep the core demo offline-capable.
13. Never download model weights/data at runtime for the canonical demo.
14. Use environment variables for secrets; never commit secrets.
15. Add deterministic tests for calculations and validation logic.
16. Keep modules separated so three developers can work in parallel with minimal merge conflicts.
17. Do not modify another team's module unless the current task explicitly requires an interface integration.
18. After each task report:
    - files changed
    - implementation summary
    - commands run
    - tests/checks
    - remaining risks
19. If a task cannot be completed honestly with available data/dependencies, stop and report the blocker instead of creating fake output.
20. Every task must leave the repository runnable or clearly state why it cannot yet run.

---

# PHASE 0 — BASELINE + LOCKED DECISIONS

## TASK-001 — Repository Audit

**Priority:** P0  
**Owner:** Shared / Lead  
**Depends on:** none  

### Prompt

```text
Inspect the complete NIRVAAN repository before changing code.

Read implementations.md and tasks.md.

Report:
- current files and architecture
- existing framework
- dependencies
- existing data/models
- existing tests
- existing map/GIS code
- existing configuration/secrets handling
- what can be reused
- what is missing

Do not modify working code.
Do not implement future tasks.
Stop after the audit.
```

### Done when

- Repository state is documented.
- No unrelated changes are made.
- Any existing work is preserved.

---

## TASK-002 — Lock Canonical Real Datasets

**Priority:** P0  
**Owner:** Person 1  
**Depends on:** TASK-001  
**Timebox:** 2–4 hours  

### Goal

Select and locally store one real flood event and one real wildfire event with before/after multispectral imagery suitable for the spectral pipeline.

### Prompt

```text
Implement the canonical NIRVAAN dataset selection and provenance layer.

You must lock:
1. one real flood event
2. one real wildfire event
3. before and after acquisition dates
4. real source/product identifiers or URLs
5. Sentinel-2 Level-2A or another explicitly justified multispectral source
6. required bands for the selected detection method
7. CRS and pixel size

Create:
- data/catalog.json
- one metadata.json per event
- a short DATA_PROVENANCE.md

Do not invent event details.
Do not rely on a live download during the demo.
If a candidate event cannot be verified, reject it and choose another.

At the end report the exact source/provenance for both canonical events and confirm which bands are available.
```

### Acceptance criteria

- Both events are real and source-traceable.
- Before/after data is locally available.
- Required spectral bands are confirmed.
- Provenance is documented.

---

## TASK-003 — Lock Technology and Detection Configuration

**Priority:** P0  
**Owner:** Shared / Lead  
**Depends on:** TASK-002  
**Timebox:** 30–45 min

### Prompt

```text
Create the NIRVAAN detection and application configuration.

Lock:
- Streamlit as UI if no existing UI must be preserved
- Folium + streamlit-folium for maps
- NDWI as the primary flood evidence index
- NBR/dNBR as the primary wildfire evidence index
- configurable thresholds per event/disaster type
- upload size limit
- supported file formats
- minimum hotspot area
- severity bands

Create config/detection.yaml or an equivalent typed configuration module.

Do not hide thresholds inside code.
Do not claim thresholds are universal emergency standards.
```

### Acceptance criteria

- Mapping stack is locked.
- Detection formulas are explicit.
- Thresholds are configuration-driven.
- Config can be loaded by tests and application code.

---

## TASK-004 — Project Structure + Environment

**Priority:** P0  
**Owner:** Person 3  
**Depends on:** TASK-001  

### Prompt

```text
Create or normalize the NIRVAAN project structure from implementations.md.

Create only the modules actually needed for the MVP:
- preprocessing/
- detection/
- analysis/
- mapping/
- reports/
- ui/
- demo/
- utils/
- tests/
- data/
- config/

Add:
- requirements.txt
- .env.example
- .gitignore
- minimal app.py

Preserve existing functionality.
Avoid unnecessary backend/API architecture.
Run a startup check.
```

### Acceptance criteria

- Repository structure exists.
- App starts.
- No secrets are committed.

---

## TASK-005 — Event Schema + Dataset Loader

**Priority:** P0  
**Owner:** Person 1  
**Depends on:** TASK-002  

### Prompt

```text
Implement a typed/validated disaster-event schema and local dataset loader.

Support:
- event_id
- disaster_type
- location_name
- latitude
- longitude
- before_image
- after_image
- before_date
- after_date
- source
- product_id or source_url
- CRS
- resolution_m
- available_bands
- optional AOI

Support flood and wildfire.

The loader must:
- validate metadata
- resolve local files
- reject missing files
- reject unsupported disaster types
- expose provenance

Add tests for valid and invalid events.
```

### Acceptance criteria

- Canonical events load through one interface.
- Invalid metadata fails clearly.
- Provenance is preserved.

---

# PHASE 1 — REMOTE-SENSING PIPELINE

## TASK-006 — Raster/Image Validation + Upload Safety

**Priority:** P0  
**Owner:** Person 1  
**Depends on:** TASK-005  

### Prompt

```text
Implement robust raster/image validation for both canonical data and user uploads.

Validate:
- file exists
- readable raster/image
- supported format
- file size against configurable MAX_UPLOAD_MB
- dimensions/pixel count against configurable limit
- expected bands/channels
- before/after compatibility
- numeric value sanity

Return safe, actionable validation errors.

Do not silently change source data.
Add deterministic tests.
```

### Acceptance criteria

- Oversized/malformed uploads are rejected gracefully.
- Valid Sentinel-2-derived inputs load.
- Tests cover size/type failures.

---

## TASK-007 — Preprocessing and Alignment

**Priority:** P0  
**Owner:** Person 1  
**Depends on:** TASK-006  

### Prompt

```text
Implement deterministic preprocessing for multispectral before/after imagery.

Requirements:
- band selection
- nodata handling
- reflectance/value normalization as appropriate to source
- spatial compatibility check
- resampling only when justified
- preserve CRS/transform/resolution
- produce analysis-ready arrays

Do not invent missing metadata.
If images cannot be safely aligned, return a clear error.
Add tests for shape, metadata preservation, and deterministic output.
```

### Acceptance criteria

- Before/after data is compatible for analysis.
- Metadata remains traceable.

---

## TASK-008 — Flood Spectral Detector (NDWI)

**Priority:** P0  
**Owner:** Person 1  
**Depends on:** TASK-003, TASK-007  

### Prompt

```text
Implement the NIRVAAN flood detector using Sentinel-2 spectral evidence.

Primary formula:
NDWI = (B03 - B08) / (B03 + B08)

Requirements:
1. calculate NDWI safely with divide-by-zero handling
2. apply the configured threshold
3. compare before/after evidence where appropriate
4. create a binary/probability-style evidence mask
5. return summary statistics
6. expose threshold and band configuration
7. label output as spectral evidence, not a trained-model probability

Store or return enough metadata for the methodology panel.
Add synthetic tests for the formula and threshold behavior.
```

### Acceptance criteria

- NDWI calculation is correct.
- Mask is reproducible.
- Threshold is configurable.
- No fake ML probability is claimed.

---

## TASK-009 — Wildfire Spectral Detector (NBR/dNBR)

**Priority:** P0  
**Owner:** Person 1  
**Depends on:** TASK-003, TASK-007  

### Prompt

```text
Implement the NIRVAAN wildfire detector using Sentinel-2 spectral evidence.

Formulas:
NBR = (B08 - B12) / (B08 + B12)
dNBR = NBR_before - NBR_after

Requirements:
- safe division
- before/after calculation
- configurable threshold
- binary evidence mask
- summary statistics
- clear method metadata

Do not call dNBR a trained model prediction.
Add deterministic tests.
```

### Acceptance criteria

- NBR/dNBR works on synthetic data.
- Threshold is configurable.
- Wildfire mask is reproducible.

---

## TASK-010 — Unified Detection Result Contract

**Priority:** P0  
**Owner:** Person 1  
**Depends on:** TASK-008, TASK-009  

### Prompt

```text
Create a common detection result schema consumed by downstream analysis and UI.

Fields should include:
- event_id
- disaster_type
- method
- evidence_score or clearly defined confidence field
- mask reference/data
- before_date
- after_date
- source/provenance
- threshold/configuration
- limitations
- is_estimate

Ensure flood and wildfire detectors produce the same outer schema.
Add schema validation tests.
```

### Acceptance criteria

- Downstream code does not need to know detector internals.
- Both disaster types conform to the same contract.

---

# PHASE 2 — IMPACT ANALYSIS

## TASK-011 — Mask Post-processing

**Priority:** P0  
**Owner:** Person 1  
**Depends on:** TASK-010  

### Prompt

```text
Implement mask cleanup and connected-region extraction.

Include:
- binary normalization
- configurable minimum region size
- removal of tiny isolated noise
- optional hole filling only when justified
- connected components
- stable region IDs

Return image-space and geospatial geometry when metadata permits.
Add synthetic-mask tests.
```

### Acceptance criteria

- Noise filtering is deterministic.
- Region extraction is stable.

---

## TASK-012 — Affected Area Calculation

**Priority:** P0  
**Owner:** Person 2  
**Depends on:** TASK-011  

### Prompt

```text
Implement affected-area calculation.

Formula:
area_km2 = affected_pixels * pixel_area_m2 / 1_000_000

Requirements:
- use trusted raster resolution/transform
- calculate pixel ground area correctly for the supported projection
- never invent resolution
- return unavailable when resolution cannot be trusted
- label result as estimate

Add unit tests with known synthetic rasters.
```

### Acceptance criteria

- Area calculation is numerically correct.
- Missing resolution is safe.

---

## TASK-013 — Prototype Severity Engine

**Priority:** P0  
**Owner:** Person 2  
**Depends on:** TASK-011, TASK-012  

### Prompt

```text
Implement a deterministic prototype severity engine.

Inputs:
- affected-area ratio
- evidence strength
- hotspot concentration
- optional infrastructure proximity

Return:
- severity_score 0–100
- severity_band
- contributing_factors

Use configurable prototype bands.

Do not call this an operational emergency standard.
Add boundary tests.
```

### Acceptance criteria

- Same input always produces same result.
- Factors are visible.
- Thresholds are configurable.

---

## TASK-014 — Hotspot Extraction

**Priority:** P0  
**Owner:** Person 2  
**Depends on:** TASK-011  

### Prompt

```text
Implement hotspot extraction from cleaned disaster regions.

For each hotspot calculate:
- hotspot_id
- centroid
- area
- evidence/impact score
- severity
- source event ID

Rank top N hotspots.
Support empty-mask behavior.
Do not invent names for locations that have no verified place name.
Add synthetic tests.
```

### Acceptance criteria

- Top hotspots are deterministic.
- Empty result is handled safely.

---

## TASK-015 — GeoJSON / Map Data Contract

**Priority:** P0  
**Owner:** Person 2  
**Depends on:** TASK-014  

### Prompt

```text
Create a map-ready geospatial contract.

Convert:
- event point
- affected polygons
- hotspots
- severity

into validated GeoJSON/features.

Requirements:
- preserve CRS expectations
- validate geometries
- reject invalid coordinates
- never invent coordinates
- include properties needed by the UI

Add tests for valid and invalid geometry.
```

### Acceptance criteria

- Map data can be consumed without detector internals.

---

## TASK-016 — Lock and Implement Folium Map

**Priority:** P0  
**Owner:** Person 2  
**Depends on:** TASK-015  

### Prompt

```text
Implement the NIRVAAN interactive map using Folium + streamlit-folium.

Show:
- event location
- affected polygons
- hotspots
- severity legend
- tooltips/popups

Requirements:
- fit bounds to the event/AOI
- accessible legend labels
- missing geospatial metadata must not crash the app
- no invented coordinates
- keep map rendering modular

Do not introduce another map library.
```

### Acceptance criteria

- Map renders inside Streamlit.
- Hotspots and affected regions are visible.
- Missing coordinates fail gracefully.

---

## TASK-017 — Optional Infrastructure Overlay

**Priority:** P1  
**Owner:** Person 2  
**Depends on:** TASK-016  

### Prompt

```text
Add an optional local/verified critical-infrastructure overlay.

Prefer a local geospatial export for the canonical AOI.
Categories may include:
- hospitals
- roads
- schools
- bridges
- settlements

For each hotspot calculate proximity only when data is available.

Never state that nearby infrastructure is damaged.
Use wording such as:
"Hospital within 0.6 km of affected hotspot — field verification recommended."

If reliable infrastructure data is unavailable, skip this feature and report it rather than inventing data.
```

### Acceptance criteria

- Optional layer never blocks core map functionality.

---

# PHASE 3 — DEMO ARTIFACTS + PERFORMANCE

## TASK-018 — Build Canonical Instant Demo Bundles

**Priority:** P0  
**Owner:** Person 3  
**Depends on:** TASK-010, TASK-013, TASK-014, TASK-016  
**Timebox:** 2–3 hours  

### Prompt

```text
Create reproducible Instant Demo Mode artifacts for the canonical flood and wildfire events.

Each bundle must be generated from the real local dataset through the actual detection/analysis pipeline.

Store only what is needed for near-zero-latency rendering, for example:
- metadata
- detection result
- mask/derived image
- hotspots GeoJSON
- severity
- structured report input
- provenance

Create a script such as demo/prepare_bundle.py that regenerates bundles.

Do not hand-write fake results.
Record generation timestamp/tool version where useful.
```

### Acceptance criteria

- Both canonical events have reproducible bundles.
- Bundles can be rendered without running expensive inference.

---

## TASK-019 — Streamlit State and Caching

**Priority:** P0  
**Owner:** Person 3  
**Depends on:** TASK-004  

### Prompt

```text
Implement explicit Streamlit state management.

Use:
- st.session_state for selected event, mode, current result, UI stage
- st.cache_resource for expensive resource/model initialization
- st.cache_data for safe deterministic reusable processing

Requirements:
- reruns must preserve current analysis
- expensive inference must not rerun unnecessarily
- switching events resets only event-specific state
- Instant Demo Mode must remain instant after reruns

Add a small manual verification checklist for rerun behavior.
```

### Acceptance criteria

- Rerun does not wipe completed results.
- Resources are not repeatedly initialized.

---

## TASK-020 — Instant vs Live Analyze Modes

**Priority:** P0  
**Owner:** Person 3  
**Depends on:** TASK-018, TASK-019  

### Prompt

```text
Implement two explicit analysis modes:

1. Instant Demo Mode — default
   - canonical event selector
   - loads precomputed bundle
   - no network dependency
   - near-zero-latency rendering

2. Live Analyze Mode — secondary
   - runs the actual local pipeline on selected/uploaded imagery
   - shows progress/loading state
   - errors gracefully

Make the UI clearly label the selected mode.
The stage demo must never require Live Analyze Mode.
```

### Acceptance criteria

- Instant Mode works offline.
- Live Mode remains functional.
- Modes are not mixed silently.

---

# PHASE 4 — AI REPORTING

## TASK-021 — Structured Assessment Schema

**Priority:** P0  
**Owner:** Person 3  
**Depends on:** TASK-010, TASK-013, TASK-014  

### Prompt

```text
Create a validated situation-assessment schema containing:
- disaster_type
- evidence/confidence
- severity
- affected_area_km2
- hotspots
- infrastructure
- evidence/source
- limitations
- recommended verification actions
- is_estimate

Ensure it serializes to JSON.
Reject unsupported claims/fields where possible.
```

### Acceptance criteria

- Assessment object is validated and serializable.

---

## TASK-022 — Grounded Situation Report + Offline Fallback

**Priority:** P0  
**Owner:** Person 3  
**Depends on:** TASK-021  

### Prompt

```text
Implement NIRVAAN situation-report generation.

If an approved/configured LLM is available:
- provide only validated structured evidence
- request a concise responder-oriented report
- explicitly prohibit unsupported facts

Always implement a deterministic fallback that works offline.

The report may include:
- situation summary
- high-priority zones
- field-verification recommendations
- monitoring recommendations
- limitations

Never invent:
- casualties
- confirmed damage
- evacuation orders
- weather
- road closures
- resource availability

Every derived number must remain labeled as estimate/prototype where appropriate.
Add tests for missing/incomplete evidence.
```

### Acceptance criteria

- LLM is optional.
- Offline fallback is deterministic.
- Unsupported claims are not generated by the fallback.

---

# PHASE 5 — DASHBOARD

## TASK-023 — Dashboard Shell

**Priority:** P0  
**Owner:** Person 3  
**Depends on:** TASK-004  

### Prompt

```text
Build the NIRVAAN Streamlit dashboard shell.

Sections:
1. Header
2. Mode selector
3. Canonical event selector / upload
4. Analyze action
5. Detection summary
6. Before/after comparison
7. Map
8. Severity/impact
9. Hotspots
10. AI assessment
11. Show Your Work

Keep analysis logic out of UI rendering functions.
Use small reusable UI modules.
```

### Acceptance criteria

- Dashboard loads.
- Main sections render without backend results.

---

## TASK-024 — Staged Reveal UX

**Priority:** P0  
**Owner:** Person 3  
**Depends on:** TASK-020, TASK-023  

### Prompt

```text
Implement the staged NIRVAAN analysis flow:

DETECT → COMPARE → MAP → ASSESS

During Live Analyze Mode show progress through these stages.
During Instant Demo Mode reveal the same stages quickly without artificial long waits.

The UI should feel like a coherent analysis story rather than a page of unrelated cards.
```

### Acceptance criteria

- Demo narration maps naturally to UI stages.

---

## TASK-025 — Before/After Slider Comparison

**Priority:** P0  
**Owner:** Person 3  
**Depends on:** TASK-023  

### Prompt

```text
Implement an interactive before/after comparison where practical, preferably a swipe/slider.

Display:
- before image
- after image
- dates
- source
- resolution when known
- optional evidence mask/difference

Do not distort imagery.
Clearly label source and dates.
```

### Acceptance criteria

- Judge can visually compare before and after quickly.

---

## TASK-026 — Severity / Hotspot Presentation

**Priority:** P0  
**Owner:** Person 3  
**Depends on:** TASK-013, TASK-014, TASK-023  

### Prompt

```text
Add concise dashboard panels for:
- severity score
- severity band
- affected area
- hotspot count
- ranked hotspot list

Every derived number must show ESTIMATE or PROTOTYPE where appropriate.
Do not rely on color alone to communicate severity.
```

### Acceptance criteria

- Key impact information is understandable in seconds.

---

## TASK-027 — Show Your Work / Methodology Panel

**Priority:** P1  
**Owner:** Person 3  
**Depends on:** TASK-003, TASK-023  

### Prompt

```text
Add an expandable methodology panel showing:
- data source
- acquisition dates
- bands used
- detection formula
- configured threshold
- pixel resolution
- affected-area formula
- severity factors
- limitations

Make the values come from configuration/metadata rather than hard-coded UI text.
```

### Acceptance criteria

- A judge can inspect how a result was produced.

---

# PHASE 6 — RELIABILITY + TESTING

## TASK-028 — Centralized Error Handling

**Priority:** P0  
**Owner:** Person 3  
**Depends on:** TASK-006, TASK-016, TASK-022, TASK-023  

### Prompt

```text
Implement user-safe error handling for:
- missing files
- malformed uploads
- oversized uploads
- invalid metadata
- incompatible imagery
- invalid bands
- detector failure
- empty masks
- missing geospatial metadata
- invalid geometry
- map rendering failure
- LLM failure

Show concise user messages and log technical details.
Never expose secrets.
```

### Acceptance criteria

- Known failure cases do not crash the app.

---

## TASK-029 — Deterministic Unit Test Suite

**Priority:** P0  
**Owner:** Person 1 + Person 2  
**Depends on:** TASK-008 through TASK-015  

### Prompt

```text
Create/complete deterministic tests for:
- NDWI formula
- NBR/dNBR formula
- threshold behavior
- metadata validation
- image validation
- mask cleanup
- affected area
- severity boundary cases
- hotspot ranking
- GeoJSON validation
- assessment schema
- fallback report generation

Tests must not require internet access.
Use synthetic arrays/geometries where possible.
```

### Acceptance criteria

- Core deterministic tests pass.
- Boundary and empty cases are covered.

---

## TASK-030 — End-to-End Demo Verification

**Priority:** P0  
**Owner:** Shared  
**Depends on:** TASK-020, TASK-024, TASK-026, TASK-028, TASK-029  

### Prompt

```text
Verify the complete NIRVAAN Instant Demo Mode for both canonical events.

Check:
1. app starts
2. event loads
3. source metadata appears
4. detection appears
5. evidence mask appears
6. before/after comparison works
7. severity appears
8. affected area appears or safely reports unavailable
9. hotspots appear
10. Folium map renders
11. AI report appears
12. offline fallback works
13. Streamlit rerun preserves result
14. no network is required

Also verify Live Analyze Mode with at least one valid input if practical.

Record failures instead of hiding them.
```

### Acceptance criteria

- Both canonical demo journeys complete successfully offline.

---

# PHASE 7 — POLISH + OPTIONAL WOW FACTORS

## TASK-031 — Data/Model Transparency

**Priority:** P1  
**Owner:** Person 3  
**Depends on:** TASK-027  

### Prompt

```text
Add visible transparency labels throughout the dashboard.

Show where appropriate:
- SATELLITE-DERIVED EVIDENCE
- ESTIMATE
- PROTOTYPE SCORE
- FIELD VERIFICATION REQUIRED
- source
- acquisition date
- method

Keep the main UI concise; use methodology expansion for detail.
```

### Acceptance criteria

- Derived values are not visually mistaken for verified facts.

---

## TASK-032 — Optional NASA FIRMS Wildfire Overlay

**Priority:** P2  
**Owner:** Person 2  
**Depends on:** TASK-030  

### Prompt

```text
Only if the core demo is already stable, add an optional NASA FIRMS active-fire overlay for the wildfire canonical event.

Requirements:
- it must be clearly labeled as optional live context
- core demo must work if the overlay is unavailable
- do not block startup on network access
- display source and timestamp

If implementation threatens stability, do not implement it.
```

### Acceptance criteria

- Optional overlay never blocks core demo.

---

## TASK-033 — Dashboard Polish

**Priority:** P1  
**Owner:** Person 3  
**Depends on:** TASK-030  

### Prompt

```text
Polish NIRVAAN without changing analysis behavior.

Improve:
- hierarchy
- spacing
- typography
- metric cards
- legends
- empty states
- loading states
- error states
- mobile/desktop readability where practical

Prioritize clarity over animation.
Do not add unrelated features.
```

### Acceptance criteria

- The judge can understand the result within seconds.

---

## TASK-034 — README + Data Provenance + Demo Runbook

**Priority:** P1  
**Owner:** Person 3  
**Depends on:** TASK-030  

### Prompt

```text
Complete documentation using only facts actually present in the repository.

Update/create:
- README.md
- DATA_PROVENANCE.md
- DEMO_RUNBOOK.md

README must include:
- problem
- solution
- architecture
- features
- tech stack
- setup
- commands
- data sources
- detection methods
- limitations
- demo modes

DEMO_RUNBOOK must include:
- exact startup command
- canonical event to select
- expected outputs
- 2–3 minute demo sequence
- offline fallback
- troubleshooting
- final pre-demo checklist
```

### Acceptance criteria

- A teammate can run the demo from the docs.

---

## TASK-035 — Final Submission Freeze

**Priority:** P0  
**Owner:** Shared  
**Depends on:** TASK-030, TASK-033, TASK-034  

### Prompt

```text
Freeze NIRVAAN for hackathon submission.

Do not add new product features.

Perform:
- full test suite
- startup verification
- offline verification
- Instant Demo Mode verification
- secret scan
- dependency review
- unused import/dead-code review
- git diff review
- README/runbook verification
- provenance verification
- final UI smoke test

Confirm that no fake outputs, invented sources, or unsupported claims remain.

Return:
- final test status
- final run command
- known issues
- exact recommended release commit message
```

### Acceptance criteria

- Submission build is reproducible.
- Core demo works offline.
- Known limitations are documented.

---

# 4-DAY EXECUTION SCHEDULE

## DAY 1 — Evidence First

### Morning — P0 gate

```text
TASK-001
↓
TASK-002  ← REAL DATA LOCK
↓
TASK-003  ← METHOD + MAP LOCK
```

**Do not proceed to broad UI work until TASK-002 is successful.**

### Afternoon

```text
TASK-004
TASK-005
TASK-006
TASK-007
TASK-008
TASK-009
TASK-010
```

### Day 1 gate

At least one real event produces a reproducible spectral evidence mask and structured result locally.

---

## DAY 2 — Impact + Map + Instant Demo

```text
TASK-011
TASK-012
TASK-013
TASK-014
TASK-015
TASK-016
TASK-018
TASK-019
TASK-020
```

### Day 2 gate

Both canonical events can produce map-ready impact intelligence offline, and Instant Demo Mode renders without expensive inference.

---

## DAY 3 — Product + AI

```text
TASK-021
TASK-022
TASK-023
TASK-024
TASK-025
TASK-026
TASK-028
TASK-029
```

Then:

```text
TASK-027
TASK-031
```

### Day 3 gate

A judge can complete:

```text
Select event
→ detect
→ compare
→ map
→ severity
→ AI assessment
```

in under two minutes.

---

## DAY 4 — Freeze

```text
TASK-030
TASK-033
TASK-034
TASK-035
```

Only after stability:

```text
TASK-017
TASK-032
```

### Day 4 rule

**No new core feature after the end-to-end demo is stable.**

---

# TEAM PARALLELIZATION

## Person 1 — Remote Sensing / Detection

Branch:

```text
feature/detection
```

Primary tasks:

```text
TASK-002
TASK-005
TASK-006
TASK-007
TASK-008
TASK-009
TASK-010
TASK-011
TASK-029
```

Owns:
- dataset verification
- multispectral preprocessing
- NDWI/NBR
- masks
- detection contracts
- detector tests

---

## Person 2 — GIS / Impact

Branch:

```text
feature/gis-analysis
```

Primary tasks:

```text
TASK-012
TASK-013
TASK-014
TASK-015
TASK-016
TASK-017
TASK-029
TASK-032
```

Owns:
- area
- severity
- hotspots
- GeoJSON
- Folium
- infrastructure
- optional FIRMS layer

---

## Person 3 — Product / Integration

Branch:

```text
feature/product-integration
```

Primary tasks:

```text
TASK-004
TASK-018
TASK-019
TASK-020
TASK-021
TASK-022
TASK-023
TASK-024
TASK-025
TASK-026
TASK-027
TASK-028
TASK-031
TASK-033
TASK-034
```

Owns:
- Streamlit
- state/cache
- demo bundles
- AI report
- UI
- methodology
- error handling
- docs

---

# INTEGRATION CONTRACT BETWEEN TEAM MEMBERS

### Person 1 publishes

```text
DetectionResult
```

containing:

```text
event_id
disaster_type
method
evidence_score
mask
source
limitations
```

### Person 2 publishes

```text
ImpactResult
```

containing:

```text
affected_area
severity
hotspots
geojson
```

### Person 3 consumes both

The UI/report layer must not import private functions from Person 1/2 internals.

Prefer:

```text
shared schemas / public functions
```

This is a merge-conflict prevention rule as well as an architecture rule.

---

# GIT / ANTIGRAVITY EXECUTION RULE

Each developer works only on their feature branch.

Before starting work:

```bash
git checkout main
git pull origin main
git checkout YOUR_BRANCH
git rebase main
```

After a task:

```bash
git status
git add .
git commit -m "feat: implement TASK-XXX"
git push
```

Open a Pull Request only when the task is tested.

Do not directly commit to `main`.

---

# STANDARD ANTIGRAVITY TASK PROMPT

Use this when starting any task:

```text
You are implementing NIRVAAN.

Current task: TASK-XXX from tasks.md.

Read:
- implementations.md
- tasks.md
- all relevant existing code

Before coding:
1. inspect dependencies and interfaces
2. identify files owned by this task
3. preserve other developers' modules

Implement ONLY TASK-XXX and required dependencies.

Rules:
- no invented datasets or APIs
- no fake model results
- no unsupported real-world claims
- keep outputs traceable
- keep the core demo offline-capable
- do not introduce a new framework unless explicitly required
- add/update deterministic tests where relevant

After implementation:
1. run relevant tests
2. run startup/smoke check
3. inspect git diff
4. report files changed
5. report commands run
6. report test results
7. report known risks

Stop after this task. Do not implement future tasks.
```

---

# FINAL DEFINITION OF DONE

NIRVAAN is ready only when:

- [ ] real flood event is locked
- [ ] real wildfire event is locked
- [ ] source/provenance is documented
- [ ] required Sentinel-2 bands are confirmed
- [ ] NDWI flood detector works
- [ ] NBR/dNBR wildfire detector works
- [ ] before/after comparison works
- [ ] affected area is traceable to resolution
- [ ] severity is clearly a prototype score
- [ ] hotspots work
- [ ] Folium map works
- [ ] optional infrastructure does not block core demo
- [ ] Instant Demo Mode works offline
- [ ] Live Analyze Mode is optional
- [ ] Streamlit state/caching is verified
- [ ] upload size/type limits work
- [ ] grounded report works
- [ ] offline report fallback works
- [ ] Show Your Work panel works
- [ ] estimate/prototype labels are visible
- [ ] deterministic tests pass
- [ ] README + provenance + runbook are complete
- [ ] 2–3 minute demo has been rehearsed twice successfully
- [ ] no fake outputs or invented source claims remain
