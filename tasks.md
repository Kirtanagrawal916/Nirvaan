# NIRVAAN — Antigravity Implementation Tasks

## Purpose

This file converts the NIRVAAN disaster-monitoring implementation plan into **directly executable tasks for Antigravity**.

Use this file as the implementation source of truth.

### Execution rules for Antigravity

1. Work in the existing repository and preserve existing working code.
2. Complete tasks in the order below unless a dependency requires otherwise.
3. Do not implement future tasks early unless required by the current task.
4. Prefer simple, reliable implementations over unnecessary abstraction.
5. Every task must leave the repository in a runnable state.
6. Do not invent APIs, datasets, credentials, model weights, or external services.
7. If an external dependency is unavailable, create a clean adapter/interface and a local fallback/mock implementation so the demo remains runnable.
8. Never hard-code fake model results as if they were real predictions. Clearly label demo/sample outputs.
9. Add or update tests for important calculations and deterministic logic.
10. Update `README.md` whenever setup, usage, architecture, or functionality changes.
11. After each task, run the relevant tests/lint/build checks and report failures.
12. Do not make unrelated refactors.
13. Keep the application usable offline for the core demo whenever possible.
14. Use environment variables for secrets and document required variables in `.env.example`.
15. At the end of each task, provide:
   - files changed
   - what was implemented
   - commands run
   - test results
   - remaining risks/issues

---

# Phase 0 — Repository Audit

## TASK-001 — Inspect Repository and Create Baseline

### Goal

Understand the current repository before changing code.

### Antigravity prompt

```text
You are implementing NIRVAAN, an AI-powered disaster monitoring prototype using satellite imagery.

First, inspect the entire existing repository.

Do not modify code yet.

Determine:
1. Existing application structure
2. Existing frontend/backend framework
3. Existing Python/Node dependencies
4. Existing model/inference code
5. Existing data or sample images
6. Existing map/GIS code
7. Existing tests
8. Existing environment/config files
9. Existing README documentation
10. Any incomplete or broken functionality

Then report:
- current architecture
- recommended implementation path
- conflicts with the NIRVAAN plan
- files that should be reused
- files that should be created

Do not rewrite working functionality.

Return a concise implementation assessment.
```

### Acceptance criteria

- Repository structure is understood.
- Existing functionality is not modified.
- Implementation risks are identified.
- Recommended next task is clear.

---

# Phase 1 — Project Foundation

## TASK-002 — Create Project Structure

### Goal

Create a clean structure for the NIRVAAN application without breaking existing code.

### Antigravity prompt

```text
Implement the NIRVAAN project structure based on the repository audit.

Create or organize these logical modules where appropriate:

- app.py
- data/
- models/
- preprocessing/
- detection/
- analysis/
- mapping/
- utils/
- tests/

Use the existing framework if one already exists.

Do not duplicate existing functionality.
Do not delete working files.
Do not introduce unnecessary architecture.

Add:
- configuration module
- logging utility
- environment-variable handling
- .env.example
- .gitignore updates where needed

Make sure the project still runs after this task.

Run the existing tests and the application startup check.
```

### Acceptance criteria

- Logical modules exist.
- Existing application still starts.
- Configuration is centralized.
- No secrets are committed.

---

## TASK-003 — Dependency Setup

### Goal

Install and document the minimum dependencies required for the MVP.

### Antigravity prompt

```text
Set up the minimum dependencies required for NIRVAAN.

Target capabilities:
- Python application
- image processing
- numerical processing
- GIS/raster processing
- interactive visualization
- testing

Prefer existing dependencies already present in the repository.

Use:
- numpy
- pandas
- opencv-python
- rasterio
- geopandas
- shapely
- streamlit
- plotly

Only add packages that are actually needed.

Update requirements.txt or the repository's existing dependency file.

Do not add large or unnecessary dependencies.

Verify installation and application startup.
```

### Acceptance criteria

- Dependency file is complete.
- Environment setup is documented.
- Application starts successfully.

---

# Phase 2 — Data Layer

## TASK-004 — Create Disaster Event Data Schema

### Goal

Create a consistent schema for satellite disaster events.

### Antigravity prompt

```text
Create a typed/validated data schema for NIRVAAN disaster events.

The schema must support:
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
- resolution_m
- coordinate_reference_system
- optional metadata

Support at least:
- flood
- wildfire

Create sample metadata JSON files for local demo events.

Do not fabricate real-world claims.
Clearly mark placeholder/demo metadata where actual values are unavailable.

Add validation and tests.
```

### Acceptance criteria

- Event schema exists.
- Invalid metadata is rejected.
- Sample events can be loaded.

---

## TASK-005 — Add Demo Dataset Loader

### Goal

Allow the application to load local satellite demo data reliably.

### Antigravity prompt

```text
Implement a dataset loader for NIRVAAN.

Requirements:
1. Load disaster events from the local data directory.
2. Validate metadata.
3. Resolve before/after image paths.
4. Provide clear errors for missing files.
5. Support flood and wildfire demo events.
6. Return a normalized event object to downstream modules.

Do not download data automatically.
Do not rely on live APIs.

Add unit tests for:
- valid event
- missing image
- invalid metadata
- unsupported disaster type
```

### Acceptance criteria

- Local datasets load through one clean interface.
- Errors are actionable.
- Tests pass.

---

# Phase 3 — Image Preprocessing

## TASK-006 — Implement Image Loader and Validation

### Goal

Build reliable image input handling.

### Antigravity prompt

```text
Implement NIRVAAN image loading and validation.

Support common image/raster formats already appropriate for the project.

Validate:
- file existence
- readable image
- dimensions
- channel count
- numeric range
- before/after compatibility

Return useful metadata with the loaded image.

Handle invalid images gracefully.

Do not silently alter source imagery.

Add tests for valid and invalid inputs.
```

### Acceptance criteria

- Valid images load consistently.
- Invalid inputs produce clear errors.
- Tests pass.

---

## TASK-007 — Implement Image Alignment and Normalization

### Goal

Prepare before/after imagery for comparison.

### Antigravity prompt

```text
Implement preprocessing for NIRVAAN before/after satellite imagery.

Requirements:
1. Resize or resample only when appropriate.
2. Ensure compatible dimensions.
3. Normalize pixel values for model inference.
4. Provide an alignment hook/interface for geospatial registration.
5. Preserve geospatial metadata when the source format provides it.
6. Make preprocessing deterministic.

Do not invent geospatial coordinates.
Do not destroy source metadata.

Add tests for output shapes and deterministic normalization.
```

### Acceptance criteria

- Before/after inputs have compatible dimensions.
- Preprocessing is deterministic.
- Metadata handling is safe.

---

# Phase 4 — Disaster Detection

## TASK-008 — Create Model Adapter Interface

### Goal

Make AI inference replaceable.

### Antigravity prompt

```text
Create a clean model adapter interface for NIRVAAN.

The interface must support:
- image input
- disaster type prediction
- confidence score
- optional segmentation/probability mask

Do not couple the UI to a specific ML framework.

Create:
1. base detector interface
2. real model adapter placeholder if a usable model already exists
3. local deterministic demo adapter only as a clearly labeled fallback

The fallback must not pretend to be a real AI prediction.

Return structured results.

Add tests for schema and error handling.
```

### Acceptance criteria

- UI can consume a standard prediction result.
- Real model integration can be added without changing the UI.
- Demo fallback is clearly labeled.

---

## TASK-009 — Integrate Disaster Classifier

### Goal

Support flood and wildfire classification.

### Antigravity prompt

```text
Integrate the best available existing/pretrained disaster classifier in the repository or selected approved dependency.

Target classes:
- flood
- wildfire
- no_disaster / unknown where supported

Requirements:
- model loading is separate from inference
- model is initialized once
- inference errors are handled
- confidence is returned
- unsupported model outputs are mapped safely

Do not train a new model from scratch unless training code/data already exists and is trivial enough for the current environment.

If no valid model is available, keep the model adapter interface and connect the clearly labeled local demo fallback.

Add an inference smoke test.
```

### Acceptance criteria

- End-to-end inference works for available model/data.
- Model loading does not happen on every request.
- No fake confidence claims are presented as real model results.

---

# Phase 5 — Change Detection

## TASK-010 — Implement Before/After Difference Pipeline

### Goal

Detect changes between pre-event and post-event imagery.

### Antigravity prompt

```text
Implement NIRVAAN before-vs-after change detection.

Pipeline:
1. Validate compatible images.
2. Preprocess consistently.
3. Compute a meaningful pixel/band difference.
4. Normalize the difference.
5. Apply a configurable threshold or model-based mask.
6. Reduce isolated noise where appropriate.
7. Return:
   - difference image
   - binary/probability mask
   - affected pixel count
   - summary statistics

Expose configuration values rather than hard-coding them.

Document that threshold-based change detection is a prototype method and is not automatically equivalent to verified physical damage.

Add deterministic tests.
```

### Acceptance criteria

- Difference image generated.
- Mask generated.
- Noise handling works.
- Results are reproducible.

---

## TASK-011 — Implement Disaster Mask Processing

### Goal

Convert model/change results into clean analysis regions.

### Antigravity prompt

```text
Implement disaster mask post-processing.

Requirements:
- normalize mask format
- remove very small isolated regions
- optionally fill small holes
- compute connected components
- rank regions by area or confidence
- preserve a configurable minimum region size

Return georeferenced or image-coordinate polygons where source metadata allows.

Do not overclaim physical accuracy.

Add tests with synthetic masks.
```

### Acceptance criteria

- Stable masks are produced.
- Connected regions can be extracted.
- Tiny noise can be filtered.

---

# Phase 6 — Severity and Impact

## TASK-012 — Implement Affected Area Calculation

### Goal

Estimate affected area from the mask.

### Antigravity prompt

```text
Implement affected-area estimation for NIRVAAN.

Requirements:
1. Calculate affected pixels.
2. Determine pixel ground area from trusted raster metadata when available.
3. Calculate square meters.
4. Convert to square kilometers.
5. Never invent resolution when metadata is missing.
6. If resolution is unavailable, return a clearly labeled unavailable/estimate state.

Formula:
area_km2 = affected_pixels * pixel_area_m2 / 1_000_000

Add unit tests with known synthetic values.
```

### Acceptance criteria

- Calculation is correct.
- Missing resolution is handled safely.
- Units are explicit.

---

## TASK-013 — Implement Prototype Severity Score

### Goal

Create a consistent prototype severity ranking.

### Antigravity prompt

```text
Implement NIRVAAN's prototype severity scoring.

Inputs may include:
- affected area ratio
- affected region concentration
- model confidence
- proximity to critical infrastructure if available

Return:
- numeric severity score
- severity label
- contributing factors

Default prototype bands:
0–20% LOW
20–50% MODERATE
50–75% HIGH
75%+ CRITICAL

Make thresholds configurable.

Clearly label this as a hackathon prototype scoring system, not an operational emergency standard.

Add unit tests around threshold boundaries.
```

### Acceptance criteria

- Severity score is deterministic.
- Boundary cases are tested.
- UI receives both score and label.

---

## TASK-014 — Implement Hotspot Extraction

### Goal

Identify highest-priority affected regions.

### Antigravity prompt

```text
Implement hotspot extraction from the disaster mask.

Requirements:
- identify connected/high-confidence regions
- calculate region area
- calculate centroid
- calculate impact/confidence score
- rank regions
- return top N hotspots
- support configurable minimum area

Output schema should include:
- hotspot_id
- centroid
- area
- score
- severity

Add tests using synthetic masks.
```

### Acceptance criteria

- Top hotspots are returned.
- Results are sorted consistently.
- Empty-mask behavior is handled.

---

# Phase 7 — Geospatial Map

## TASK-015 — Implement Map Data Layer

### Goal

Convert analysis results into map-ready objects.

### Antigravity prompt

```text
Create a map data layer for NIRVAAN.

Convert:
- event location
- affected regions
- hotspots
- severity
- optional critical infrastructure

into a consistent map schema.

Support GeoJSON or another standard geospatial representation already used by the application.

Do not invent coordinates.

Validate geometries before rendering.
```

### Acceptance criteria

- Map data is structured consistently.
- Invalid geometry is handled.
- Coordinates are traceable to source data.

---

## TASK-016 — Build Interactive Disaster Map

### Goal

Display disaster impact clearly.

### Antigravity prompt

```text
Implement the NIRVAAN interactive disaster map.

The map must display:
- disaster event location
- affected regions
- hotspots
- severity
- legend
- optional infrastructure

Requirements:
- fit map bounds to event
- clear legend
- tooltips for important regions
- visually distinguish severity levels
- avoid excessive visual clutter
- handle missing geospatial data gracefully

Use the project's existing mapping technology where possible.

Add a simple rendering smoke test or manual verification checklist.
```

### Acceptance criteria

- Map renders.
- Affected regions are visible.
- Hotspots can be identified.
- Missing coordinates do not crash the dashboard.

---

# Phase 8 — Critical Infrastructure Context

## TASK-017 — Add Optional Infrastructure Overlay

### Goal

Provide operational context near disaster hotspots.

### Antigravity prompt

```text
Add an optional critical-infrastructure layer.

Support categories such as:
- hospitals
- roads
- bridges
- schools
- settlements

The implementation may use:
- available local demo data
- an existing geospatial dataset
- a clean adapter for a future live source

Do not introduce live API dependency unless credentials/access already exist.

For each hotspot, calculate proximity to available infrastructure when possible.

Label inferred/estimated impact carefully.
```

### Acceptance criteria

- Infrastructure can be displayed.
- Proximity can be calculated when data is available.
- Missing infrastructure data does not break the app.

---

# Phase 9 — AI Response Intelligence

## TASK-018 — Define Structured Disaster Assessment Schema

### Goal

Create a reliable schema for the AI report generator.

### Antigravity prompt

```text
Create a structured disaster-assessment schema.

Required fields:
- disaster_type
- confidence
- severity
- affected_area_km2
- hotspots
- critical_infrastructure
- evidence
- limitations
- recommended_actions

Make the schema serializable to JSON.

Ensure recommendations are generated from available evidence and not unsupported facts.

Add validation.
```

### Acceptance criteria

- Assessment object validates.
- JSON serialization works.
- Missing optional fields are handled.

---

## TASK-019 — Implement AI Situation Report Generator

### Goal

Generate concise, evidence-grounded disaster summaries.

### Antigravity prompt

```text
Implement an AI situation-report generator for NIRVAAN.

Input:
- validated structured disaster assessment

Output:
1. situation summary
2. high-priority zones
3. recommended verification/response actions
4. monitoring recommendations
5. limitations/uncertainty

Important:
- Only use facts present in the structured input.
- Never invent infrastructure damage, casualties, evacuation orders, weather, or other facts.
- Recommendations must be phrased as decision support, not authoritative emergency commands.
- Clearly indicate when values are estimates or prototype outputs.

Use an existing LLM integration only if already configured in the repository.
Otherwise implement a deterministic template-based fallback.

Add tests for empty/incomplete evidence.
```

### Acceptance criteria

- Report is generated from structured evidence.
- Unsupported claims are avoided.
- Fallback works without an LLM service.

---

# Phase 10 — Streamlit Dashboard

## TASK-020 — Build Dashboard Shell

### Goal

Create the main NIRVAAN user interface.

### Antigravity prompt

```text
Build the NIRVAAN dashboard using the existing frontend framework, preferably Streamlit if no frontend framework exists.

Dashboard sections:

1. Header
   NIRVAAN
   AI Satellite Disaster Monitoring

2. Event selector / image upload

3. Analyze button

4. Top metrics:
   - disaster type
   - confidence
   - severity
   - affected area

5. Before/after imagery

6. Interactive map

7. Hotspot list

8. AI assessment

9. Response recommendations

Use reusable UI functions/components.
Keep the dashboard clean and readable.

Do not put analysis logic directly into UI functions.
```

### Acceptance criteria

- Dashboard loads.
- User can select a demo event.
- Main sections are visible.
- UI is separated from analysis logic.

---

## TASK-021 — Add Analysis Workflow to Dashboard

### Goal

Connect all backend modules to the UI.

### Antigravity prompt

```text
Connect the complete NIRVAAN analysis pipeline to the dashboard.

Workflow:

Select event
→ Load before/after imagery
→ Preprocess
→ Run detection
→ Change detection
→ Severity
→ Affected area
→ Hotspots
→ Map
→ AI assessment
→ Recommendations

Requirements:
- show progress/loading state
- cache model initialization where appropriate
- prevent duplicate expensive work
- display actionable errors
- preserve previous successful state when possible

Do not fabricate outputs when analysis fails.
```

### Acceptance criteria

- Full workflow executes from one user action.
- Errors are visible and understandable.
- Results are displayed in all major sections.

---

## TASK-022 — Add Before/After Comparison UI

### Goal

Make the satellite change visually obvious.

### Antigravity prompt

```text
Add a clear before-vs-after comparison component.

Display:
- before image
- after image
- optional difference/mask image
- dates
- source information
- resolution if known

Allow a simple side-by-side layout.

Clearly label all images and avoid implying that "after" means confirmed damage.

Do not distort imagery.
```

### Acceptance criteria

- Before and after are easy to compare.
- Metadata is visible.
- Difference/mask can be inspected.

---

## TASK-023 — Add Severity and Hotspot UI

### Goal

Make risk information immediately understandable.

### Antigravity prompt

```text
Add severity and hotspot visualizations.

Show:
- severity label
- severity score
- affected area
- hotspot count
- ranked hotspot table/list

Each hotspot should show:
- rank
- score
- severity
- area
- location/centroid

Use accessible labels instead of color alone.
```

### Acceptance criteria

- Severity is obvious.
- Hotspots are ranked.
- Important values are visible without opening hidden menus.

---

# Phase 11 — Reliability

## TASK-024 — Add Error Handling

### Goal

Ensure the demo does not crash on normal failures.

### Antigravity prompt

```text
Add robust error handling across the NIRVAAN pipeline.

Handle:
- missing image
- invalid metadata
- model loading failure
- inference failure
- incompatible images
- missing geospatial metadata
- invalid geometries
- unavailable LLM
- empty mask
- map rendering failure

Display user-friendly messages in the dashboard.

Log technical details for debugging.

Never expose secrets in error messages.
```

### Acceptance criteria

- Known failure cases are handled.
- Dashboard remains usable.
- Logs contain actionable diagnostics.

---

## TASK-025 — Add Offline Demo Fallback

### Goal

Make the core demo reliable even if external services fail.

### Antigravity prompt

```text
Implement an offline-safe NIRVAAN demo path.

Requirements:
- bundled/local sample imagery
- local metadata
- cached or local model where available
- deterministic fallback for AI report generation if external LLM is unavailable
- no live API required for the primary demo

Do not fake real-world observations.
Clearly label deterministic/sample fallback outputs.

Add a documented "Demo Mode".
```

### Acceptance criteria

- NIRVAAN can run with no external API dependency for the core demo.
- Demo Mode is clearly identified.
- Failure of optional services does not crash the application.

---

# Phase 12 — Testing

## TASK-026 — Unit Tests for Deterministic Logic

### Goal

Cover important calculations.

### Antigravity prompt

```text
Create or complete unit tests for:
- metadata validation
- image validation
- normalization
- affected area calculation
- severity boundaries
- hotspot extraction
- geometry validation
- response schema validation

Use synthetic inputs where possible.

Do not depend on internet access for unit tests.
```

### Acceptance criteria

- Core deterministic tests pass.
- Edge cases are covered.

---

## TASK-027 — End-to-End Demo Test

### Goal

Verify the full application workflow.

### Antigravity prompt

```text
Create an end-to-end verification procedure for the NIRVAAN demo.

Verify:
1. application starts
2. demo event loads
3. before image appears
4. after image appears
5. inference runs
6. confidence displays
7. change mask appears
8. affected area calculates
9. severity displays
10. hotspots appear
11. map renders
12. AI report appears
13. recommendations appear

Use automated tests where practical and a documented manual checklist for UI-only behavior.

Run the full test suite.
```

### Acceptance criteria

- Full demo path works.
- Any remaining failure is documented.

---

# Phase 13 — Product Polish

## TASK-028 — Improve Dashboard UX

### Goal

Make the application hackathon-demo ready.

### Antigravity prompt

```text
Polish the NIRVAAN dashboard without changing core functionality.

Improve:
- spacing
- typography
- section hierarchy
- metric cards
- loading indicators
- error states
- labels
- legends
- empty states

Keep the interface professional and compact.

Prioritize readability over decorative animation.

Do not add unrelated features.
```

### Acceptance criteria

- Dashboard feels coherent and professional.
- Important insights can be understood quickly.

---

## TASK-029 — Add Data/Model Transparency

### Goal

Make the prototype trustworthy.

### Antigravity prompt

```text
Add transparent metadata to the NIRVAAN UI.

Clearly display where appropriate:
- imagery source
- acquisition dates
- spatial resolution
- model name/version if known
- confidence
- prototype assumptions
- estimated vs observed values
- limitations

Do not overwhelm the main dashboard; use an expandable methodology/about section if helpful.
```

### Acceptance criteria

- Users can understand the source and limitations of results.
- Estimates are not presented as confirmed facts.

---

# Phase 14 — Documentation

## TASK-030 — Complete README

### Goal

Make the repository understandable to judges and teammates.

### Antigravity prompt

```text
Update README.md with:

1. Project overview
2. Problem
3. Solution
4. Key features
5. Architecture
6. Tech stack
7. Repository structure
8. Setup instructions
9. Environment variables
10. Demo instructions
11. Supported disaster types
12. Data/model sources
13. Limitations
14. Future work
15. Hackathon demo flow

Use commands that actually work in the repository.

Do not invent setup steps.
```

### Acceptance criteria

- A new developer can follow README instructions.
- Demo instructions work.

---

## TASK-031 — Create Demo Runbook

### Goal

Make the final demonstration reproducible.

### Antigravity prompt

```text
Create DEMO_RUNBOOK.md for NIRVAAN.

Include:
- exact startup command
- demo dataset/event to use
- expected visible outputs
- 2-minute demo flow
- backup path if model/API fails
- common troubleshooting steps
- final pre-demo checklist

Keep it practical and command-oriented.
```

### Acceptance criteria

- Another teammate can run the demo using only the runbook.

---

# Phase 15 — Final Freeze

## TASK-032 — Production-Style Cleanup for Hackathon Submission

### Goal

Freeze a stable submission build.

### Antigravity prompt

```text
Prepare NIRVAAN for hackathon submission.

Do not add new product features.

Perform:
- dead-code review
- obvious bug fixes
- dependency cleanup
- import cleanup
- startup verification
- test-suite verification
- README verification
- Demo Mode verification
- secret scan
- git diff review

Do not remove necessary experimental code unless it is confirmed unused.

Return:
- final test status
- known issues
- recommended commit message
- final run command
```

### Acceptance criteria

- Application starts cleanly.
- Tests pass or known failures are documented.
- No secrets are committed.
- Demo is reproducible.

---

# 4-Day Execution Order

## DAY 1 — Foundation

```text
TASK-001
↓
TASK-002
↓
TASK-003
↓
TASK-004
↓
TASK-005
↓
TASK-006
↓
TASK-007
```

### Day 1 mandatory milestone

```text
Local satellite event
        ↓
Preprocessing
        ↓
Model interface
        ↓
Initial inference
        ↓
Structured result
```

---

## DAY 2 — AI + GIS Intelligence

```text
TASK-008
↓
TASK-009
↓
TASK-010
↓
TASK-011
↓
TASK-012
↓
TASK-013
↓
TASK-014
↓
TASK-015
↓
TASK-016
```

Optional after the above:

```text
TASK-017
```

### Day 2 mandatory milestone

```text
Disaster
→ Confidence
→ Change mask
→ Severity
→ Affected area
→ Hotspots
→ Map data
```

---

## DAY 3 — Product Integration

```text
TASK-018
↓
TASK-019
↓
TASK-020
↓
TASK-021
↓
TASK-022
↓
TASK-023
↓
TASK-024
```

Optional:

```text
TASK-017
TASK-025
```

### Day 3 mandatory milestone

A judge can execute:

```text
Select Event
→ Analyze
→ See Disaster
→ See Before/After
→ See Severity
→ See Map
→ See AI Assessment
```

---

## DAY 4 — Reliability + Submission

```text
TASK-025
↓
TASK-026
↓
TASK-027
↓
TASK-028
↓
TASK-029
↓
TASK-030
↓
TASK-031
↓
TASK-032
```

### Day 4 rule

**No major new features after TASK-027 unless the full demo is already stable.**

---

# Priority Labels

## P0 — Must Work

- TASK-004
- TASK-005
- TASK-006
- TASK-007
- TASK-008
- TASK-009
- TASK-010
- TASK-012
- TASK-013
- TASK-014
- TASK-016
- TASK-020
- TASK-021
- TASK-022
- TASK-023
- TASK-024
- TASK-025
- TASK-027

## P1 — Strongly Recommended

- TASK-003
- TASK-011
- TASK-015
- TASK-018
- TASK-019
- TASK-026
- TASK-028
- TASK-029
- TASK-030
- TASK-031
- TASK-032

## P2 — Optional

- TASK-017
- live satellite ingestion
- weather integration
- alerts
- social-media monitoring
- additional disaster categories
- multi-day prediction

---

# Final User Journey

The final application should follow this exact experience:

```text
1. User opens NIRVAAN
          ↓
2. Selects Flood Demo Event
          ↓
3. Clicks "Analyze Disaster"
          ↓
4. System preprocesses imagery
          ↓
5. AI detects disaster
          ↓
6. Confidence appears
          ↓
7. Before/after imagery appears
          ↓
8. Change mask appears
          ↓
9. Affected area is calculated
          ↓
10. Severity is calculated
          ↓
11. Hotspots are extracted
          ↓
12. Interactive map is rendered
          ↓
13. Critical infrastructure context appears
          ↓
14. AI situation report is generated
          ↓
15. Priority actions are shown
```

---

# Definition of Done

NIRVAAN is ready for the hackathon when all of the following are true:

- [ ] One flood demo works end-to-end
- [ ] One wildfire demo works or is clearly marked optional
- [ ] Before/after images render
- [ ] Disaster classification works
- [ ] Confidence is shown
- [ ] Change mask works
- [ ] Severity works
- [ ] Affected area works
- [ ] Hotspots work
- [ ] Map works
- [ ] AI report works
- [ ] Recommendations work
- [ ] Offline/demo fallback works
- [ ] Errors are handled
- [ ] Tests pass
- [ ] README is complete
- [ ] Demo runbook is complete
- [ ] No secrets are committed
- [ ] 2–3 minute demo is rehearsed

---

# Suggested Antigravity Master Prompt

Use this prompt when you want Antigravity to take ownership of the complete plan:

```text
You are the lead implementation engineer for NIRVAAN — an AI Satellite Threat & Response Assistant for disaster monitoring.

The repository contains:
- implementations.md
- tasks.md

Use tasks.md as the executable task specification.

Your mission is to implement NIRVAAN as a stable hackathon MVP within the existing repository.

Rules:
1. Inspect the existing repository before modifying code.
2. Follow tasks.md in dependency order.
3. Complete the highest-priority unfinished task first.
4. Reuse existing working code.
5. Avoid unnecessary rewrites.
6. Keep the core demo runnable without external APIs.
7. Never fabricate scientific observations or model outputs.
8. Clearly label estimates, demo data, prototype thresholds, and fallbacks.
9. Add tests for deterministic logic.
10. After every task:
   - run relevant tests
   - verify the application still starts
   - summarize files changed
   - summarize implementation
   - summarize test results
   - identify remaining issues
11. Do not stop at documentation if implementation is still incomplete.
12. Do not implement optional P2 features until all P0 tasks are complete.
13. If a dependency or model is unavailable, implement a clean adapter/fallback and continue.
14. Keep all external credentials in environment variables.
15. Prioritize a stable demo over feature count.

Start by executing TASK-001.

After TASK-001, continue sequentially through the highest-priority unfinished tasks.

Do not ask me to restate the requirements. Use tasks.md and implementations.md as the source of truth.
```
