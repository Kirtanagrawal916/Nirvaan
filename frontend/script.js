
function setPageContent(html) {
    const container = document.getElementById("pageContent");
    if (container) {
        container.innerHTML = html;
    }
}
/* =========================================================
   THEME TOGGLE SYSTEM
========================================================= */

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

let pageContent = document.getElementById("pageContent");
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

// Bind all data-page buttons & topbar alert bell buttons
document.querySelectorAll("[data-page], .alert-icon-btn").forEach(el => {
    el.addEventListener("click", (e) => {
        const page = el.dataset.page || "alerts";
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

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
        loadPage("dashboard");
    });
} else {
    loadPage("dashboard");
}



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

    const disasterTypeUpper = (latest && latest.type) ? latest.type.toUpperCase() + " DETECTED" : "FLOOD DETECTED";
    const confidenceScore = (latest && latest.confidence !== undefined) ? latest.confidence : 94.7;
    const severity = (latest && latest.severity) ? latest.severity.toUpperCase() : "HIGH";
    const affectedArea = (latest && latest.affectedArea) ? latest.affectedArea : "31.8 km²";
    const location = (latest && latest.location) ? latest.location : "Surat, Gujarat";

    const beforeImgPath = (satellite && satellite.beforeImage) ? satellite.beforeImage : "assets/before.jpg";
    const afterImgPath = (satellite && satellite.afterImage) ? satellite.afterImage : "assets/after.jpg";

    let satelliteHtml = `
        <div style="padding: 20px;">

            <!-- FLOOD COMPARISON SCENE -->
            <div style="margin-bottom: 24px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <span style="font-size: 13px; font-weight: 700; color: #38bdf8;">🌊 SCENE 1: FLOOD INUNDATION (Surat, Gujarat — Tapi River Basin)</span>
                    <span style="font-size: 11px; opacity: 0.7;">Pass: Sentinel-2 L2A (10m)</span>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                    <div class="sat-card-box">
                        <span class="sat-badge normal">BEFORE FLOOD (PRE-EVENT)</span>
                        <img src="assets/before.jpg" alt="Before Flood Satellite Scene" class="sat-img">
                        <div class="sat-meta">
                            <span>🛰 Sentinel-2 L2A</span>
                            <span>NDWI: 0.12 (Normal Flow)</span>
                        </div>
                    </div>

                    <div class="sat-card-box">
                        <span class="sat-badge alert">AFTER FLOOD (POST-EVENT INUNDATED)</span>
                        <img src="assets/after.jpg" alt="After Flood Satellite Scene" class="sat-img">
                        <div class="sat-meta">
                            <span>🛰 Sentinel-2 L2A</span>
                            <span class="red-text">NDWI: 0.84 (Inundated)</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TSUNAMI COMPARISON SCENE -->
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <span style="font-size: 13px; font-weight: 700; color: #38bdf8;">🏖️ SCENE 2: TSUNAMI COASTAL SURGE IMPACT (Chennai Coastline)</span>
                    <span style="font-size: 11px; opacity: 0.7;">Pass: PlanetScope (3m High-Res)</span>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                    <div class="sat-card-box">
                        <span class="sat-badge normal">BEFORE TSUNAMI (PRE-EVENT)</span>
                        <img src="assets/tsunami-before.jpg" alt="Before Tsunami Satellite Scene" class="sat-img">
                        <div class="sat-meta">
                            <span>🛰 PlanetScope (3m)</span>
                            <span>Surge Index: 0.05 (Calm Sea)</span>
                        </div>
                    </div>

                    <div class="sat-card-box">
                        <span class="sat-badge alert">AFTER TSUNAMI (COASTAL INUNDATION)</span>
                        <img src="assets/tsunami-after.jpg" alt="After Tsunami Satellite Scene" class="sat-img">
                        <div class="sat-meta">
                            <span>🛰 PlanetScope (3m)</span>
                            <span class="red-text">Surge Index: 0.92 (Extreme Surge)</span>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    `;

    setPageContent(`

        <section class="dashboard-section">

            <h1 class="page-title">
                Dashboard
            </h1>

            <p class="page-subtitle">
                Real-time overview of disaster monitoring and multi-scene satellite imagery comparison
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



            <section class="dashboard-grid" style="display: block; width: 100%;">


                <!-- MULTI-SCENE SATELLITE COMPARISON SHOWCASE (FULL WIDTH) -->

                <div class="panel" style="width: 100%;">

                    <div class="panel-header">

                        <h2>
                            🛰 Multi-Temporal Satellite Image Comparison Showcase
                        </h2>

                        <button
                            onclick="loadPage('satellite')"
                        >
                            View Fullscreen Monitor
                        </button>

                    </div>

                    ${satelliteHtml}

                </div>

            </section>

        </section>

    `);

}



/* =========================================================
   SATELLITE MONITOR
========================================================= */

async function showSatellite() {

    const satellite = await getSatelliteImages();

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

    setPageContent(`

        <div class="satellite-section">

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

    `);

}



/* =========================================================
   DISASTER DETECTION
========================================================= */

function showDetection() {

    setPageContent(`

        <div class="disaster-section">

            <h1 class="page-title">
                Disaster Detection Engine
            </h1>

            <p class="page-subtitle">
                Configure satellite parameters, upload scenes, and run real-time AI flood analysis
            </p>


            <!-- DISASTER DETECTION 50% / 50% SPLIT LAYOUT GRID -->
            <div class="detection-50-split-grid">

                <!-- COLUMN 1: INTERACTIVE FLOOD DETECTION USER INPUT FORM (50% WIDTH) -->
                <div class="detection-input-card" style="margin-bottom: 0;">

                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 12px;">
                        <h3 style="font-size: 16px; color: #38bdf8; font-weight: 700; display: flex; align-items: center; gap: 8px; margin: 0;">
                            <span>🎛️</span> AI Flood Detection Parameters
                        </h3>
                        <span style="font-size: 11px; color: #a1a1aa; background: rgba(255,255,255,0.05); padding: 4px 10px; border-radius: 6px;">
                            Model: Sentinel-NET v4.2
                        </span>
                    </div>

                    <form id="floodDetectionForm" onsubmit="event.preventDefault(); runLiveDetection();">

                        <div class="detection-input-grid" style="grid-template-columns: 1fr; gap: 14px;">

                            <div class="input-field-group">
                                <label for="detectRegion">
                                    <span>Target Region / Location</span>
                                    <span>📍</span>
                                </label>
                                <select id="detectRegion">
                                    <option value="Surat, Gujarat (Tapi Basin)" selected>Surat, Gujarat (Tapi Basin)</option>
                                    <option value="Guwahati, Assam (Brahmaputra)">Guwahati, Assam (Brahmaputra)</option>
                                    <option value="Kochi, Kerala (Periyar Basin)">Kochi, Kerala (Periyar Basin)</option>
                                    <option value="Patna, Bihar (Ganges Basin)">Patna, Bihar (Ganges Basin)</option>
                                    <option value="Custom Coordinates">Custom Coordinates...</option>
                                </select>
                            </div>

                            <div class="input-field-group">
                                <label for="satSource">
                                    <span>Satellite Constellation</span>
                                    <span>🛰️</span>
                                </label>
                                <select id="satSource">
                                    <option value="Sentinel-2 L2A (10m SAR+Optical)" selected>Sentinel-2 L2A (10m SAR+Optical)</option>
                                    <option value="Landsat-9 OLI-2 (15m Thermal)">Landsat-9 OLI-2 (15m Thermal)</option>
                                    <option value="PlanetScope Constellation (3m High-Res)">PlanetScope Constellation (3m)</option>
                                    <option value="RISAT-1A Synthetic Aperture Radar">RISAT-1A SAR Radar</option>
                                </select>
                            </div>

                            <div class="input-field-group">
                                <label for="thresholdSlider">
                                    <span>NDWI Water Index Sensitivity</span>
                                    <span class="slider-val-badge" id="sliderValBadge">85%</span>
                                </label>
                                <div class="range-slider-wrapper">
                                    <span style="font-size: 11px; opacity: 0.6;">50%</span>
                                    <input
                                        type="range"
                                        id="thresholdSlider"
                                        min="50"
                                        max="99"
                                        value="85"
                                        oninput="document.getElementById('sliderValBadge').textContent = this.value + '%'"
                                    >
                                    <span style="font-size: 11px; opacity: 0.6;">99%</span>
                                </div>
                            </div>

                            <div class="input-field-group">
                                <label for="customSatImage">
                                    <span>Upload Satellite Scene (Optional)</span>
                                    <span>📁</span>
                                </label>
                                <input type="file" id="customSatImage" accept="image/*,.tif,.tiff">
                            </div>

                        </div>

                        <button type="submit" class="run-detection-btn" id="runDetectBtn" style="margin-top: 10px;">
                            <span>⚡ Run AI Flood Detection Analysis</span>
                            <span>→</span>
                        </button>

                    </form>

                </div>


                <!-- COLUMN 2: ATTRACTIVE LIVE AI DISASTER ANALYSIS OUTPUT (50% WIDTH) -->
                <div class="ai-output-panel">

                    <!-- PANEL HEADER -->
                    <div class="ai-output-header">
                        <h2>
                            <span class="alert-dot"></span>
                            <span>Live AI Disaster Analysis Output</span>
                        </h2>
                        <div class="ai-status-badge" id="detectStatusText">
                            <span>●</span>
                            <span>READY FOR ANALYSIS</span>
                        </div>
                    </div>

                    <!-- HERO ANALYSIS RESULT BOX -->
                    <div class="ai-hero-box">
                        <div class="ai-hero-icon-wrapper" id="detectIcon">
                            <span>≋</span>
                        </div>

                        <h2 class="ai-hero-title" id="detectResultTitle">
                            FLOOD INUNDATION DETECTED
                        </h2>

                        <div class="ai-hero-location" id="detectResultLoc">
                            <span>📍</span>
                            <span>Surat, Gujarat (Tapi Basin) • Sentinel-2 L2A Pass</span>
                        </div>
                    </div>

                    <!-- CONFIDENCE PROGRESS METER -->
                    <div class="ai-confidence-box">
                        <div class="ai-confidence-header">
                            <span>AI Neural Net Confidence Score</span>
                            <strong id="detectConfidenceVal">94.7%</strong>
                        </div>
                        <div class="ai-progress-track">
                            <div
                                class="ai-progress-fill"
                                id="detectProgressBar"
                                style="width: 94.7%;"
                            ></div>
                        </div>
                    </div>

                    <!-- 2x2 DETAILED METRICS GRID -->
                    <div class="ai-metrics-grid-2x2">
                        <div class="ai-metric-item">
                            <span class="ai-metric-label">Severity Level</span>
                            <span class="ai-metric-val high-alert" id="detectSeverityVal">HIGH SEVERITY</span>
                        </div>

                        <div class="ai-metric-item">
                            <span class="ai-metric-label">Inundated Area</span>
                            <span class="ai-metric-val cyan-highlight" id="detectAreaVal">31.8 km²</span>
                        </div>

                        <div class="ai-metric-item">
                            <span class="ai-metric-label">Population Exposed</span>
                            <span class="ai-metric-val" id="detectPopVal">128,400 people</span>
                        </div>

                        <div class="ai-metric-item">
                            <span class="ai-metric-label">Spectral NDWI Index</span>
                            <span class="ai-metric-val cyan-highlight" id="detectNdwiVal">0.84 (Critical)</span>
                        </div>
                    </div>

                    <!-- TELEMETRY FOOTER -->
                    <div class="ai-footer-telemetry">
                        <span>🛰 Neural Net Inference Engine</span>
                        <span>Multi-Band Fusion L2A</span>
                    </div>

                </div>

            </div>

        </div>

    `);

}

function runLiveDetection() {
    const region = document.getElementById("detectRegion").value;
    const source = document.getElementById("satSource").value;
    const threshold = document.getElementById("thresholdSlider").value;
    const btn = document.getElementById("runDetectBtn");
    const statusText = document.getElementById("detectStatusText");

    if (btn) btn.disabled = true;
    if (statusText) statusText.textContent = "⌛ RUNNING NEURAL NETWORK SEGMENTATION...";

    setTimeout(() => {
        const confidence = (88 + (threshold * 0.11)).toFixed(1);
        const area = (24 + (threshold * 0.12)).toFixed(1);
        const pop = Math.round(100000 + (threshold * 450));
        const ndwi = (0.75 + (threshold * 0.0015)).toFixed(2);

        document.getElementById("detectResultTitle").textContent = "FLOOD INUNDATION DETECTED";
        document.getElementById("detectResultLoc").textContent = `Target: ${region} — Data Source: ${source}`;
        document.getElementById("detectConfidenceVal").textContent = `${confidence}%`;
        document.getElementById("detectProgressBar").style.width = `${confidence}%`;
        document.getElementById("detectSeverityVal").textContent = threshold > 80 ? "EXTREME" : "HIGH";
        document.getElementById("detectAreaVal").textContent = `${area} km²`;
        document.getElementById("detectPopVal").textContent = `${pop.toLocaleString()} people`;
        document.getElementById("detectNdwiVal").textContent = `${ndwi} (Critical)`;

        if (statusText) statusText.textContent = "● ANALYSIS COMPLETE (LIVE SATELLITE FEED)";
        if (btn) btn.disabled = false;

        alert(`AI Flood Detection complete for ${region}!\n\nConfidence: ${confidence}%\nInundated Area: ${area} km²\nPopulation at Risk: ${pop.toLocaleString()}`);
    }, 800);
}



/* =========================================================
   RISK MAP
========================================================= */

function showRiskMap() {

    setPageContent(`

        <h1 class="page-title">
            Disaster Risk Map
        </h1>

        <p class="page-subtitle">
            Geographic risk visualization, seismic fault lines, inundation heatmaps, and tsunami hazard zones
        </p>

        <!-- MAP CONTROLS & LAYER SELECTOR -->
        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 24px; margin-bottom: 24px;">

            <div class="panel" style="padding: 20px;">

                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <h2 style="font-size: 16px; color: #38bdf8;">📍 Interactive Geo-Spatial Risk Engine</h2>
                        <select id="mapLocationSelect" onchange="updateRiskMapLocation(this.value)" style="background: #0b0c10; border: 1px solid #2b2e33; color: #fff; padding: 6px 12px; border-radius: 8px; font-size: 12.5px;">
                            <option value="surat" selected>Surat Tapi Basin (Flood - HIGH)</option>
                            <option value="bhuj">Bhuj Kutch Fault Line (Seismic - HIGH)</option>
                            <option value="guwahati">Guwahati Brahmaputra (Flood - EXTREME)</option>
                            <option value="chennai">Chennai Coastal Zone (Tsunami - WATCH)</option>
                        </select>
                    </div>

                    <div style="display: flex; gap: 8px;">
                        <button onclick="toggleMapLayer('flood')" class="map-layer-btn active" id="layerBtnFlood">🌊 Inundation</button>
                        <button onclick="toggleMapLayer('fault')" class="map-layer-btn" id="layerBtnFault">⚡ Fault Line</button>
                        <button onclick="toggleMapLayer('tsunami')" class="map-layer-btn" id="layerBtnTsunami">🏖️ Tsunami Zone</button>
                    </div>
                </div>

                <!-- ENHANCED RISK MAP DISPLAY CONTAINER -->
                <div class="map-container" id="riskMapDisplay" style="height: 380px; position: relative; border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.08); background: radial-gradient(circle at center, #0f1923 0%, #070d14 100%);">

                    <div class="map-grid"></div>

                    <!-- INTERACTIVE MAP OVERLAY ZONES -->
                    <div class="risk-zone zone-red" id="mapZoneRed" style="top: 35%; left: 42%; width: 140px; height: 140px;"></div>
                    <div class="risk-zone zone-orange" id="mapZoneOrange" style="top: 25%; left: 32%; width: 220px; height: 220px;"></div>
                    <div class="risk-zone zone-green" style="top: 15%; left: 20%; width: 320px; height: 320px;"></div>

                    <div class="map-label" id="mapLabelText" style="position: absolute; bottom: 20px; left: 20px; background: rgba(11, 12, 16, 0.85); backdrop-filter: blur(8px); padding: 8px 16px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); font-size: 13px; font-weight: 700; color: #38bdf8;">
                        📍 Surat, Gujarat — Active Flood Inundation Zone
                    </div>

                    <div style="position: absolute; top: 16px; right: 16px; background: rgba(11, 12, 16, 0.85); backdrop-filter: blur(8px); padding: 10px 14px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); font-size: 11px;">
                        <div style="font-weight: 700; color: #a1a1aa; margin-bottom: 6px;">MAP LEGEND</div>
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;"><span style="width: 10px; height: 10px; background: #ef4444; border-radius: 50%; display: inline-block;"></span> Critical Inundation</div>
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;"><span style="width: 10px; height: 10px; background: #f97316; border-radius: 50%; display: inline-block;"></span> Warning Buffer</div>
                        <div style="display: flex; align-items: center; gap: 8px;"><span style="width: 10px; height: 10px; background: #22c55e; border-radius: 50%; display: inline-block;"></span> Safe Relief Zones</div>
                    </div>

                </div>

            </div>

            <!-- LIVE RISK ANALYTICS PANEL -->
            <div class="panel" style="padding: 20px; display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <h3 style="font-size: 15px; color: #38bdf8; font-weight: 700; margin-bottom: 14px;">📊 Live Spatial Analytics</h3>
                    
                    <div style="display: flex; flex-direction: column; gap: 14px;">
                        <div style="background: rgba(255,255,255,0.03); padding: 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05);">
                            <span style="font-size: 11px; color: #a1a1aa;">Active Risk Hotspots</span>
                            <div style="font-size: 20px; font-weight: 800; color: #ef4444; margin-top: 2px;" id="riskHotspotsVal">3 Zones Active</div>
                        </div>

                        <div style="background: rgba(255,255,255,0.03); padding: 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05);">
                            <span style="font-size: 11px; color: #a1a1aa;">Population in Hazard Area</span>
                            <div style="font-size: 20px; font-weight: 800; color: #f97316; margin-top: 2px;" id="riskPopVal">142,500 People</div>
                        </div>

                        <div style="background: rgba(255,255,255,0.03); padding: 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05);">
                            <span style="font-size: 11px; color: #a1a1aa;">Relief Center Readiness</span>
                            <div style="font-size: 20px; font-weight: 800; color: #22c55e; margin-top: 2px;" id="riskReadinessVal">91% Operational</div>
                        </div>
                    </div>
                </div>

                <button class="run-detection-btn" style="margin-top: 16px;" onclick="alert('Exporting high-resolution GeoJSON risk map layer...')">
                    📥 Export GeoJSON Risk Layer
                </button>
            </div>

        </div>

    `);

}

function updateRiskMapLocation(loc) {
    const label = document.getElementById("mapLabelText");
    const hotspots = document.getElementById("riskHotspotsVal");
    const pop = document.getElementById("riskPopVal");

    if (loc === "surat") {
        if (label) label.textContent = "📍 Surat, Gujarat — Active Flood Inundation Zone";
        if (hotspots) hotspots.textContent = "3 Zones Active";
        if (pop) pop.textContent = "142,500 People";
    } else if (loc === "bhuj") {
        if (label) label.textContent = "📍 Bhuj, Kutch — Active Seismic Fault Line Zone";
        if (hotspots) hotspots.textContent = "2 Fault Rifts Active";
        if (pop) pop.textContent = "98,200 People";
    } else if (loc === "guwahati") {
        if (label) label.textContent = "📍 Guwahati, Assam — Brahmaputra Critical Overflow";
        if (hotspots) hotspots.textContent = "5 Zones Active";
        if (pop) pop.textContent = "310,000 People";
    } else if (loc === "chennai") {
        if (label) label.textContent = "📍 Chennai Coast — Tsunami Early Watch Boundary";
        if (hotspots) hotspots.textContent = "1 Warning Zone";
        if (pop) pop.textContent = "215,000 People";
    }
}

function toggleMapLayer(layer) {
    const btns = ["Flood", "Fault", "Tsunami"];
    btns.forEach(b => {
        const el = document.getElementById("layerBtn" + b);
        if (el) el.classList.remove("active");
    });

    const activeBtn = document.getElementById("layerBtn" + layer.charAt(0).toUpperCase() + layer.slice(1));
    if (activeBtn) activeBtn.classList.add("active");

    const redZone = document.getElementById("mapZoneRed");
    if (layer === "fault") {
        if (redZone) redZone.style.background = "radial-gradient(circle, rgba(168,85,247,0.7) 0%, rgba(168,85,247,0) 70%)";
    } else if (layer === "tsunami") {
        if (redZone) redZone.style.background = "radial-gradient(circle, rgba(56,189,248,0.7) 0%, rgba(56,189,248,0) 70%)";
    } else {
        if (redZone) redZone.style.background = "radial-gradient(circle, rgba(239,68,68,0.7) 0%, rgba(239,68,68,0) 70%)";
    }
}



/* =========================================================
   ALERTS
========================================================= */

function showAlerts() {

    setPageContent(`

        <h1 class="page-title" style="font-size: 28px; font-weight: 900; margin-bottom: 8px;">
            Emergency Disaster Alerts
        </h1>

        <p class="page-subtitle" style="font-size: 16px; margin-bottom: 28px;">
            Real-time disaster warnings, satellite telemetry alerts, and responder dispatches
        </p>

        <div class="alerts-grid">

            <!-- ALERT BOX 1: FLOOD -->
            <div class="alert-box-card critical">
                <div class="alert-box-header">
                    <div class="alert-title">
                        <span>🌊</span>
                        <span>Flood Inundation Warning — Surat, Gujarat (Tapi Basin)</span>
                    </div>
                    <span class="alert-badge critical">CRITICAL ALERT</span>
                </div>

                <p style="font-size: 14px; color: #a1a1aa; line-height: 1.6; margin-bottom: 12px;">
                    Sentinel-2 SAR imagery detected <strong>31.8 km² river overflow</strong> breaching Tapi embankment walls. Sub-surface flooding threatens urban residential sectors.
                </p>

                <div class="alert-metrics-grid">
                    <div class="alert-metric-item">
                        <span class="alert-metric-label">Inundation Extent</span>
                        <span class="alert-metric-value">31.8 km²</span>
                    </div>
                    <div class="alert-metric-item">
                        <span class="alert-metric-label">Population in Hazard</span>
                        <span class="alert-metric-value">128,400 People</span>
                    </div>
                    <div class="alert-metric-item">
                        <span class="alert-metric-label">Spectral NDWI Score</span>
                        <span class="alert-metric-value" style="color: #ef4444;">0.84 (Critical)</span>
                    </div>
                    <div class="alert-metric-item">
                        <span class="alert-metric-label">Alert Timestamp</span>
                        <span class="alert-metric-value" style="color: #a1a1aa;">10:28 AM (Active)</span>
                    </div>
                </div>

                <div class="alert-actions">
                    <button class="run-detection-btn" style="max-width: 220px; font-size: 13px; padding: 10px 16px;" onclick="alert('Dispatching emergency NDRF flood response team to Surat Tapi Basin...')">
                        🚨 Dispatch Responders
                    </button>
                    <button class="map-layer-btn active" style="font-size: 13px; padding: 10px 16px;" onclick="navigateToPage('risk')">
                        📍 Open Geo Map
                    </button>
                </div>
            </div>

            <!-- ALERT BOX 2: SEISMIC EARTHQUAKE -->
            <div class="alert-box-card high">
                <div class="alert-box-header">
                    <div class="alert-title">
                        <span>⚡</span>
                        <span>Seismic Fault Line Rupture — Bhuj, Kutch (Gujarat)</span>
                    </div>
                    <span class="alert-badge high">HIGH ALERT</span>
                </div>

                <p style="font-size: 14px; color: #a1a1aa; line-height: 1.6; margin-bottom: 12px;">
                    Seismic SAR interferometry detected <strong>4.2 cm ground rift displacement</strong> along the Kutch Fault Line. Structural integrity advisory issued for nearby settlements.
                </p>

                <div class="alert-metrics-grid">
                    <div class="alert-metric-item">
                        <span class="alert-metric-label">Seismic Rift Displacement</span>
                        <span class="alert-metric-value">4.2 cm SAR Shift</span>
                    </div>
                    <div class="alert-metric-item">
                        <span class="alert-metric-label">Population at Risk</span>
                        <span class="alert-metric-value">98,200 People</span>
                    </div>
                    <div class="alert-metric-item">
                        <span class="alert-metric-label">Rift Magnitude</span>
                        <span class="alert-metric-value" style="color: #f97316;">5.4 Mw Equivalent</span>
                    </div>
                    <div class="alert-metric-item">
                        <span class="alert-metric-label">Alert Timestamp</span>
                        <span class="alert-metric-value" style="color: #a1a1aa;">09:15 AM (Active)</span>
                    </div>
                </div>

                <div class="alert-actions">
                    <button class="run-detection-btn" style="max-width: 220px; font-size: 13px; padding: 10px 16px;" onclick="alert('Dispatching seismic inspection units to Bhuj Fault Zone...')">
                        🚨 Dispatch Responders
                    </button>
                    <button class="map-layer-btn active" style="font-size: 13px; padding: 10px 16px;" onclick="navigateToPage('risk')">
                        📍 Open Geo Map
                    </button>
                </div>
            </div>

            <!-- ALERT BOX 3: TSUNAMI WATCH -->
            <div class="alert-box-card warning">
                <div class="alert-box-header">
                    <div class="alert-title">
                        <span>🏖️</span>
                        <span>Tsunami Coastal Surge Watch — Chennai Coastline</span>
                    </div>
                    <span class="alert-badge warning">COASTAL WATCH</span>
                </div>

                <p style="font-size: 14px; color: #a1a1aa; line-height: 1.6; margin-bottom: 12px;">
                    Deep-sea buoy telemetry and PlanetScope satellite imagery identified a <strong>2.8m ocean surge wave</strong> approaching the coastal harbor region.
                </p>

                <div class="alert-metrics-grid">
                    <div class="alert-metric-item">
                        <span class="alert-metric-label">Coastal Surge Wave</span>
                        <span class="alert-metric-value">2.8m Amplitude</span>
                    </div>
                    <div class="alert-metric-item">
                        <span class="alert-metric-label">Coastal Population</span>
                        <span class="alert-metric-value">215,000 People</span>
                    </div>
                    <div class="alert-metric-item">
                        <span class="alert-metric-label">Surge Hazard Index</span>
                        <span class="alert-metric-value" style="color: #eab308;">0.92 (Elevated)</span>
                    </div>
                    <div class="alert-metric-item">
                        <span class="alert-metric-label">Alert Timestamp</span>
                        <span class="alert-metric-value" style="color: #a1a1aa;">08:40 AM (Monitoring)</span>
                    </div>
                </div>

                <div class="alert-actions">
                    <button class="run-detection-btn" style="max-width: 220px; font-size: 13px; padding: 10px 16px;" onclick="alert('Activating coastal evacuation siren alert network...')">
                        🚨 Issue Siren Alert
                    </button>
                    <button class="map-layer-btn active" style="font-size: 13px; padding: 10px 16px;" onclick="navigateToPage('risk')">
                        📍 Open Geo Map
                    </button>
                </div>
            </div>

        </div>

    `);

}



/* =========================================================
   REPORTS
========================================================= */

function showReports() {

    setPageContent(`

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

    `);

}



/* =========================================================
   HISTORY
========================================================= */

async function showHistory() {

    const disasters = await getDisasterHistory();

    setPageContent(`

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

    `);

}




/* =========================================================
   SETTINGS
========================================================= */

function showSettings() {

    setPageContent(`

        <h1 class="page-title" style="font-size: 28px; font-weight: 900; margin-bottom: 8px;">
            System Settings & Controls
        </h1>

        <p class="page-subtitle" style="font-size: 16px; margin-bottom: 28px;">
            Manage satellite telemetry streams, automated early warning triggers, and operational permissions
        </p>

        <!-- CATEGORY 1: SYSTEM OPERATIONS -->
        <div class="settings-card-panel">
            <div class="settings-card-header">
                <h3 class="settings-card-title">
                    <span>🎛️</span> Core Operations & Live Ingestion
                </h3>
                <span style="font-size: 11px; color: #38bdf8; background: rgba(56, 189, 248, 0.15); padding: 4px 10px; border-radius: 6px;">
                    Operational Status: ACTIVE
                </span>
            </div>

            <div class="settings-list">
                <div class="setting-item">
                    <div>
                        <strong>📡 Real-Time Satellite Telemetry Monitoring</strong>
                        <p>Continuously poll and process incoming orbital imagery from ESA Sentinel & USGS Landsat hubs</p>
                    </div>
                    <label class="setting-switch">
                        <input type="checkbox" checked onchange="alert('Real-time monitoring toggle updated.')">
                        <span class="setting-switch-slider"></span>
                    </label>
                </div>

                <div class="setting-item">
                    <div>
                        <strong>🤖 Automated AI Neural Segmentation Engine</strong>
                        <p>Automatically run U-Net NDWI & SAR inundation inference on incoming satellite passes</p>
                    </div>
                    <label class="setting-switch">
                        <input type="checkbox" checked onchange="alert('Automated AI Analysis toggle updated.')">
                        <span class="setting-switch-slider"></span>
                    </label>
                </div>

                <div class="setting-item">
                    <div>
                        <strong>📄 Automated SITREP Report Generation</strong>
                        <p>Generate GeoJSON hazard maps and PDF situational briefs immediately post-detection</p>
                    </div>
                    <label class="setting-switch">
                        <input type="checkbox" checked onchange="alert('Automated SITREP Reports toggle updated.')">
                        <span class="setting-switch-slider"></span>
                    </label>
                </div>
            </div>
        </div>

        <!-- CATEGORY 2: OPERATIONAL PERMISSIONS -->
        <div class="settings-card-panel">
            <div class="settings-card-header">
                <h3 class="settings-card-title">
                    <span>🛡️</span> Disaster Access & Operational Permissions
                </h3>
                <span style="font-size: 11px; color: #a1a1aa; background: rgba(255, 255, 255, 0.05); padding: 4px 10px; border-radius: 6px;">
                    Role: Commander / Response Lead
                </span>
            </div>

            <div class="settings-list">
                <div class="setting-item">
                    <div>
                        <strong>🛰️ Satellite Stream Ingestion Permission (Sentinel / Landsat)</strong>
                        <p>Authorize live telemetry data stream from ESA Sentinel Hub & USGS Landsat APIs</p>
                    </div>
                    <label class="setting-switch">
                        <input type="checkbox" checked onchange="alert('Satellite Stream Authorization updated.')">
                        <span class="setting-switch-slider"></span>
                    </label>
                </div>

                <div class="setting-item">
                    <div>
                        <strong>📡 High-Resolution SAR Synthetic Aperture Radar Access</strong>
                        <p>Enable all-weather cloud-penetrating radar feeds for flood and landslide tracking</p>
                    </div>
                    <label class="setting-switch">
                        <input type="checkbox" checked onchange="alert('SAR Radar Access permission updated.')">
                        <span class="setting-switch-slider"></span>
                    </label>
                </div>

                <div class="setting-item">
                    <div>
                        <strong>🚨 Emergency Disaster Warning Broadcast Authorization</strong>
                        <p>Authorize automated emergency SMS & push broadcasts to NDMA and first responder network</p>
                    </div>
                    <label class="setting-switch">
                        <input type="checkbox" checked onchange="alert('Emergency Warning Broadcast Authorization updated.')">
                        <span class="setting-switch-slider"></span>
                    </label>
                </div>

                <div class="setting-item">
                    <div>
                        <strong>🤖 AI Segmentation Model Calibration Rights</strong>
                        <p>Allow manual override and fine-tuning of neural network NDWI inundation thresholds</p>
                    </div>
                    <label class="setting-switch">
                        <input type="checkbox" checked onchange="alert('AI Model Calibration Rights updated.')">
                        <span class="setting-switch-slider"></span>
                    </label>
                </div>

                <div class="setting-item">
                    <div>
                        <strong>🏛️ Government Inter-Agency Data Exchange (ISRO / NDMA)</strong>
                        <p>Share encrypted spatial telemetry with state disaster management authorities</p>
                    </div>
                    <label class="setting-switch">
                        <input type="checkbox" checked onchange="alert('Government Inter-Agency Data Exchange permission updated.')">
                        <span class="setting-switch-slider"></span>
                    </label>
                </div>
            </div>
        </div>

    `);

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

/* =========================================================
   ABOUT PAGE
========================================================= */

function showAbout() {
    setPageContent(`
        <h1 class="page-title" style="font-size: 28px; font-weight: 900; margin-bottom: 8px;">About Nirvaan</h1>
        <p class="page-subtitle" style="font-size: 16px; margin-bottom: 28px;">Satellite-Based AI Disaster Monitoring & Rapid Intelligence Platform</p>

        <div class="panel" style="padding: 32px; border-radius: 16px; margin-bottom: 24px; background: #121417; border: 1px solid rgba(255, 255, 255, 0.08);">
            <h2 style="margin-bottom: 16px; color: #38bdf8; font-size: 22px; font-weight: 800; display: flex; align-items: center; gap: 10px;">
                <span>🌐</span> Mission & System Overview
            </h2>
            <p style="font-size: 16px; line-height: 1.8; color: #e0e0e0; margin-bottom: 24px;">
                <strong>Nirvaan</strong> is an advanced, satellite-driven disaster intelligence engine engineered to perform <strong>rapid disaster detection</strong>, <strong>inundated area mapping</strong>, and <strong>real-time situational risk assessment</strong>. By fusing multi-spectral satellite imagery (Copernicus Sentinel-2, USGS Landsat-9) with deep learning segmentation neural networks, Nirvaan equips emergency response managers with sub-hour actionable intelligence.
            </p>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px;">
                <div class="card" style="padding: 24px; border-radius: 14px; background: #1a1c20; border: 1px solid rgba(255, 255, 255, 0.06);">
                    <h3 style="margin-bottom: 10px; color: #38bdf8; font-size: 17px; font-weight: 700;">🛰 Multi-Spectral Imagery</h3>
                    <p style="font-size: 14.5px; line-height: 1.7; color: #a1a1aa;">
                        Automated extraction of <strong>NDWI (Water Index)</strong> and <strong>SAR (Synthetic Aperture Radar)</strong> masks to detect flood extent through heavy cloud cover.
                    </p>
                </div>

                <div class="card" style="padding: 24px; border-radius: 14px; background: #1a1c20; border: 1px solid rgba(255, 255, 255, 0.06);">
                    <h3 style="margin-bottom: 10px; color: #38bdf8; font-size: 17px; font-weight: 700;">⚡ Rapid Early Warning</h3>
                    <p style="font-size: 14.5px; line-height: 1.7; color: #a1a1aa;">
                        Sub-hour automated pipeline processing raw satellite swaths into <strong>high-resolution vector risk maps</strong> and automated broadcasts.
                    </p>
                </div>

                <div class="card" style="padding: 24px; border-radius: 14px; background: #1a1c20; border: 1px solid rgba(255, 255, 255, 0.06);">
                    <h3 style="margin-bottom: 10px; color: #38bdf8; font-size: 17px; font-weight: 700;">📊 Population & Asset Risk</h3>
                    <p style="font-size: 14.5px; line-height: 1.7; color: #a1a1aa;">
                        Spatial demographic overlay calculating <strong>affected populations</strong>, <strong>submerged roadways</strong>, and <strong>critical infrastructure</strong>.
                    </p>
                </div>

                <div class="card" style="padding: 24px; border-radius: 14px; background: #1a1c20; border: 1px solid rgba(255, 255, 255, 0.06);">
                    <h3 style="margin-bottom: 10px; color: #38bdf8; font-size: 17px; font-weight: 700;">🛡️ Inter-Agency Interoperability</h3>
                    <p style="font-size: 14.5px; line-height: 1.7; color: #a1a1aa;">
                        Seamless GIS spatial telemetry exchange with <strong>NDMA</strong>, <strong>ISRO</strong>, and <strong>State Disaster Relief Forces</strong>.
                    </p>
                </div>
            </div>
        </div>
    `);
}


/* =========================================================
   FAQ PAGE
========================================================= */

function showFAQ() {
    setPageContent(`
        <h1 class="page-title" style="font-size: 28px; font-weight: 900; margin-bottom: 8px;">Frequently Asked Questions</h1>
        <p class="page-subtitle" style="font-size: 16px; margin-bottom: 28px;">Learn more about Nirvaan satellite intelligence, metrics, and emergency response workflows.</p>

        <div style="display: flex; flex-direction: column; gap: 20px;">

            <div class="panel" style="padding: 26px; border-radius: 14px; background: #121417; border: 1px solid rgba(255, 255, 255, 0.08);">
                <h3 style="margin-bottom: 10px; color: #38bdf8; font-size: 18px; font-weight: 800;">Q1: How does Nirvaan detect disaster affected zones?</h3>
                <p style="font-size: 15px; line-height: 1.8; color: #e0e0e0;">
                    Nirvaan compares pre-event baseline scenes with post-event satellite imagery using optical spectral indices (<strong>NDWI</strong> for floods, <strong>dNBR</strong> for burn severity) and synthetic aperture radar (<strong>SAR</strong>) to identify flooded surfaces regardless of cloud cover.
                </p>
            </div>

            <div class="panel" style="padding: 26px; border-radius: 14px; background: #121417; border: 1px solid rgba(255, 255, 255, 0.08);">
                <h3 style="margin-bottom: 10px; color: #38bdf8; font-size: 18px; font-weight: 800;">Q2: What satellite constellations are supported?</h3>
                <p style="font-size: 15px; line-height: 1.8; color: #e0e0e0;">
                    Nirvaan natively ingests <strong>Copernicus Sentinel-2</strong> (Optical), <strong>Sentinel-1</strong> (C-Band Radar), <strong>USGS Landsat-8/9</strong>, and high-resolution <strong>PlanetScope (3m)</strong> imagery feeds via automated REST APIs.
                </p>
            </div>

            <div class="panel" style="padding: 26px; border-radius: 14px; background: #121417; border: 1px solid rgba(255, 255, 255, 0.08);">
                <h3 style="margin-bottom: 10px; color: #38bdf8; font-size: 18px; font-weight: 800;">Q3: How frequently is the disaster risk map updated?</h3>
                <p style="font-size: 15px; line-height: 1.8; color: #e0e0e0;">
                    Automated background tasks ingest new satellite passes as soon as they become available from orbital feeds (typically <strong>12 to 24-hour revisit cadence</strong>), instantly recalculating hazard boundaries.
                </p>
            </div>

            <div class="panel" style="padding: 26px; border-radius: 14px; background: #121417; border: 1px solid rgba(255, 255, 255, 0.08);">
                <h3 style="margin-bottom: 10px; color: #38bdf8; font-size: 18px; font-weight: 800;">Q4: Can SITREP situational reports be exported?</h3>
                <p style="font-size: 15px; line-height: 1.8; color: #e0e0e0;">
                    Yes, under the <strong>Reports</strong> tab, response leads can generate and export <strong>JSON metadata</strong>, <strong>GeoJSON impact vector boundaries</strong>, or formatted <strong>SITREP situation reports</strong>.
                </p>
            </div>

            <div class="panel" style="padding: 26px; border-radius: 14px; background: #121417; border: 1px solid rgba(255, 255, 255, 0.08);">
                <h3 style="margin-bottom: 10px; color: #38bdf8; font-size: 18px; font-weight: 800;">Q5: How do first responders receive critical warnings?</h3>
                <p style="font-size: 15px; line-height: 1.8; color: #e0e0e0;">
                    Whenever the AI neural network detects inundation confidence exceeding <strong>85%</strong>, automated push notifications and SMS warning broadcasts are immediately dispatched to registered emergency commanders.
                </p>
            </div>

        </div>
    `);
}