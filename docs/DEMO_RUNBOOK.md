# NIRVAAN — Hackathon Stage Demo Runbook

> **Goal:** Zero surprises on stage. Deliver a bulletproof presentation using **INSTANT_DEMO** mode as the rock-solid default path, with a rehearsed **LIVE_ANALYZE** "flex" moment.

---

## 1. One-Line Judge Talking Point (Why Two Modes Exist)

> *"We engineered NIRVAAN with two execution architectures: an **Instant Demo Mode** for zero-latency, fail-safe emergency presentation guarantees, and a **Live Analysis Mode** that runs full multispectral raster change detection in real-time — let us show you both."*

---

## 2. Pre-Stage Readiness Checklist (5 Minutes Before Stage)

1. **Terminal Pre-Check**:
   Run the stage-readiness verification script in PowerShell / CMD:
   ```bash
   python scripts/pre_demo_check.py
   ```
   *Verify that all 7 checks pass and output states `[+] FINAL VERDICT: STAGE READY! ALL CHECKS PASSED.`*

2. **Backend Daemon Status**:
   Confirm FastAPI server is running on `http://localhost:8000`:
   ```bash
   python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
   ```

3. **Frontend Application**:
   Open browser at `http://localhost:5173` (or `http://localhost:5500`).

4. **Hardware & Environment**:
   - Disable laptop sleep / display lock.
   - Confirm Mode Indicator in topbar displays `⚡ INSTANT DEMO [DEFAULT]`.
   - **Offline Safeguard**: INSTANT_DEMO mode requires **zero external internet connectivity**. If conference Wi-Fi drops, NIRVAAN continues working 100% locally.

---

## 3. Recommended Live Demo Script Sequence

```
[0:00 - 0:45] DASHBOARD & FLOOD EVENT (INSTANT_DEMO)
 ├── Open on Dashboard (Emilia-Romagna Flood Event)
 ├── Point out instant zero-latency visual metrics & Sentinel-2 before/after scenes
 └── Point out Provenance Banner & Topbar Mode Indicator ("INSTANT DEMO")

[0:45 - 1:30] ONE-CLICK SITREP GENERATION (THE WOW MOMENT)
 ├── Click "⚡ Generate SITREP" button on Dashboard or Reports tab
 ├── Watch loading spinner (~0.2s) & formatted letterhead SITREP render live
 ├── Highlight Affected Area (km²), Population Exposure, & Priority Responder Advisories
 └── Click "🖨️ Print / Save as PDF" or "📥 Download Markdown" to demonstrate exportability

[1:30 - 2:15] WILDFIRE DISASTER EVENT (INSTANT_DEMO)
 ├── Switch to Rhodes Wildfire Event via Event Selector
 ├── Click "Generate for Selected Event" -> Instant SITREP render for Wildfire dNBR
 └── Point out automatic dNBR burn-severity classification & highway inspection advisories

[2:15 - 3:00] THE "WATCH IT COMPUTE LIVE" FLEX MOMENT (LIVE_ANALYZE)
 ├── Explain: "Now, let us switch from Instant Demo to Live Analysis mode to prove our pipeline computes real spectral indices in real-time."
 ├── Click Topbar Mode Badge (`⚡ INSTANT DEMO`) -> Toggles to `⚡ LIVE ANALYZE [FLEX MODE]`
 ├── Trigger SITREP or Detection -> Watch live numpy array processing (~120-150ms)
 └── Point out live processing duration timestamp in letterhead ("Generated in 124 ms")

[3:00 +] Q&A & DEEP DIVE
 └── Toggle back to `⚡ INSTANT DEMO` for rapid, zero-latency exploration during judge questions.
```

---

## 4. Stage Recovery & On-Stage Fallback Protocol

### Scenario: Live Analysis Mode Times Out or Experiences Latency

- **Presenter's Exact On-Stage Recovery Line**:
  > *"Our real-time pipeline executes full multispectral raster analysis on-the-fly, but to keep our demo seamlessly moving forward, let's switch right back to our instant presentation mode."*

- **Immediate Action**:
  1. Click the Topbar Mode Indicator (`⚡ LIVE ANALYZE`) to immediately toggle back to `⚡ INSTANT DEMO`.
  2. Continue speaking without stopping or attempting to debug code on stage.
  3. All dashboard metrics, maps, and situation reports will immediately return at ~0.28ms latency.

---

## 5. Summary of Architecture Safeguards

| Feature | INSTANT_DEMO Mode | LIVE_ANALYZE Mode |
| :--- | :--- | :--- |
| **Latency** | `~0.28 ms` | `~120 - 150 ms` |
| **Data Source** | Precomputed validated JSON contracts | Full local numpy change detection pipeline |
| **Timeout Protection** | N/A (Instant) | Hard 10.0s thread pool timeout protection |
| **Internet Requirement** | **NONE (100% Offline)** | None (Uses local canonical band files) |
| **Data Provenance** | Explicitly tagged (`SYNTHETIC_FALLBACK`) | Explicitly tagged (`SYNTHETIC_FALLBACK` / `REAL_SATELLITE_DATA`) |
| **Stage Role** | **Primary presentation path** | **Rehearsed flex moment** |
