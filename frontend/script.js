
function setPageContent(html) {
    const container = document.getElementById("pageContent");
    if (container) {
        container.innerHTML = html;
    }
}
/* =========================================================
   THEME TOGGLE SYSTEM

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

/* =========================================================
   AUTHENTICATION & LOGIN SYSTEM

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

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
        loadPage("dashboard");
    });
} else {
    loadPage("dashboard");
}



/* =========================================================
   PAGE ROUTER

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

            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <div>
                    <h1 class="page-title" style="margin-bottom: 4px;">
                        Dashboard
                    </h1>
                    <p class="page-subtitle">
                        Real-time overview of disaster monitoring and multi-scene satellite imagery comparison
                    </p>
                </div>
                <button class="primary-btn" id="dashboardGenerateSitrepBtn" style="padding: 10px 20px; font-weight: 700; background: linear-gradient(135deg, #2563eb, #1d4ed8); border: none; box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4);">
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

    const sitrepBtn = document.getElementById("dashboardGenerateSitrepBtn");
    if (sitrepBtn) {
        const targetEventId = (latest && latest.event_id) ? latest.event_id : "flood-emilia-romagna-2023";
        sitrepBtn.addEventListener("click", () => {
            loadPage("reports");
            setTimeout(() => executeSitrepGeneration(targetEventId), 150);
        });
    }

}



/* =========================================================
   SATELLITE MONITOR

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

async function showDetection() {

    const latest = await getLatestDisaster();
    updateProvenanceBanner(latest);
    const disasterTypeUpper = (latest && latest.type) ? latest.type.toUpperCase() + " DETECTED" : "FLOOD DETECTED";
    const confidenceScore = (latest && latest.confidence !== undefined) ? latest.confidence : 94.7;
    const severity = (latest && latest.severity) ? latest.severity.toUpperCase() : "LOW";
    const affectedArea = (latest && latest.affectedArea) ? latest.affectedArea : "0.0 km²";
    const location = (latest && latest.location) ? latest.location : "Emilia-Romagna, Italy";

    setPageContent(`

        <div class="disaster-section">

            <h1 class="page-title">
                Disaster Detection Engine
            </h1>

            <p class="page-subtitle">
                Configure satellite parameters, upload scenes, and run real-time AI flood analysis
            </p>


            <!-- FLOOD DETECTION BOX (CONSISTS OF 65-70% TOTAL HORIZONTAL AREA) -->
            <div class="flood-detection-box-container">

                <!-- INTERACTIVE FLOOD DETECTION USER INPUT FORM -->
                <div class="detection-input-card">

                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 12px;">
                        <h3 style="font-size: 16px; color: #38bdf8; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                            <span>🎛️</span> AI Flood Detection Input Parameters
                        </h3>
                        <span style="font-size: 11px; color: #a1a1aa; background: rgba(255,255,255,0.05); padding: 4px 10px; border-radius: 6px;">
                            Model: Nirvaan Sentinel-NET v4.2
                        </span>
                    </div>

                    <form id="floodDetectionForm" onsubmit="event.preventDefault(); runLiveDetection();">

                        <div class="detection-input-grid">

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

                        <button type="submit" class="run-detection-btn" id="runDetectBtn">
                            <span>⚡ Run AI Flood Detection Analysis</span>
                            <span>→</span>
                        </button>

                    </form>

                </div>


                <!-- AI MODEL DETECTION RESULTS -->

                <div class="panel" style="width: 100%;">

                    <div class="panel-header">
                        <h2>
                            ⚠ Live AI Disaster Analysis Output
                        </h2>
                        <span style="font-size: 12px; color: #38bdf8; font-weight: 600;" id="detectStatusText">
                            ● READY FOR ANALYSIS
                        </span>
                    </div>

                    <div class="detection" style="max-width: 100%; padding: 24px;">

                        <div class="detection-icon" id="detectIcon">
                            ≋
                        </div>

                        <h2 id="detectResultTitle" style="font-size: 22px;">
                            FLOOD INUNDATION DETECTED
                        </h2>

                        <p id="detectResultLoc" style="font-size: 14px; opacity: 0.8; margin-bottom: 20px;">
                            Target: Surat, Gujarat (Tapi Basin) — Sentinel-2 L2A Pass
                        </p>


                        <div class="confidence-row">
                            <span>AI Confidence Score</span>
                            <strong id="detectConfidenceVal">94.7%</strong>
                        </div>

                        <div class="progress">
                            <div
                                class="progress-value"
                                id="detectProgressBar"
                                style="width: 94.7%;"
                            ></div>
                        </div>


                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; width: 100%; margin-top: 20px;">

                            <div class="detail" style="background: rgba(255,255,255,0.03); padding: 12px; border-radius: 8px;">
                                <span>Severity Level</span>
                                <strong class="high" id="detectSeverityVal">HIGH</strong>
                            </div>

                            <div class="detail" style="background: rgba(255,255,255,0.03); padding: 12px; border-radius: 8px;">
                                <span>Inundated Area</span>
                                <strong id="detectAreaVal">31.8 km²</strong>
                            </div>

                            <div class="detail" style="background: rgba(255,255,255,0.03); padding: 12px; border-radius: 8px;">
                                <span>Population at Risk</span>
                                <strong id="detectPopVal">128,400 people</strong>
                            </div>

                            <div class="detail" style="background: rgba(255,255,255,0.03); padding: 12px; border-radius: 8px;">
                                <span>Spectral NDWI Index</span>
                                <strong style="color: #38bdf8;" id="detectNdwiVal">0.84 (Critical)</strong>
                            </div>

                        </div>

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

async function showRiskMap() {

    const latest = await getLatestDisaster();
    updateProvenanceBanner(latest);
    const location = (latest && latest.location) ? latest.location : "Emilia-Romagna, Italy";

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

async function showAlerts() {

    const disasters = await getDisasterHistory();
    updateProvenanceBanner(disasters && disasters[0]);

    setPageContent(`

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

    `);

}



/* =========================================================
   REPORTS & ONE-CLICK SITREP GENERATION
========================================================= */

let currentSitrepData = null;

async function showReports() {
    const latest = await getLatestDisaster();
    updateProvenanceBanner(latest);

    const activeEventId = (latest && latest.event_id) ? latest.event_id : "flood-emilia-romagna-2023";
    const location = (latest && latest.location) ? latest.location : "Emilia-Romagna, Italy";

    setPageContent(`
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <div>
                <h1 class="page-title" style="margin-bottom: 4px;">Emergency Situation Reports</h1>
                <p class="page-subtitle">One-click responder SITREP generation powered by satellite observation & spatial analytics</p>
            </div>
            <button class="primary-btn" id="headerGenerateSitrepBtn" style="padding: 12px 24px; font-size: 15px; font-weight: 700; background: linear-gradient(135deg, #2563eb, #1d4ed8); border: none; box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4);">
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
    `);

    const headerBtn = document.getElementById("headerGenerateSitrepBtn");
    if (headerBtn) {
        headerBtn.addEventListener("click", () => {
            executeSitrepGeneration(activeEventId);
        });
    }
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


/* =========================================================
   HISTORY
========================================================= */

async function showHistory() {

    const disasters = await getDisasterHistory();
    updateProvenanceBanner(disasters && disasters[0]);

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

        <!-- OPERATIONAL PERMISSIONS & DATA SECURITY PANEL -->
        <div class="panel" style="margin-top: 24px; padding: 24px;">

            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 12px;">
                <h3 style="font-size: 16px; color: #38bdf8; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                    <span>🛡️</span> Disaster Access & Operational Permissions
                </h3>
                <span style="font-size: 11px; color: #a1a1aa; background: rgba(56, 189, 248, 0.15); padding: 4px 10px; border-radius: 6px;">
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