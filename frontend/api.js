/* =========================================================
   NIRVAAN REAL-DATA API LAYER (frontend/api.js)

   Connects directly to backend /api/v1/ REST endpoints.
   No mock/synthetic/fake data fallbacks.
   Includes retry backoff for Render cold starts.
========================================================= */

function getApiBaseUrl() {
    let rawUrl = null;

    // 1. Check Vite build-time environment variables
    try {
        if (typeof import.meta !== "undefined" && import.meta.env) {
            rawUrl = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_NIRVAAN_API_URL || import.meta.env.VITE_API_URL;
        }
    } catch (e) {}

    // 2. Check window runtime globals
    if (!rawUrl && typeof window !== "undefined") {
        rawUrl = window.NIRVAAN_API_URL || window.VITE_API_BASE_URL || window.VITE_NIRVAAN_API_URL;
    }

    if (rawUrl) {
        let u = String(rawUrl).trim().replace(/\/$/, "");
        return u.endsWith("/api") ? u : `${u}/api`;
    }

    // 3. If running on local development host (localhost or 127.0.0.1)
    if (typeof window !== "undefined" && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")) {
        return "http://localhost:8000/api";
    }

    // 4. Default Production Render Backend URL (for Vercel deployment: https://nirvaan-one.vercel.app)
    return "https://nirvaan-pd7i.onrender.com/api";
}

const API_BASE_URL = getApiBaseUrl();

function getAuthHeaders() {
    const headers = { "Content-Type": "application/json" };
    const token = typeof localStorage !== "undefined" ? localStorage.getItem("nirvaan_token") : null;
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
}

/**
 * Robust fetch with automatic retry and exponential backoff for backend cold starts.
 */
async function fetchWithRetry(url, options = {}, retries = 2, backoffMs = 1200, timeoutMs = 15000) {
    let attempt = 0;
    while (attempt <= retries) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
        const fetchOptions = {
            ...options,
            signal: controller.signal
        };

        try {
            const response = await fetch(url, fetchOptions);
            clearTimeout(timeoutId);

            // Render free tier returns 502/503/504 while waking up the container
            if (!response.ok && [502, 503, 504].includes(response.status) && attempt < retries) {
                attempt++;
                await new Promise(r => setTimeout(r, backoffMs * Math.pow(1.5, attempt - 1)));
                continue;
            }

            return response;
        } catch (err) {
            clearTimeout(timeoutId);
            if (attempt < retries) {
                attempt++;
                await new Promise(r => setTimeout(r, backoffMs * Math.pow(1.5, attempt - 1)));
            } else {
                throw err;
            }
        }
    }
}

/* =========================================================
   0. HEALTH CHECK
========================================================= */
async function checkBackendHealth() {
    try {
        const res = await fetchWithRetry(`${API_BASE_URL}/v1/health`, { method: "GET" }, 1, 800, 6000);
        return res.ok;
    } catch (e) {
        return false;
    }
}

/* =========================================================
   1. AUTHENTICATION APIs
========================================================= */
async function registerUser(email, password, fullName) {
    const res = await fetchWithRetry(`${API_BASE_URL}/v1/auth/register`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ email, password, full_name: fullName })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error?.message || "Registration failed");
    if (data.access_token) {
        localStorage.setItem("nirvaan_token", data.access_token);
        localStorage.setItem("nirvaan_user", JSON.stringify(data.user));
    }
    return data;
}

async function loginUser(email, password) {
    const res = await fetchWithRetry(`${API_BASE_URL}/v1/auth/login`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error?.message || "Authentication failed");
    if (data.access_token) {
        localStorage.setItem("nirvaan_token", data.access_token);
        localStorage.setItem("nirvaan_user", JSON.stringify(data.user));
    }
    return data;
}

async function getAuthMe() {
    try {
        const res = await fetchWithRetry(`${API_BASE_URL}/v1/auth/me`, {
            headers: getAuthHeaders()
        });
        if (!res.ok) return null;
        return await res.json();
    } catch (e) {
        return null;
    }
}

function logoutUser() {
    if (typeof localStorage !== "undefined") {
        localStorage.removeItem("nirvaan_token");
        localStorage.removeItem("nirvaan_user");
    }
}

/* =========================================================
   2. GET LATEST DISASTER
========================================================= */
async function getLatestDisaster() {
    try {
        const response = await fetchWithRetry(`${API_BASE_URL}/v1/disaster/latest`, { headers: getAuthHeaders() });
        if (!response.ok) {
            throw new Error(`API request failed with status ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.warn("Unable to fetch latest disaster from backend API:", error);
        return {
            type: "None",
            location: "Unable to connect to live API",
            confidence: 0.0,
            severity: "NONE",
            affectedArea: "0.0 km²",
            beforeImage: "assets/before.jpg",
            afterImage: "assets/after.jpg",
            data_provenance: "NO_LIVE_DATA",
            error: String(error)
        };
    }
}

/* =========================================================
   3. GET DISASTER HISTORY (WITH FILTERS & PAGINATION)
========================================================= */
async function getDisasterHistory(params = {}) {
    try {
        const query = new URLSearchParams();
        if (params.limit) query.append("limit", params.limit);
        if (params.offset) query.append("offset", params.offset);
        if (params.type) query.append("type", params.type);
        if (params.severity) query.append("severity", params.severity);
        if (params.source_type) query.append("source_type", params.source_type);

        const url = `${API_BASE_URL}/v1/disasters?${query.toString()}`;
        const response = await fetchWithRetry(url, { headers: getAuthHeaders() });
        if (!response.ok) {
            throw new Error(`Unable to fetch disasters with status ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.warn("Unable to fetch disaster history from backend API:", error);
        return [];
    }
}

/* =========================================================
   4. GET SATELLITE IMAGES / SCENES
========================================================= */
async function getSatelliteImages() {
    try {
        const response = await fetchWithRetry(`${API_BASE_URL}/v1/satellite/latest`);
        if (!response.ok) {
            throw new Error(`Satellite API unavailable with status ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.warn("Unable to fetch latest satellite scenes:", error);
        return {
            beforeImage: "assets/before.jpg",
            afterImage: "assets/after.jpg",
            data_provenance: "NO_LIVE_DATA"
        };
    }
}

async function getSatelliteScenes() {
    try {
        const response = await fetchWithRetry(`${API_BASE_URL}/v1/satellite-scenes`);
        if (!response.ok) {
            throw new Error(`Satellite scenes API unavailable with status ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.warn("Unable to fetch satellite scenes:", error);
        return [];
    }
}

/* =========================================================
   5. ASYNCHRONOUS DETECTION JOBS
========================================================= */
async function createDetectionJob(payload) {
    try {
        const response = await fetchWithRetry(`${API_BASE_URL}/v1/detection`, {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify(payload || {})
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            const msg = errData.error?.message || errData.message || `Detection job submission failed with status ${response.status}`;
            throw new Error(msg);
        }

        return await response.json();
    } catch (error) {
        console.error("Error creating detection job:", error);
        throw error;
    }
}

async function getDetectionJobStatus(jobId) {
    try {
        const response = await fetchWithRetry(`${API_BASE_URL}/v1/detection/${jobId}`, { headers: getAuthHeaders() }, 1, 500, 8000);
        if (!response.ok) {
            throw new Error(`Query job status failed with status ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Error querying detection job '${jobId}':`, error);
        throw error;
    }
}

/* =========================================================
   6. GET ALERTS (REAL DATABASE ALERTS)
========================================================= */
async function getRealAlerts() {
    try {
        const response = await fetchWithRetry(`${API_BASE_URL}/v1/alerts`, { headers: getAuthHeaders() });
        if (!response.ok) {
            throw new Error(`Alerts API failed with status ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.warn("Unable to fetch database alerts:", error);
        return [];
    }
}

/* =========================================================
   7. GET RISK MAP (GEOJSON)
========================================================= */
async function getRiskMapGeoJSON() {
    try {
        const response = await fetchWithRetry(`${API_BASE_URL}/v1/risk`, { headers: getAuthHeaders() });
        if (!response.ok) {
            throw new Error(`Risk map API failed with status ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.warn("Unable to fetch risk map GeoJSON:", error);
        return { type: "FeatureCollection", features: [] };
    }
}

/* =========================================================
   8. SITREP REPORTS APIs
========================================================= */
async function createReport(payload = {}) {
    try {
        const response = await fetchWithRetry(`${API_BASE_URL}/v1/reports`, {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify(payload)
        });
        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.error?.message || `Report creation failed with status ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Error generating report:", error);
        throw error;
    }
}

async function getReports() {
    try {
        const response = await fetchWithRetry(`${API_BASE_URL}/v1/reports`, { headers: getAuthHeaders() });
        if (!response.ok) return [];
        return await response.json();
    } catch (error) {
        console.warn("Error listing reports:", error);
        return [];
    }
}

async function generateSituationReport(payload) {
    return await createReport(payload);
}