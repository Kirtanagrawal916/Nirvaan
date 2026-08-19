/* =========================================================
   NIRVAAN FRONTEND
========================================================= */

function updateProvenanceBanner(dataOrProvenance) {
    const banner = document.getElementById("provenanceBanner");
    if (!banner) return;

    let prov = "SYNTHETIC_FALLBACK";
    if (typeof dataOrProvenance === "string") {
        prov = dataOrProvenance;
    } else if (dataOrProvenance && typeof dataOrProvenance === "object") {
        prov = dataOrProvenance.data_provenance ||
               (dataOrProvenance.provenance && dataOrProvenance.provenance.data_provenance) ||
               (dataOrProvenance.event_metadata && dataOrProvenance.event_metadata.data_provenance) ||
               "SYNTHETIC_FALLBACK";
    }

    if (prov === "REAL_SATELLITE_DATA") {
        banner.className = "provenance-banner real-mode";
        banner.innerHTML = `<span class="banner-icon">🛰️</span><span class="banner-text"><strong>REAL SATELLITE DATA</strong> — Processing genuine Sentinel-2 Level-2A surface reflectance imagery.</span>`;
        banner.style.display = "flex";
    } else {
        banner.className = "provenance-banner synthetic-mode";
        banner.innerHTML = `<span class="banner-icon">⚠️</span><span class="banner-text"><strong>DEMO MODE: SYNTHETIC DATA</strong> — This view displays simulated/synthetic placeholder satellite data for demonstration purposes.</span>`;
        banner.style.display = "flex";
    }
}

const pageContent =
    document.getElementById(
        "pageContent"
    );


const navItems =
    document.querySelectorAll(
        ".nav-item"
    );


/* =========================================================
   NAVIGATION
========================================================= */

navItems.forEach(
    item => {

        item.addEventListener(
            "click",
            () => {

                navItems.forEach(
                    nav =>
                        nav.classList.remove(
                            "active"
                        )
                );


                item.classList.add(
                    "active"
                );


                const page =
                    item.dataset.page;


                loadPage(page);

            }
        );

    }
);


/* =========================================================
   INITIAL PAGE
========================================================= */

loadPage("dashboard");



/* =========================================================
   PAGE ROUTER
========================================================= */

async function loadPage(page) {

    switch(page) {

        case "dashboard":
            await showDashboard();
            break;

        case "satellite":
            await showSatellite();
            break;

        case "detection":
            showDetection();
            break;

        case "risk":
            showRiskMap();
            break;

        case "alerts":
            showAlerts();
            break;

        case "reports":
            showReports();
            break;

        case "history":
            await showHistory();
            break;

        case "settings":
            showSettings();
            break;

        default:
            await showDashboard();

    }

}



/* =========================================================
   DASHBOARD
========================================================= */

async function showDashboard() {

    const stats = nirvaanData.statistics;
    const latest = await getLatestDisaster();
    const satellite = await getSatelliteImages();

    updateProvenanceBanner(latest || satellite);

    const disasterTypeUpper = (latest && latest.type) ? latest.type.toUpperCase() + " DETECTED" : "FLOOD DETECTED";
    const confidenceScore = (latest && latest.confidence !== undefined) ? latest.confidence : 94.7;
    const severity = (latest && latest.severity) ? latest.severity.toUpperCase() : "LOW";
    const affectedArea = (latest && latest.affectedArea) ? latest.affectedArea : "0.0 km²";
    const location = (latest && latest.location) ? latest.location : "Emilia-Romagna, Italy";

    let satelliteHtml = `
        <div class="satellite-placeholder">
            <div class="satellite-icon">🛰</div>
            <h3>Satellite Imagery</h3>
            <p>Loaded from backend satellite API.</p>
            <div class="api-status">● API CONNECTED</div>
        </div>
    `;

    if (satellite && satellite.beforeImage && satellite.afterImage) {
        satelliteHtml = `
            <div class="satellite-comparison" style="display: flex; gap: 10px; justify-content: center; align-items: center; padding: 10px 0;">
                <div style="text-align: center;">
                    <span style="font-size: 0.8rem; color: #888;">BEFORE SCENE</span><br>
                    <img src="${satellite.beforeImage}" alt="Before Satellite Scene" style="max-width: 100%; height: 110px; object-fit: cover; border-radius: 6px; margin-top: 4px;">
                </div>
                <div style="text-align: center;">
                    <span style="font-size: 0.8rem; color: #888;">AFTER SCENE</span><br>
                    <img src="${satellite.afterImage}" alt="After Satellite Scene" style="max-width: 100%; height: 110px; object-fit: cover; border-radius: 6px; margin-top: 4px;">
                </div>
            </div>
        `;
    }

    pageContent.innerHTML = `

        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <div>
                <h1 class="page-title" style="margin-bottom: 4px;">
                    Dashboard
                </h1>
                <p class="page-subtitle">
                    Real-time overview of disaster monitoring and analysis
                </p>
            </div>
            <button class="primary-btn" onclick="loadPage('reports'); setTimeout(() => executeSitrepGeneration('${(latest && latest.event_id) ? latest.event_id : "flood-emilia-romagna-2023"}'), 150);" style="padding: 10px 20px; font-weight: 700; background: linear-gradient(135deg, #2563eb, #1d4ed8); border: none; box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4);">
                ⚡ Generate SITREP
            </button>
        </div>


        <section class="stats-grid">


            <div class="stat-card">

                <div class="stat-icon">
                    ⚠
                </div>

                <div>

                    <span class="stat-label">
                        Active Disasters
                    </span>

                    <h2 class="stat-value">
                        ${stats.activeDisasters}
                    </h2>

                    <span class="stat-change red">
                        2 High Risk
                    </span>

                </div>

            </div>



            <div class="stat-card">

                <div class="stat-icon">
                    📍
                </div>

                <div>

                    <span class="stat-label">
                        Affected Area
                    </span>

                    <h2 class="stat-value">
                        ${affectedArea}
                    </h2>

                    <span class="stat-change orange">
                        ↑ 12.6% vs yesterday
                    </span>

                </div>

            </div>



            <div class="stat-card">

                <div class="stat-icon">
                    👥
                </div>

                <div>

                    <span class="stat-label">
                        Population at Risk
                    </span>

                    <h2 class="stat-value">
                        ${stats.populationAtRisk}
                    </h2>

                    <span class="stat-change">
                        ↑ 8.4% vs yesterday
                    </span>

                </div>

            </div>



            <div class="stat-card">

                <div class="stat-icon">
                    ◎
                </div>

                <div>

                    <span class="stat-label">
                        Detection Accuracy
                    </span>

                    <h2 class="stat-value">
                        ${stats.detectionAccuracy}
                    </h2>

                    <span class="stat-change">
                        ↑ 3.2% vs yesterday
                    </span>

                </div>

            </div>


        </section>



        <section class="dashboard-grid">


            <!-- SATELLITE -->

            <div class="panel">

                <div class="panel-header">

                    <h2>
                        ⌁ Satellite Image Comparison
                    </h2>

                    <button
                        onclick="loadPage('satellite')"
                    >
                        View Fullscreen
                    </button>

                </div>

                ${satelliteHtml}

            </div>



            <!-- DETECTION -->

            <div class="panel">

                <div class="panel-header">

                    <h2>
                        ⚠ Disaster Detection
                    </h2>

                </div>


                <div class="detection">

                    <div class="detection-icon">
                        ≋
                    </div>

                    <h2>
                        ${disasterTypeUpper}
                    </h2>

                    <p>
                        AI-powered satellite analysis (${location})
                    </p>


                    <div class="confidence-row">

                        <span>
                            Confidence Score
                        </span>

                        <strong>
                            ${confidenceScore}%
                        </strong>

                    </div>


                    <div class="progress">

                        <div
                            class="progress-value"
                            style="width: ${confidenceScore}%;"
                        ></div>

                    </div>


                    <div class="detail">

                        <span>
                            Severity Level
                        </span>

                        <strong class="${severity.toLowerCase() === 'high' || severity.toLowerCase() === 'extreme' ? 'high' : 'medium'}">
                            ${severity}
                        </strong>

                    </div>


                    <div class="detail">

                        <span>
                            Affected Area
                        </span>

                        <strong>
                            ${affectedArea}
                        </strong>

                    </div>


                    <button
                        class="primary-btn full-btn"
                        onclick="loadPage('detection')"
                    >
                        View Detailed Analysis
                    </button>

                </div>

            </div>


        </section>

    `;

}



/* =========================================================
   SATELLITE MONITOR
========================================================= */

async function showSatellite() {

    const satellite = await getSatelliteImages();
    updateProvenanceBanner(satellite);

    let satelliteContent = `
        <div class="satellite-placeholder">

            <div class="satellite-icon">
                🛰
            </div>

            <h3>
                Waiting for Satellite Data
            </h3>

            <p>
                The frontend is ready to receive
                satellite imagery from your backend.
            </p>

            <div class="api-status">
                API READY
            </div>

        </div>
    `;

    if (satellite && satellite.beforeImage && satellite.afterImage) {
        satelliteContent = `
            <div style="display: flex; gap: 20px; justify-content: center; align-items: center; padding: 20px 0;">
                <div style="text-align: center; flex: 1;">
                    <h3 style="margin-bottom: 10px; color: #888;">BEFORE SCENE</h3>
                    <img src="${satellite.beforeImage}" alt="Before Scene" style="width: 100%; max-height: 320px; object-fit: cover; border-radius: 8px;">
                </div>
                <div style="text-align: center; flex: 1;">
                    <h3 style="margin-bottom: 10px; color: #888;">AFTER SCENE</h3>
                    <img src="${satellite.afterImage}" alt="After Scene" style="width: 100%; max-height: 320px; object-fit: cover; border-radius: 8px;">
                </div>
            </div>
        `;
    }

    pageContent.innerHTML = `

        <h1 class="page-title">
            Satellite Monitor
        </h1>

        <p class="page-subtitle">
            Monitor satellite imagery and detect environmental changes
        </p>


        <div class="panel">

            <div class="panel-header">

                <h2>
                    🛰 Live Satellite Monitoring
                </h2>

                <button
                    onclick="loadPage('satellite')"
                >
                    ↻ Refresh
                </button>

            </div>

            ${satelliteContent}

        </div>



        <br>


        <div class="feature-grid">


            <div class="feature-card">

                <div class="big-icon">
                    🌍
                </div>

                <h3>
                    Earth Observation
                </h3>

                <p>
                    Monitor selected geographical
                    regions using satellite imagery.
                </p>

            </div>


            <div class="feature-card">


                <div class="big-icon">
                    🛰
                </div>

                <h3>
                    Image Acquisition
                </h3>

                <p>
                    Retrieve satellite images through
                    the connected backend API.
                </p>

            </div>


            <div class="feature-card">

                <div class="big-icon">
                    🔄
                </div>

                <h3>
                    Change Detection
                </h3>

                <p>
                    Compare images captured before
                    and after a disaster.
                </p>

            </div>


        </div>

    `;

}



/* =========================================================
   DISASTER DETECTION
========================================================= */

async function showDetection() {

    const latest = await getLatestDisaster();
    updateProvenanceBanner(latest);
    const disasterTypeUpper = (latest && latest.type) ? latest.type.toUpperCase() + " DETECTED" : "FLOOD DETECTED";
    const confidenceScore = (latest && latest.confidence !== undefined) ? latest.confidence : 94.7;
    const severity = (latest && latest.severity) ? latest.severity.toUpperCase() : "LOW";
    const affectedArea = (latest && latest.affectedArea) ? latest.affectedArea : "0.0 km²";
    const location = (latest && latest.location) ? latest.location : "Emilia-Romagna, Italy";

    pageContent.innerHTML = `

        <h1 class="page-title">
            Disaster Detection
        </h1>

        <p class="page-subtitle">
            AI-powered analysis of satellite imagery
        </p>



        <div class="feature-grid">


            <div class="feature-card">

                <div class="big-icon">
                    🌊
                </div>

                <h3>
                    Flood Detection
                </h3>

                <p>
                    Detect abnormal water expansion
                    from satellite imagery.
                </p>

                <br>

                <strong>
                    Confidence: ${confidenceScore}%
                </strong>

            </div>



            <div class="feature-card">

                <div class="big-icon">
                    🔥
                </div>

                <h3>
                    Wildfire Detection
                </h3>

                <p>
                    Identify potential wildfire
                    regions using image analysis.
                </p>

                <br>

                <strong>
                    Model Ready
                </strong>

            </div>



            <div class="feature-card">

                <div class="big-icon">
                    ⛰
                </div>

                <h3>
                    Landslide Detection
                </h3>

                <p>
                    Detect changes in terrain and
                    identify possible landslide zones.
                </p>

                <br>

                <strong>
                    Model Ready
                </strong>

            </div>


        </div>



        <br>



        <div class="panel">

            <div class="panel-header">

                <h2>
                    Latest AI Detection
                </h2>

            </div>


            <div class="detection">

                <div class="detection-icon">
                    ≋
                </div>

                <h2>
                    ${disasterTypeUpper}
                </h2>

                <p>
                    ${location}
                </p>


                <div class="detail">

                    <span>
                        Confidence
                    </span>

                    <strong>
                        ${confidenceScore}%
                    </strong>

                </div>


                <div class="detail">

                    <span>
                        Severity
                    </span>

                    <strong class="${severity.toLowerCase()}">
                        ${severity}
                    </strong>

                </div>


                <div class="detail">

                    <span>
                        Affected Area
                    </span>

                    <strong>
                        ${affectedArea}
                    </strong>

                </div>


            </div>

        </div>

    `;

}



/* =========================================================
   RISK MAP
========================================================= */

async function showRiskMap() {

    const latest = await getLatestDisaster();
    updateProvenanceBanner(latest);
    const location = (latest && latest.location) ? latest.location : "Emilia-Romagna, Italy";

    pageContent.innerHTML = `

        <h1 class="page-title">
            Risk Map
        </h1>

        <p class="page-subtitle">
            Spatial distribution of high-risk disaster zones
        </p>


        <div class="panel">

            <div class="panel-header">

                <h2>
                    Risk Zone Visualization
                </h2>

                <button class="primary-btn">
                    Recalculate Risk
                </button>

            </div>


            <div class="map-container">

                <div class="map-grid"></div>

                <div class="risk-zone zone-green"></div>

                <div class="risk-zone zone-orange"></div>

                <div class="risk-zone zone-red"></div>


                <div class="map-label">
                    📍 ${location}
                </div>

            </div>

        </div>

    `;

}



/* =========================================================
   ALERTS
========================================================= */

async function showAlerts() {

    const disasters = await getDisasterHistory();
    updateProvenanceBanner(disasters && disasters[0]);

    pageContent.innerHTML = `

        <h1 class="page-title">
            Alerts
        </h1>

        <p class="page-subtitle">
            Active disaster warnings and emergency notifications
        </p>


        <div class="panel">

            <div class="table-container">

                <table>

                    <thead>

                        <tr>

                            <th>
                                Alert
                            </th>

                            <th>
                                Location
                            </th>

                            <th>
                                Severity
                            </th>

                            <th>
                                Time
                            </th>

                            <th>
                                Status
                            </th>

                        </tr>

                    </thead>


                    <tbody>

                        ${(disasters || []).map(dis => `

                            <tr>

                                <td>
                                    ${dis.type} detected
                                </td>

                                <td>
                                    ${dis.location}
                                </td>

                                <td>
                                    <span class="status ${(dis.severity || "LOW").toLowerCase()}">
                                        ${dis.severity || "LOW"}
                                    </span>
                                </td>

                                <td>
                                    ${dis.date || "Active"}
                                </td>

                                <td>
                                    ${dis.status || "Active"}
                                </td>

                            </tr>

                        `).join("")}

                    </tbody>

                </table>

            </div>

        </div>

    `;

}



/* =========================================================
   REPORTS
========================================================= */

/* =========================================================
   REPORTS & ONE-CLICK SITREP GENERATION
========================================================= */

let currentSitrepData = null;

async function showReports() {
    const latest = await getLatestDisaster();
    updateProvenanceBanner(latest);

    const activeEventId = (latest && latest.event_id) ? latest.event_id : "flood-emilia-romagna-2023";
    const location = (latest && latest.location) ? latest.location : "Emilia-Romagna, Italy";

    pageContent.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <div>
                <h1 class="page-title" style="margin-bottom: 4px;">Emergency Situation Reports</h1>
                <p class="page-subtitle">One-click responder SITREP generation powered by satellite observation & spatial analytics</p>
            </div>
            <button class="primary-btn" onclick="executeSitrepGeneration('${activeEventId}')" style="padding: 12px 24px; font-size: 15px; font-weight: 700; background: linear-gradient(135deg, #2563eb, #1d4ed8); border: none; box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4);">
                ⚡ Generate Live SITREP
            </button>
        </div>

        <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid #1e293b; border-radius: 10px; padding: 18px; margin-bottom: 25px; display: flex; align-items: center; gap: 20px;">
            <div style="flex: 1;">
                <label style="font-size: 12px; color: #94a3b8; font-weight: 600; text-transform: uppercase;">Active Disaster Event</label>
                <select id="sitrepEventSelect" style="width: 100%; background: #0f172a; color: #f8fafc; border: 1px solid #334155; border-radius: 6px; padding: 10px; margin-top: 5px; font-size: 14px; font-weight: 600;">
                    <option value="flood-emilia-romagna-2023" ${activeEventId.includes('flood') ? 'selected' : ''}>🌊 Emilia-Romagna Flood Event (Italy, May 2023)</option>
                    <option value="wildfire-rhodes-2023" ${activeEventId.includes('wildfire') ? 'selected' : ''}>🔥 Rhodes Wildfire Event (Greece, July 2023)</option>
                </select>
            </div>
            <div style="margin-top: 18px;">
                <button class="primary-btn" onclick="executeSitrepGeneration(document.getElementById('sitrepEventSelect').value)" style="padding: 10px 20px;">
                    Generate for Selected Event
                </button>
            </div>
        </div>

        <div id="sitrepOutputContainer">
            <div class="feature-grid">
                <div class="feature-card" style="text-align: left;">
                    <div class="big-icon">📄</div>
                    <h3>Executive SITREP Summary</h3>
                    <p>Grounded situation report containing severity indices, affected area bounds, and responder advisories.</p>
                    <br>
                    <button class="primary-btn" onclick="executeSitrepGeneration(document.getElementById('sitrepEventSelect').value)">Generate Report</button>
                </div>
                <div class="feature-card" style="text-align: left;">
                    <div class="big-icon">📊</div>
                    <h3>Population & Risk Assessment</h3>
                    <p>Population exposure analysis cross-examined with land-cover classification and proxy data.</p>
                    <br>
                    <button class="primary-btn" onclick="executeSitrepGeneration(document.getElementById('sitrepEventSelect').value)">Generate Report</button>
                </div>
                <div class="feature-card" style="text-align: left;">
                    <div class="big-icon">📈</div>
                    <h3>Infrastructure Proximity Audit</h3>
                    <p>Geospatial analysis of critical health, power, and transit facilities within impact buffer zones.</p>
                    <br>
                    <button class="primary-btn" onclick="executeSitrepGeneration(document.getElementById('sitrepEventSelect').value)">Generate Report</button>
                </div>
            </div>
        </div>
    `;
}

async function executeSitrepGeneration(eventId) {
    const container = document.getElementById("sitrepOutputContainer");
    if (!container) return;

    const selEventId = eventId || "flood-emilia-romagna-2023";

    container.innerHTML = `
        <div class="sitrep-loading">
            <div class="spinner"></div>
            <h3 style="color: #f8fafc; font-size: 18px; margin-bottom: 8px;">⚡ Generating Emergency Situation Report...</h3>
            <p style="color: #94a3b8; font-size: 13px;">Extracting multispectral Sentinel-2 indices & computing composite severity metrics</p>
        </div>
    `;

    try {
        const payload = {
            event_id: selEventId,
            event: {
                event_id: selEventId,
                name: selEventId.includes("wildfire") ? "Rhodes Wildfire Event" : "Emilia-Romagna Flood Event",
                type: selEventId.includes("wildfire") ? "wildfire" : "flood",
                location_name: selEventId.includes("wildfire") ? "Rhodes, Greece" : "Emilia-Romagna, Italy"
            }
        };

        const startTime = performance.now();
        const res = await generateSituationReport(payload);
        const elapsedMs = Math.round(performance.now() - startTime);

        currentSitrepData = res;
        updateProvenanceBanner(res);

        renderSitrepDocument(container, res, elapsedMs);

    } catch (err) {
        console.error("SITREP Generation Error:", err);
        container.innerHTML = `
            <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; border-radius: 10px; padding: 20px; text-align: center; color: #fca5a5;">
                <h3 style="margin-top: 0;">❌ Report Generation Error</h3>
                <p>${err.message || "Failed to communicate with report generation service."}</p>
                <button class="secondary-btn" onclick="showReports()" style="margin-top: 10px;">Retry</button>
            </div>
        `;
    }
}

function renderSitrepDocument(container, reportData, elapsedMs) {
    const rJson = reportData.report_json || {};
    const title = rJson.title || "NIRVAAN Emergency Situation Report";
    const disasterType = (rJson.disaster_type || "DISASTER").toUpperCase();
    const location = rJson.location || "Target Area of Interest";
    const dataProv = reportData.data_provenance || rJson.data_provenance || "SYNTHETIC_FALLBACK";

    const isSynthetic = (dataProv === "SYNTHETIC_FALLBACK");
    const provBadgeClass = isSynthetic ? "pill-sev moderate" : "pill-type";
    const provLabel = isSynthetic ? "⚠️ DEMO MODE: SYNTHETIC DATA" : "🛰️ SATELLITE: SENTINEL-2";

    const sevScore = rJson.severity ? rJson.severity.impact_score : 65.0;
    const sevBand = rJson.severity ? rJson.severity.impact_band : "Moderate";
    const sevClass = (sevBand.toLowerCase() === "high" || sevBand.toLowerCase() === "extreme") ? "high" : "moderate";

    const affectedArea = rJson.affected_area ? rJson.affected_area.affected_area_km2 : 14.2;
    const popEst = (rJson.population_exposure && rJson.population_exposure.estimated_affected_population)
        ? rJson.population_exposure.estimated_affected_population.toLocaleString()
        : "12,500";
    const infraCount = rJson.infrastructure_impact ? rJson.infrastructure_impact.impacted_facilities_count : 2;
    const sensorName = (rJson.observation_window && rJson.observation_window.sensor) ? rJson.observation_window.sensor : "Sentinel-2 Level-2A";

    const formattedDate = new Date(rJson.generated_at || Date.now()).toLocaleString('en-US', {
        dateStyle: 'medium', timeStyle: 'short'
    });

    const recs = rJson.recommendations || [
        "[P0] Prioritize ground verification in core affected zone (Severity Index: 65.0/100 - Moderate band).",
        "[P1] Cross-examine estimated population exposure (~12,500 people) against local district census records."
    ];

    let recsHtml = recs.map(r => `<li>${r}</li>`).join("");

    const markdownText = reportData.report_markdown || rJson.markdown_report || "";

    let simpleHtml = markdownText
        .replace(/^# (.*$)/gim, '<h2 style="color: #60a5fa; margin-top: 15px;">$1</h2>')
        .replace(/^## (.*$)/gim, '<h3 style="color: #93c5fd; margin-top: 15px;">$1</h3>')
        .replace(/^### (.*$)/gim, '<h4 style="color: #cbd5e1; margin-top: 10px;">$1</h4>')
        .replace(/^\- (.*$)/gim, '<li style="margin-left: 15px;">$1</li>')
        .replace(/`([^`]+)`/g, '<code style="background: rgba(30, 41, 59, 0.8); padding: 2px 6px; border-radius: 4px; color: #fde68a;">$1</code>')
        .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
        .replace(/\n\n/g, '<br><br>');

    container.innerHTML = `
        <div id="sitrepDocument" class="sitrep-document">
            <div class="sitrep-letterhead">
                <div class="letterhead-brand">
                    <span class="brand-logo">◒</span>
                    <div>
                        <h2>NIRVAAN EMERGENCY SITREP</h2>
                        <p>Satellite Disaster Monitoring & Intelligence System</p>
                    </div>
                </div>
                <div class="letterhead-meta">
                    <span class="pill ${provBadgeClass}">${provLabel}</span>
                    <span class="meta-date">Generated in ${elapsedMs} ms | ${formattedDate}</span>
                </div>
            </div>

            <div class="sitrep-title-box">
                <h1>${title}</h1>
                <div class="sitrep-pills">
                    <span class="pill pill-type">TYPE: ${disasterType}</span>
                    <span class="pill pill-loc">AOI: ${location}</span>
                    <span class="pill pill-sev ${sevClass}">SEVERITY INDEX: ${sevScore}/100 (${sevBand})</span>
                </div>
            </div>

            <div class="sitrep-metrics-grid">
                <div class="metric-card">
                    <span class="metric-label">Affected Area</span>
                    <span class="metric-val">${affectedArea} km²</span>
                </div>
                <div class="metric-card">
                    <span class="metric-label">Population Exposure</span>
                    <span class="metric-val">~${popEst} people</span>
                </div>
                <div class="metric-card">
                    <span class="metric-label">Impacted Infrastructure</span>
                    <span class="metric-val">${infraCount} facilities</span>
                </div>
                <div class="metric-card">
                    <span class="metric-label">Source Platform</span>
                    <span class="metric-val" style="font-size: 15px; font-weight: 600;">${sensorName}</span>
                </div>
            </div>

            <div class="sitrep-section">
                <h3>📋 Priority Responder Recommendations</h3>
                <ul class="recommendation-list">
                    ${recsHtml}
                </ul>
            </div>

            <div class="sitrep-section">
                <h3>📄 Grounded Situation Narrative</h3>
                <div class="markdown-body">
                    ${simpleHtml}
                </div>
            </div>

            <div class="sitrep-toolbar no-print">
                <button onclick="window.print()" class="primary-btn" style="background: #2563eb; font-weight: 700;">
                    🖨️ Print / Save as PDF
                </button>
                <button onclick="downloadSitrepMarkdown()" class="secondary-btn">
                    📥 Download Markdown
                </button>
                <button onclick="copySitrepToClipboard()" class="secondary-btn" id="copySitrepBtn">
                    📋 Copy to Clipboard
                </button>
            </div>
        </div>
    `;
}

function downloadSitrepMarkdown() {
    if (!currentSitrepData) return;
    const text = currentSitrepData.report_markdown || "";
    const blob = new Blob([text], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `NIRVAAN_SITREP_${Date.now()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function copySitrepToClipboard() {
    if (!currentSitrepData) return;
    const text = currentSitrepData.report_markdown || "";
    navigator.clipboard.writeText(text).then(() => {
        const btn = document.getElementById("copySitrepBtn");
        if (btn) {
            btn.innerHTML = "✅ Copied!";
            setTimeout(() => { btn.innerHTML = "📋 Copy to Clipboard"; }, 2000);
        }
    }).catch(err => {
        alert("Clipboard copy failed: " + err);
    });
}

}



/* =========================================================
   HISTORY
========================================================= */

async function showHistory() {

    const disasters = await getDisasterHistory();
    updateProvenanceBanner(disasters && disasters[0]);

    pageContent.innerHTML = `

        <h1 class="page-title">
            History
        </h1>

        <p class="page-subtitle">
            Previous disaster detections and satellite analyses
        </p>


        <div class="panel">

            <div class="table-container">

                <table>

                    <thead>

                        <tr>

                            <th>
                                ID
                            </th>

                            <th>
                                Disaster
                            </th>

                            <th>
                                Location
                            </th>

                            <th>
                                Confidence
                            </th>

                            <th>
                                Area
                            </th>

                            <th>
                                Status
                            </th>

                        </tr>

                    </thead>


                    <tbody>

                        ${(disasters || []).map(
                            disaster => `

                            <tr>

                                <td>
                                    ${disaster.id}
                                </td>

                                <td>
                                    ${disaster.type}
                                </td>

                                <td>
                                    ${disaster.location}
                                </td>

                                <td>
                                    ${disaster.confidence}%
                                </td>

                                <td>
                                    ${disaster.area}
                                </td>

                                <td>

                                    <span
                                        class="status ${
                                            disaster.status ===
                                            "Resolved"
                                                ? "resolved"
                                                : "high"
                                        }"
                                    >
                                        ${disaster.status}
                                    </span>

                                </td>

                            </tr>

                        `
                        ).join("")}

                    </tbody>

                </table>

            </div>

        </div>

    `;

}




/* =========================================================
   SETTINGS
========================================================= */

function showSettings() {

    pageContent.innerHTML = `

        <h1 class="page-title">
            Settings
        </h1>

        <p class="page-subtitle">
            Configure Nirvaan monitoring preferences
        </p>


        <div class="settings-list">


            <div class="setting-item">

                <div>

                    <strong>
                        Real-time Monitoring
                    </strong>

                    <p>
                        Continuously monitor new satellite data
                    </p>

                </div>

                <div class="toggle"></div>

            </div>



            <div class="setting-item">

                <div>

                    <strong>
                        Disaster Alerts
                    </strong>

                    <p>
                        Receive alerts when disasters are detected
                    </p>

                </div>

                <div class="toggle"></div>

            </div>



            <div class="setting-item">

                <div>

                    <strong>
                        AI Analysis
                    </strong>

                    <p>
                        Automatically analyze incoming imagery
                    </p>

                </div>

                <div class="toggle"></div>

            </div>



            <div class="setting-item">

                <div>

                    <strong>
                        Automatic Reports
                    </strong>

                    <p>
                        Generate reports after disaster detection
                    </p>

                </div>

                <div class="toggle"></div>

            </div>


        </div>

    `;

}



/* =========================================================
   SATELLITE REFRESH
========================================================= */

async function refreshSatellite() {

    const data =
        await getSatelliteImages();


    if (
        data.beforeImage &&
        data.afterImage
    ) {

        console.log(
            "Satellite images received:",
            data
        );

    }

    else {

        alert(
            "Satellite API is not connected yet.\n\n" +
            "Your frontend is ready. " +
            "Connect the backend API to display real satellite imagery."
        );

    }

}