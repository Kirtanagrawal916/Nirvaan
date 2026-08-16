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

function loadPage(page) {


    switch(page) {


        case "dashboard":

            showDashboard();

            break;


        case "satellite":

            showSatellite();

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

            showHistory();

            break;


        case "settings":

            showSettings();

            break;


        default:

            showDashboard();

    }

}



/* =========================================================
   DASHBOARD
========================================================= */

function showDashboard() {

    const stats =
        nirvaanData.statistics;


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
                        ${stats.affectedArea}
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


                <div class="satellite-placeholder">

                    <div class="satellite-icon">
                        🛰
                    </div>

                    <h3>
                        Satellite Imagery
                    </h3>

                    <p>
                        Before and after disaster
                        imagery will be loaded from
                        the backend satellite API.
                    </p>

                    <div class="api-status">
                        ● Waiting for Satellite API
                    </div>

                </div>

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
                        FLOOD DETECTED
                    </h2>

                    <p>
                        AI-powered satellite analysis
                    </p>


                    <div class="confidence-row">

                        <span>
                            Confidence Score
                        </span>

                        <strong>
                            94.7%
                        </strong>

                    </div>


                    <div class="progress">

                        <div
                            class="progress-value"
                        ></div>

                    </div>


                    <div class="detail">

                        <span>
                            Severity Level
                        </span>

                        <strong class="high">
                            HIGH
                        </strong>

                    </div>


                    <div class="detail">

                        <span>
                            Affected Area
                        </span>

                        <strong>
                            31.8 km²
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

function showSatellite() {

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
                    onclick="refreshSatellite()"
                >
                    ↻ Refresh
                </button>

            </div>


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
                    Your backend can provide the before
                    and after image URLs through an API.
                </p>

                <div class="api-status">
                    API READY
                </div>

            </div>

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

function showDetection() {

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
                    Confidence: 94.7%
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
                    FLOOD DETECTED
                </h2>

                <p>
                    Surat, Gujarat
                </p>


                <div class="detail">

                    <span>
                        Confidence
                    </span>

                    <strong>
                        94.7%
                    </strong>

                </div>


                <div class="detail">

                    <span>
                        Severity
                    </span>

                    <strong class="high">
                        HIGH
                    </strong>

                </div>


                <div class="detail">

                    <span>
                        Affected Area
                    </span>

                    <strong>
                        31.8 km²
                    </strong>

                </div>


            </div>

        </div>

    `;

}



/* =========================================================
   RISK MAP
========================================================= */

function showRiskMap() {

    pageContent.innerHTML = `

        <h1 class="page-title">
            Risk Map
        </h1>

        <p class="page-subtitle">
            Geographic visualization of disaster risk zones
        </p>


        <div class="panel">

            <div class="panel-header">

                <h2>
                    📍 Disaster Risk Visualization
                </h2>

                <button>
                    Fullscreen
                </button>

            </div>


            <div class="map-container">

                <div class="map-grid"></div>

                <div class="risk-zone zone-green"></div>

                <div class="risk-zone zone-orange"></div>

                <div class="risk-zone zone-red"></div>


                <div class="map-label">
                    📍 Surat, Gujarat
                </div>

            </div>

        </div>

    `;

}



/* =========================================================
   ALERTS
========================================================= */

function showAlerts() {

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

                        <tr>

                            <td>
                                Flood detected
                            </td>

                            <td>
                                Surat, Gujarat
                            </td>

                            <td>
                                <span class="status high">
                                    HIGH
                                </span>
                            </td>

                            <td>
                                10:28 AM
                            </td>

                            <td>
                                Active
                            </td>

                        </tr>


                        <tr>

                            <td>
                                Wildfire detected
                            </td>

                            <td>
                                Ahmedabad
                            </td>

                            <td>
                                <span class="status medium">
                                    MEDIUM
                                </span>
                            </td>

                            <td>
                                09:15 AM
                            </td>

                            <td>
                                Active
                            </td>

                        </tr>


                    </tbody>

                </table>

            </div>

        </div>

    `;

}



/* =========================================================
   REPORTS
========================================================= */

function showReports() {

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
                    detection report for Surat.
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

function showHistory() {

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

                        ${nirvaanData.disasters.map(
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