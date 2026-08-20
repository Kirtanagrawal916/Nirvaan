/* =========================================================
   NIRVAAN REAL-DATA API LAYER (frontend/api.js)

   Connects directly to backend /api/v1/ REST endpoints.
   No mock/synthetic/fake data fallbacks.
========================================================= */

function getApiBaseUrl() {
    if (typeof window !== "undefined") {
        const winUrl = window.NIRVAAN_API_URL || window.VITE_API_BASE_URL || window.VITE_NIRVAAN_API_URL;
        if (winUrl) {
            let u = String(winUrl).trim().replace(/\/$/, "");
            return u.endsWith("/api") ? u : `${u}/api`;
        }

        // 2. If running on local development host (localhost or 127.0.0.1)
        if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
            return "http://localhost:8000/api";
        }
    }

    // 3. Default Production Render Backend URL (for Vercel deployment and non-localhost)
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

/* =========================================================
   0. AUTHENTICATION APIs
========================================================= */
async function registerUser(email, password, fullName) {
    const res = await fetch(`${API_BASE_URL}/v1/auth/register`, {
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
    const res = await fetch(`${API_BASE_URL}/v1/auth/login`, {
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
    const res = await fetch(`${API_BASE_URL}/v1/auth/me`, {
        headers: getAuthHeaders()
    });
    if (!res.ok) return null;
    return await res.json();
}

function logoutUser() {
    if (typeof localStorage !== "undefined") {
        localStorage.removeItem("nirvaan_token");
        localStorage.removeItem("nirvaan_user");
    }
}


/* =========================================================
   1. GET LATEST DISASTER
========================================================= */
async function getLatestDisaster() {
    try {
        const response = await fetch(`${API_BASE_URL}/v1/disaster/latest`, { headers: getAuthHeaders() });
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
   2. GET DISASTER HISTORY (WITH FILTERS & PAGINATION)
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
        const response = await fetch(url, { headers: getAuthHeaders() });
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
   3. GET SATELLITE IMAGES / SCENES
========================================================= */
async function getSatelliteImages() {
    try {
        const response = await fetch(`${API_BASE_URL}/v1/satellite/latest`);
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
        const response = await fetch(`${API_BASE_URL}/v1/satellite-scenes`);
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
   4. ASYNCHRONOUS DETECTION JOBS
========================================================= */
async function createDetectionJob(payload) {
    try {
        const response = await fetch(`${API_BASE_URL}/v1/detection`, {
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
        const response = await fetch(`${API_BASE_URL}/v1/detection/${jobId}`, { headers: getAuthHeaders() });
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
   5. GET ALERTS (REAL DATABASE ALERTS)
========================================================= */
async function getRealAlerts() {
    try {
        const response = await fetch(`${API_BASE_URL}/v1/alerts`, { headers: getAuthHeaders() });
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
   6. GET RISK MAP (GEOJSON)
========================================================= */
async function getRiskMapGeoJSON() {
    try {
        const response = await fetch(`${API_BASE_URL}/v1/risk`, { headers: getAuthHeaders() });
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
   7. SITREP REPORTS APIs
========================================================= */
async function createReport(payload = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}/v1/reports`, {
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
        const response = await fetch(`${API_BASE_URL}/v1/reports`, { headers: getAuthHeaders() });
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