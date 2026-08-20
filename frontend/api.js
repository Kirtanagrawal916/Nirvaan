/* =========================================================
   NIRVAAN REAL-DATA API LAYER (frontend/api.js)

   Connects directly to backend /api/v1/ REST endpoints.
   No mock/synthetic/fake data fallbacks.
========================================================= */

const API_BASE_URL =
    (typeof window !== "undefined" && window.NIRVAAN_API_URL)
    ? window.NIRVAAN_API_URL
    : (typeof window !== "undefined" && window.VITE_NIRVAAN_API_URL)
    ? window.VITE_NIRVAAN_API_URL
    : "http://localhost:8000/api";


/* =========================================================
   1. GET LATEST DISASTER
========================================================= */
async function getLatestDisaster() {
    try {
        const response = await fetch(`${API_BASE_URL}/v1/disaster/latest`);
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
            error: str(error)
        };
    }
}


/* =========================================================
   2. GET DISASTER HISTORY
========================================================= */
async function getDisasterHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/v1/disasters`);
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
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload || {})
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.message || `Detection job submission failed with status ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error("Error creating detection job:", error);
        throw error;
    }
}

async function getDetectionJobStatus(jobId) {
    try {
        const response = await fetch(`${API_BASE_URL}/v1/detection/${jobId}`);
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
        const response = await fetch(`${API_BASE_URL}/v1/alerts`);
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
        const response = await fetch(`${API_BASE_URL}/v1/risk`);
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
   7. GENERATE SITREP (SITUATION REPORT)
========================================================= */
async function generateSituationReport(payload) {
    try {
        const response = await fetch(`${API_BASE_URL}/v1/report`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload || {})
        });

        if (!response.ok) {
            throw new Error(`Report API request failed with status ${response.status}`);
        }

        const resData = await response.json();
        return resData && resData.data ? resData.data : resData;
    } catch (error) {
        console.warn("Backend Report API not connected or error occurred:", error);
        throw error;
    }
}