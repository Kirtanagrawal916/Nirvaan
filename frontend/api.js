/* =========================================================
   NIRVAAN API LAYER

   Supports configurable backend URL for local development
   and production deployment (e.g. Vercel + Render).
========================================================= */


const API_BASE_URL =
    (typeof window !== "undefined" && window.NIRVAAN_API_URL)
    ? window.NIRVAAN_API_URL
    : (typeof import.meta !== "undefined" && import.meta.env && import.meta.env.VITE_NIRVAAN_API_URL)
    ? import.meta.env.VITE_NIRVAAN_API_URL
    : "http://localhost:8000/api";


/* =========================================================
   GET LATEST DISASTER
========================================================= */

async function getLatestDisaster() {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/disaster/latest`
            );


        if (!response.ok) {

            throw new Error(
                `API request failed with status ${response.status}`
            );

        }


        const data =
            await response.json();


        return data;

    }

    catch (error) {

        console.log(
            "Backend API not connected or error occurred. Using demo fallback.",
            error
        );


        /*
            Fallback data matching NIRVAAN precomputed / static contract.
        */

        return {

            type: "Flood",

            location: "Emilia-Romagna, Italy",

            confidence: 94.7,

            severity: "LOW",

            affectedArea: "0.0 km²",

            beforeImage: "assets/before.jpg",

            afterImage: "assets/after.jpg",

            data_provenance: "SYNTHETIC_FALLBACK"

        };

    }

}



/* =========================================================
   GET DISASTER HISTORY
========================================================= */

async function getDisasterHistory() {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/disasters`
            );


        if (!response.ok) {

            throw new Error(
                `Unable to fetch disasters with status ${response.status}`
            );

        }


        return await response.json();

    }

    catch (error) {

        console.log(
            "Backend API not connected or error occurred. Using history fallback.",
            error
        );

        const list = (typeof nirvaanData !== "undefined" && nirvaanData.disasters)
            ? nirvaanData.disasters
            : [];
        return list.map(item => Object.assign({ data_provenance: "SYNTHETIC_FALLBACK" }, item));

    }

}



/* =========================================================
   GET SATELLITE IMAGES
========================================================= */

async function getSatelliteImages() {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/satellite/latest`
            );


        if (!response.ok) {

            throw new Error(
                `Satellite API unavailable with status ${response.status}`
            );

        }


        return await response.json();

    }

    catch (error) {

        console.log(
            "Backend API not connected or error occurred. Using satellite fallback.",
            error
        );

        return {

            beforeImage: "assets/before.jpg",

            afterImage: "assets/after.jpg",

            data_provenance: "SYNTHETIC_FALLBACK"

        };

    }

}



/* =========================================================
   GENERATE SITREP (SITUATION REPORT)
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
        if (resData && resData.data) {
            return resData.data;
        }
        return resData;

    } catch (error) {

        console.log("Backend Report API not connected or error occurred. Using client SITREP fallback generator.", error);
        
        const evt = (payload && (payload.event || payload)) || {};
        const evtId = evt.event_id || "flood-emilia-romagna-2023";
        const evtName = evt.name || evt.location || "Emilia-Romagna Flood Event";
        const disasterType = (evt.type || "Flood").toUpperCase();

        const fallbackMarkdown = `# 🛰️ NIRVAAN Situation Report: ${evtName}\n` +
            `**Event Type:** ${disasterType} | **Location:** Emilia-Romagna, Italy | **Severity Index:** 65.0/100 (Moderate) \`[PROTOTYPE]\`\n` +
            `**Source Sensor:** Sentinel-2 Level-2A | **Observation Window:** 2023-05-04 to 2023-05-19\n` +
            `**Data Provenance:** ⚠️ \`SYNTHETIC_FALLBACK\` (Demonstration Mode — This report uses simulated placeholder raster data for testing/demo purposes.)\n\n` +
            `---\n\n` +
            `## 1. Executive Situation Summary\n` +
            `Multispectral satellite observation confirms spectral anomalies consistent with **${disasterType.toLowerCase()}** evidence in the Emilia-Romagna area.\n` +
            `- **Prototype Composite Severity Score:** \`65.0/100\` (\`Moderate\` band).\n` +
            `- **Center Coordinates:** Latitude \`44.5000\`, Longitude \`11.3000\`.\n\n` +
            `## 2. High-Priority Impact Zones\n` +
            `- Identified **1 concentric risk zones** derived from spectral change masks.\n` +
            `- **Estimated Population Exposure:** ~\`12,500\` people \`[ESTIMATE]\`.\n\n` +
            `## 3. Field-Verification Recommendations\n` +
            `- ⚠️ Field verification recommended for SP25 Highway Bridge (0.8 km from hotspot).\n` +
            `- ⚠️ Inspect perimeter access at Bologna Regional Hospital (1.2 km from hotspot).\n\n` +
            `## 4. Responder Recommendations\n` +
            `- [P0] Prioritize ground verification in core affected zone (Severity Index: 65.0/100 - Moderate band).\n` +
            `- [P1] Cross-examine estimated population exposure (~12,500 people) against local district census records.\n\n` +
            `## 5. Data Provenance & Limitations\n` +
            `> [!IMPORTANT]\n` +
            `> **Prototype Disclaimer:** This situation report is generated from satellite spectral indices and local geospatial proxy data.\n`;

        return {
            status: "SUCCESS",
            mode: "CLIENT_FALLBACK",
            data_provenance: "SYNTHETIC_FALLBACK",
            report_markdown: fallbackMarkdown,
            report_json: {
                title: `NIRVAAN Situation Report: ${evtName}`,
                event_id: evtId,
                event_name: evtName,
                disaster_type: disasterType,
                location: "Emilia-Romagna, Italy",
                latitude: 44.5,
                longitude: 11.3,
                generated_at: new Date().toISOString(),
                data_provenance: "SYNTHETIC_FALLBACK",
                observation_window: {
                    sensor: "Sentinel-2 Level-2A",
                    before_date: "2023-05-04",
                    after_date: "2023-05-19"
                },
                severity: { impact_score: 65.0, impact_band: "Moderate" },
                affected_area: { total_risk_zones: 1, affected_area_km2: 14.2 },
                population_exposure: { status: "SUCCESS", estimated_affected_population: 12500 },
                infrastructure_impact: {
                    status: "SUCCESS",
                    impacted_facilities_count: 2,
                    facilities: [
                        { name: "SP25 Highway Bridge", category: "bridge", distance_km: 0.8 },
                        { name: "Bologna Regional Hospital", category: "hospital", distance_km: 1.2 }
                    ],
                    advisories: ["Field verification recommended for SP25 Highway Bridge (0.8 km from hotspot)."]
                },
                recommendations: [
                    "[P0] Prioritize ground verification in core affected zone (Severity Index: 65.0/100 - Moderate band).",
                    "[P1] Cross-examine estimated population exposure (~12,500 people) against local district census records."
                ],
                markdown_report: fallbackMarkdown
            }
        };

    }

}