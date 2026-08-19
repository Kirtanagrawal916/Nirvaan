/* =========================================================
   THEME TOGGLE SYSTEM
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

let currentAnalysisMode = "INSTANT_DEMO";

function toggleAnalysisMode() {
    if (currentAnalysisMode === "INSTANT_DEMO") {
        currentAnalysisMode = "LIVE_ANALYZE";
    } else {
        currentAnalysisMode = "INSTANT_DEMO";
    }
    updateModeIndicatorUI();
}

function updateModeIndicatorUI() {
    const el = document.getElementById("modeIndicator");
    const txt = document.getElementById("modeText");
    const badge = document.getElementById("modeBadge");
    if (!el || !txt || !badge) return;

    if (currentAnalysisMode === "LIVE_ANALYZE") {
        el.className = "mode-indicator live-mode";
        txt.innerHTML = "<strong>LIVE ANALYZE</strong>";
        badge.innerHTML = "FLEX MODE";
    } else {
        el.className = "mode-indicator instant-mode";
        txt.innerHTML = "<strong>INSTANT DEMO</strong>";
        badge.innerHTML = "DEFAULT";
    }
}

function initTheme() {
    const savedTheme = localStorage.getItem("nirvaan_theme") || "dark";
    applyTheme(savedTheme);

    const themeSwitchWrapper = document.getElementById("themeSwitchWrapper");

    if (themeSwitchWrapper) {
        themeSwitchWrapper.addEventListener("click", () => {
            const currentTheme = document.documentElement.getAttribute("data-theme") || "dark";
            const newTheme = currentTheme === "dark" ? "light" : "dark";
            applyTheme(newTheme);
            localStorage.setItem("nirvaan_theme", newTheme);
        });
    }

    const themePillBtns = document.querySelectorAll(".theme-pill-btn");
    themePillBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetTheme = btn.dataset.themeSet;
            if (targetTheme) {
                applyTheme(targetTheme);
                localStorage.setItem("nirvaan_theme", targetTheme);
            }
        });
    });
}

function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    
    const themeText = document.getElementById("themeToggleText");
    if (themeText) {
        themeText.textContent = theme === "dark" ? "Light Mode" : "Dark Mode";
    }

    const themePillBtns = document.querySelectorAll(".theme-pill-btn");
    themePillBtns.forEach(btn => {
        if (btn.dataset.themeSet === theme) {
            btn.classList.add("active");
        } else {
            btn.classList.remove("active");
        }
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initTheme);
} else {
    initTheme();
}


/* =========================================================
   NAVIGATION (SIDEBAR & TOPBAR NAVBAR)
========================================================= */

const pageContent = document.getElementById("pageContent");
const navItems = document.querySelectorAll(".nav-item");
const topbarNavLinks = document.querySelectorAll(".topbar-nav-link, .alert-icon-btn, .topbar-learn-btn");

function navigateToPage(page) {
    // Sync sidebar
    navItems.forEach(nav => {
        if (nav.dataset.page === page) {
            nav.classList.add("active");
        } else {
            nav.classList.remove("active");
        }
    });

    // Sync menu dropdown items
    const menuItems = document.querySelectorAll(".menu-dropdown-item");
    menuItems.forEach(item => {
        if (item.dataset.page === page) {
            item.classList.add("active");
        } else {
            item.classList.remove("active");
        }
    });

    loadPage(page);
}

navItems.forEach(item => {
    item.addEventListener("click", () => {
        const page = item.dataset.page;
        if (page) navigateToPage(page);
    });
});

/* =========================================================
   AUTHENTICATION & LOGIN SYSTEM
========================================================= */

function initAuth() {
    const loginBtn = document.getElementById("loginBtn");
    const menuLoginItem = document.getElementById("menuLoginItem");
    const loginModalOverlay = document.getElementById("loginModalOverlay");
    const closeLoginModalBtn = document.getElementById("closeLoginModalBtn");
    const loginForm = document.getElementById("loginForm");
    const signOutBtn = document.getElementById("signOutBtn");
    const userProfileBadge = document.getElementById("userProfileBadge");
    const userNameText = document.getElementById("userNameText");
    const userRoleText = document.getElementById("userRoleText");
    const togglePasswordBtn = document.getElementById("togglePasswordBtn");
    const loginPassword = document.getElementById("loginPassword");
    const tabSignin = document.getElementById("tabSignin");
    const tabRegister = document.getElementById("tabRegister");
    const nameGroup = document.getElementById("nameGroup");
    const authSubmitText = document.getElementById("authSubmitText");
    const googleSSOBtn = document.getElementById("googleSSOBtn");
    const govSSOBtn = document.getElementById("govSSOBtn");

    let savedUser = localStorage.getItem("nirvaan_user");
    let currentUser = savedUser ? JSON.parse(savedUser) : null;

    function updateAuthUI() {
        if (currentUser && currentUser.isLoggedIn) {
            if (loginBtn) loginBtn.style.display = "none";
            if (signOutBtn) signOutBtn.style.display = "inline-flex";
            if (userProfileBadge) {
                userProfileBadge.classList.add("logged-in");
                if (userNameText) userNameText.textContent = currentUser.name || "Cmdr. Yashi";
                if (userRoleText) userRoleText.textContent = currentUser.role || "Manager";
            }
            const menuLoginText = document.getElementById("menuLoginText");
            if (menuLoginText) menuLoginText.textContent = `Account (${(currentUser.name || 'User').split(' ')[0]})`;
        } else {
            if (loginBtn) loginBtn.style.display = "inline-flex";
            if (signOutBtn) signOutBtn.style.display = "none";
            if (userProfileBadge) userProfileBadge.classList.remove("logged-in");
            const menuLoginText = document.getElementById("menuLoginText");
            if (menuLoginText) menuLoginText.textContent = "Login / Account";
        }
    }

    function openModal() {
        if (loginModalOverlay) loginModalOverlay.classList.add("show");
    }

    function closeModal() {
        if (loginModalOverlay) loginModalOverlay.classList.remove("show");
    }

    if (loginBtn) loginBtn.addEventListener("click", openModal);
    if (menuLoginItem) menuLoginItem.addEventListener("click", openModal);
    if (closeLoginModalBtn) closeLoginModalBtn.addEventListener("click", closeModal);

    if (loginModalOverlay) {
        loginModalOverlay.addEventListener("click", (e) => {
            if (e.target === loginModalOverlay) closeModal();
        });
    }

    if (togglePasswordBtn && loginPassword) {
        togglePasswordBtn.addEventListener("click", () => {
            const type = loginPassword.type === "password" ? "text" : "password";
            loginPassword.type = type;
            togglePasswordBtn.textContent = type === "password" ? "👁️" : "🙈";
        });
    }

    if (tabSignin && tabRegister) {
        tabSignin.addEventListener("click", () => {
            tabSignin.classList.add("active");
            tabRegister.classList.remove("active");
            if (nameGroup) nameGroup.style.display = "none";
            if (authSubmitText) authSubmitText.textContent = "Authenticate & Launch Portal";
        });

        tabRegister.addEventListener("click", () => {
            tabRegister.classList.add("active");
            tabSignin.classList.remove("active");
            if (nameGroup) nameGroup.style.display = "flex";
            if (authSubmitText) authSubmitText.textContent = "Create Account & Register";
        });
    }

    if (loginForm) {
        loginForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const email = document.getElementById("loginEmail").value;
            const role = document.getElementById("loginRole").value;
            const regName = document.getElementById("regName").value;
            
            currentUser = {
                isLoggedIn: true,
                name: regName || email.split("@")[0].replace(".", " ").toUpperCase() || "Cmdr. Yashi",
                email: email,
                role: role
            };

            localStorage.setItem("nirvaan_user", JSON.stringify(currentUser));
            updateAuthUI();
            closeModal();
            alert(`Welcome back, ${currentUser.name}!\nAuthenticated as ${currentUser.role}.`);
        });
    }

    if (signOutBtn) {
        signOutBtn.addEventListener("click", () => {
            currentUser = null;
            localStorage.removeItem("nirvaan_user");
            updateAuthUI();
            alert("Signed out successfully.");
        });
    }

    if (googleSSOBtn) {
        googleSSOBtn.addEventListener("click", () => {
            currentUser = {
                isLoggedIn: true,
                name: "Cmdr. Yashi (Google)",
                email: "yashi@google.com",
                role: "Disaster Response Manager"
            };
            localStorage.setItem("nirvaan_user", JSON.stringify(currentUser));
            updateAuthUI();
            closeModal();
            alert("Google SSO Authentication successful!");
        });
    }

    if (govSSOBtn) {
        govSSOBtn.addEventListener("click", () => {
            currentUser = {
                isLoggedIn: true,
                name: "Cmdr. Yashi (Gov Net)",
                email: "yashi@ndma.gov.in",
                role: "Disaster Response Manager"
            };
            localStorage.setItem("nirvaan_user", JSON.stringify(currentUser));
            updateAuthUI();
            closeModal();
            alert("Government Disaster Network Authentication successful!");
        });
    }

    updateAuthUI();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAuth);
} else {
    initAuth();
}

// 3-Line Menu Dropdown (Settings, About, History, FAQ)
const topbarMenuBtn = document.getElementById("topbarMenuBtn");
const menuDropdown = document.getElementById("menuDropdown");

if (topbarMenuBtn && menuDropdown) {
    topbarMenuBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        menuDropdown.classList.toggle("show");
    });

    document.addEventListener("click", (e) => {
        if (!menuDropdown.contains(e.target) && e.target !== topbarMenuBtn) {
            menuDropdown.classList.remove("show");
        }
    });

    const menuItems = menuDropdown.querySelectorAll(".menu-dropdown-item");
    menuItems.forEach(item => {
        item.addEventListener("click", () => {
            const page = item.dataset.page;
            if (page) {
                navigateToPage(page);
            }
            menuDropdown.classList.remove("show");
        });
    });
}


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

        case "about":
            showAbout();
            break;

        case "faq":
            showFAQ();
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

    const beforeImgPath = (satellite && satellite.beforeImage) ? satellite.beforeImage : "assets/before.jpg";
    const afterImgPath = (satellite && satellite.afterImage) ? satellite.afterImage : "assets/after.jpg";

    let satelliteHtml = `
        <div style="padding: 16px;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                <div class="sat-card-box">
                    <span class="sat-badge normal">PRE-EVENT (BEFORE FLOOD)</span>
                    <img src="${beforeImgPath}" alt="Before Flood Satellite Scene" class="sat-img">
                    <div class="sat-meta">
                        <span>🛰 Sentinel-2 L2A</span>
                        <span>NDWI: 0.12 (Normal Flow)</span>
                    </div>
                </div>

                <div class="sat-card-box">
                    <span class="sat-badge alert">POST-EVENT (INUNDATED FLOOD)</span>
                    <img src="${afterImgPath}" alt="After Flood Satellite Scene" class="sat-img">
                    <div class="sat-meta">
                        <span>🛰 Sentinel-2 L2A</span>
                        <span class="red-text">NDWI: 0.84 (Inundated)</span>
                    </div>
                </div>
            </div>
        </div>
    `;

        <section class="dashboard-section">

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

        </section>

    `;

}



/* =========================================================
   SATELLITE MONITOR
========================================================= */

async function showSatellite() {

    const satellite = await getSatelliteImages();
    updateProvenanceBanner(satellite);

    const beforeImgPath = (satellite && satellite.beforeImage) ? satellite.beforeImage : "assets/before.jpg";
    const afterImgPath = (satellite && satellite.afterImage) ? satellite.afterImage : "assets/after.jpg";

    let satelliteContent = `
        <div style="padding: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <div>
                    <h3 style="font-size: 16px; color: #38bdf8; font-weight: 700;">🛰 Sentinel-2 Multi-Spectral Inundation Comparison</h3>
                    <p style="font-size: 12px; opacity: 0.75;">Pre-event Baseline vs Post-event Overflow Flood Surface (Surat, Gujarat)</p>
                </div>
                <div style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; font-weight: 700; font-size: 11px; padding: 6px 14px; border-radius: 20px; border: 1px solid rgba(56, 189, 248, 0.3);">
                    ● SENTINEL-2 L2A LIVE FEED
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
                <div style="background: #121215; border: 1px solid #27272a; border-radius: 14px; padding: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <span class="sat-badge normal">BEFORE FLOOD (PRE-EVENT)</span>
                        <span style="font-size: 11px; opacity: 0.7;">Pass: 12 Aug 2026</span>
                    </div>
                    <img src="${beforeImgPath}" alt="Before Flood Satellite Scene" style="width: 100%; height: 320px; object-fit: cover; border-radius: 10px; border: 1px solid #27272a;">
                    <div style="display: flex; justify-content: space-between; font-size: 12px; opacity: 0.8; margin-top: 12px;">
                        <span>Terrain: Normal River Basin & Town</span>
                        <span>NDWI Score: 0.12</span>
                    </div>
                </div>

                <div style="background: #121215; border: 1px solid #ef4444; border-radius: 14px; padding: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <span class="sat-badge alert">AFTER FLOOD (POST-EVENT INUNDATED)</span>
                        <span style="font-size: 11px; color: #ef4444; font-weight: 600;">Pass: 19 Aug 2026</span>
                    </div>
                    <img src="${afterImgPath}" alt="After Flood Satellite Scene" style="width: 100%; height: 320px; object-fit: cover; border-radius: 10px; border: 1px solid #ef4444;">
                    <div style="display: flex; justify-content: space-between; font-size: 12px; margin-top: 12px;">
                        <span style="color: #ef4444; font-weight: 600;">Severe Inundation Over Banks</span>
                        <span style="color: #ef4444; font-weight: 600;">NDWI Score: 0.84</span>
                    </div>
                </div>
            </div>
        </div>
    `;

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


/* =========================================================
   ABOUT PAGE
========================================================= */

function showAbout() {
    pageContent.innerHTML = `
        <h1 class="page-title">About Nirvaan</h1>
        <p class="page-subtitle">Satellite-Based AI Disaster Monitoring & Rapid Intelligence Platform</p>

        <div class="panel" style="padding: 28px; line-height: 1.8;">
            <h2 style="margin-bottom: 12px; color: #38bdf8; font-size: 18px;">Platform Overview</h2>
            <p style="margin-bottom: 20px; font-size: 14px;">
                Nirvaan leverages multi-spectral satellite imagery (Sentinel-2, Landsat-9) and deep learning models to perform rapid disaster detection, inundated area mapping, damage assessment, and real-time situational reporting for emergency response teams.
            </p>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-top: 24px;">
                <div class="card" style="padding: 20px; border-radius: 10px;">
                    <h3 style="margin-bottom: 8px; color: #38bdf8; font-size: 15px;">🛰 Multi-Spectral Analysis</h3>
                    <p style="font-size: 13px; opacity: 0.85;">Automated NDWI, dNBR, and SAR mask extraction for flood & fire boundaries.</p>
                </div>
                <div class="card" style="padding: 20px; border-radius: 10px;">
                    <h3 style="margin-bottom: 8px; color: #38bdf8; font-size: 15px;">⚡ Rapid Early Warning</h3>
                    <p style="font-size: 13px; opacity: 0.85;">Sub-hour processing pipeline converting raw satellite swaths into vector risk maps.</p>
                </div>
                <div class="card" style="padding: 20px; border-radius: 10px;">
                    <h3 style="margin-bottom: 8px; color: #38bdf8; font-size: 15px;">📊 Population Impact</h3>
                    <p style="font-size: 13px; opacity: 0.85;">Spatial overlay estimation of affected populations, infrastructure, and roads.</p>
                </div>
            </div>
        </div>
    `;
}


/* =========================================================
   FAQ PAGE
========================================================= */

function showFAQ() {
    pageContent.innerHTML = `
        <h1 class="page-title">Frequently Asked Questions</h1>
        <p class="page-subtitle">Learn more about Nirvaan satellite intelligence, metrics, and workflows.</p>

        <div style="display: flex; flex-direction: column; gap: 16px;">
            <div class="panel" style="padding: 22px;">
                <h3 style="margin-bottom: 8px; color: #38bdf8; font-size: 15px;">Q1: How does Nirvaan detect disaster affected zones?</h3>
                <p style="font-size: 14px; line-height: 1.6; opacity: 0.88;">
                    Nirvaan compares pre-event and post-event satellite imagery using optical spectral indices (NDWI for floods, dNBR for burn severity) and synthetic aperture radar (SAR) to identify flooded surfaces and burnt terrain regardless of cloud cover.
                </p>
            </div>

            <div class="panel" style="padding: 22px;">
                <h3 style="margin-bottom: 8px; color: #38bdf8; font-size: 15px;">Q2: What satellite constellations are supported?</h3>
                <p style="font-size: 14px; line-height: 1.6; opacity: 0.88;">
                    Currently supports Copernicus Sentinel-2 (Optical), Sentinel-1 (C-Band SAR), USGS Landsat-8/9, and custom high-resolution commercial imagery feeds via REST API endpoints.
                </p>
            </div>

            <div class="panel" style="padding: 22px;">
                <h3 style="margin-bottom: 8px; color: #38bdf8; font-size: 15px;">Q3: How frequently is the disaster map updated?</h3>
                <p style="font-size: 14px; line-height: 1.6; opacity: 0.88;">
                    Automated backend jobs ingest new satellite passes as soon as they become public (typically 12 to 24 hours revisit time), triggering instant risk updates and automated alert dispatches.
                </p>
            </div>

            <div class="panel" style="padding: 22px;">
                <h3 style="margin-bottom: 8px; color: #38bdf8; font-size: 15px;">Q4: Can SITREP situational reports be exported?</h3>
                <p style="font-size: 14px; line-height: 1.6; opacity: 0.88;">
                    Yes, under the <strong>Reports</strong> tab, you can export JSON metadata, GeoJSON impact boundaries, or formatted PDF situation reports for disaster management authorities.
                </p>
            </div>
        </div>
    `;
}