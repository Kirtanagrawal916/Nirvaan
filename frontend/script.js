/* =========================================================
   NIRVAAN FRONTEND
========================================================= */


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

        <h1 class="page-title">
            Dashboard
        </h1>

        <p class="page-subtitle">
            Real-time overview of disaster monitoring and analysis
        </p>


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

async function showReports() {

    const latest = await getLatestDisaster();
    const location = (latest && latest.location) ? latest.location : "Emilia-Romagna, Italy";

    pageContent.innerHTML = `

        <h1 class="page-title">
            Reports
        </h1>

        <p class="page-subtitle">
            Disaster analysis reports generated by Nirvaan
        </p>


        <div class="feature-grid">


            <div class="feature-card">

                <div class="big-icon">
                    📄
                </div>

                <h3>
                    Flood Analysis
                </h3>

                <p>
                    Detailed satellite-based flood
                    detection report for ${location}.
                </p>

                <br>

                <button
                    class="primary-btn"
                >
                    Generate Report
                </button>

            </div>


            <div class="feature-card">

                <div class="big-icon">
                    📊
                </div>

                <h3>
                    Risk Assessment
                </h3>

                <p>
                    Geographic risk assessment
                    based on detected disasters.
                </p>

                <br>

                <button
                    class="primary-btn"
                >
                    Generate Report
                </button>

            </div>


            <div class="feature-card">

                <div class="big-icon">
                    📈
                </div>

                <h3>
                    Historical Trends
                </h3>

                <p>
                    Analyze disaster activity over
                    selected time periods.
                </p>

                <br>

                <button
                    class="primary-btn"
                >
                    Generate Report
                </button>

            </div>


        </div>

    `;

}



/* =========================================================
   HISTORY
========================================================= */

async function showHistory() {

    const disasters = await getDisasterHistory();

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