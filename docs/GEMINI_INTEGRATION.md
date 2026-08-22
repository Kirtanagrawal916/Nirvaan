# NIRVAAN — Gemini AI Visual Analysis & Multimodal Intelligence

**Platform:** NIRVAAN — Satellite Disaster Intelligence Platform  
**Branch:** `detection`  
**Status:** ✅ HARDENED & PRODUCTION READY  

---

## 1. Architectural Role & Demarcation

NIRVAAN explicitly demarcates two distinct analysis pipelines:

```
+------------------------------------------------------------------------------------+
| 1. SATELLITE SPECTRAL ANALYSIS (Copernicus Sentinel-2 Level-2A)                     |
| - Source: Copernicus Data Space Ecosystem (CDSE) STAC & Process API                |
| - Bands: B03 (Green), B08 (NIR), B12 (SWIR-2)                                      |
| - Algorithms: NDWI, NBR, dNBR (Quantitative Physical Surface Reflectance)         |
| - Output: Measured affected area (km²), water masks, burn severity polygons         |
| - Provenance: REAL_SATELLITE_DATA                                                  |
+------------------------------------------------------------------------------------+
                                      vs
+------------------------------------------------------------------------------------+
| 2. GEMINI AI VISUAL ANALYSIS (Google GenAI Multimodal Vision)                      |
| - Source: User-uploaded imagery / aerial disaster scene photos                     |
| - Model: gemini-2.5-flash (with cascading fallback to gemini-2.0-flash / 1.5-flash)|
| - Methods: Visual damage feature detection, hazard interpretation, heuristics      |
| - Output: AI Visual Estimate, AI-Assessed Severity, Priority Responder Actions     |
| - Provenance: USER_UPLOADED_IMAGE_ANALYSIS                                         |
+------------------------------------------------------------------------------------+
```

> [!IMPORTANT]
> **Gemini is NOT the satellite spectral detector.**
> Quantitative flood extents and wildfire burn scars are computed via mathematical index thresholds on calibrated Sentinel-2 Level-2A rasters. Gemini provides **multimodal qualitative visual scene interpretation and advisory recommendations**.

---

## 2. Trigger & Execution Flow

1. **User Action:** User clicks `📁 Upload Image` in the Sentinel-2 Spectral Monitor toolbar (`.sat-btn-group-primary`).
2. **File Picker:** Hidden `<input type="file" id="satImageUploadInput">` triggers local file selection.
3. **JS Handler:** `handleSatImageUpload(event)` reads local preview and dispatches `analyzeUploadedImage(file, context)` in `frontend/api.js`.
4. **HTTP Request:** Dispatches `POST /api/v1/analyze/image` as `multipart/form-data` with `file` and `context`.
5. **Backend Route:** `@app.post("/api/v1/analyze/image")` in `api/main.py` dispatches to `handle_analyze_image_endpoint()` in `api/server.py`.
6. **Gemini Service:** `GeminiService.analyze_disaster_image()` in `services/gemini_service.py` executes validation, system prompts, and calls Google GenAI SDK.
7. **Model Resolution:** `google.genai.Client` queries the cascading model ladder (`gemini-2.5-flash` ➔ `gemini-2.0-flash` ➔ `gemini-1.5-flash`).
8. **UI Rendering:** `refreshSatelliteMonitoringUI()` in `frontend/script.js` renders the scene with AI visual labels and advisory cards.

---

## 3. Security & Secret Protection

- **Key Isolation:** `GEMINI_API_KEY` is loaded exclusively inside backend server workers via `os.getenv("GEMINI_API_KEY")`.
- **Zero Client Exposure:** The API key is never transmitted over HTTP to the frontend, never logged, and never included in JSON error responses.
- **Git Security:** `.env` is strictly git-ignored; `.env.example` contains only an empty template.

---

## 4. Safety Guardrails & Hallucination Defense

- **No Fabricated Casualties:** The prompt and validation strictly prohibit declaring confirmed deaths, injuries, body counts, or municipal evacuation decrees.
- **Controlled Low-Evidence Responses:** If an uninformative or non-disaster scene is uploaded, the service returns `Normal Scene / Insufficient Visual Evidence` with `LOW` severity and baseline confidence.
- **Advisory Labeling:** All recommendations are explicitly presented as `Priority Actions (AI Advisory)`, and derived numbers are labeled `AI Visual Estimate` / `AI/Contextual Estimate`.

---

## 5. Input Validation & Error Handling

- **MIME Types Supported:** `image/jpeg`, `image/png`, `image/webp`, `image/tiff`, `image/bmp`, `image/gif`.
- **File Size Boundaries:** Min 100 Bytes, Max 15 MB.
- **Image Integrity:** Verified using Pillow `Image.verify()`.
- **Error Codes:**
  - `400 EMPTY_IMAGE_PAYLOAD`: Empty upload
  - `400 IMAGE_TOO_SMALL`: Under 100 bytes
  - `413 IMAGE_OVERSIZED`: Exceeds 15 MB
  - `422 CORRUPTED_OR_INVALID_IMAGE`: Corrupted binary
  - `503 GEMINI_API_KEY_MISSING`: Unconfigured key
  - `502 GEMINI_INFERENCE_FAILED`: Model service error

---

## 6. Model Cascade Ladder

| Priority | Model Identifier | SDK Support | Purpose |
| :--- | :--- | :--- | :--- |
| **Primary** | `gemini-2.5-flash` | `google.genai` / REST | High-speed multimodal scene parsing |
| **Fallback 1** | `gemini-2.0-flash` | `google.genai` / REST | High-availability fallback |
| **Fallback 2** | `gemini-1.5-flash` | `google.genai` / REST | Long-context multimodal standard |
| **Fallback 3** | `gemini-1.5-pro` | `google.genai` / REST | Deep reasoning backup |
| **Fallback 4** | `gemini-2.5-pro` | `google.genai` / REST | Enterprise tier fallback |
