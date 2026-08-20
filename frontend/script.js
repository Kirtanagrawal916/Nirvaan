
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
   DYNAMIC CANVAS SATELLITE ORBIT ANIMATION ENGINE (ENHANCED BRIGHTNESS)
========================================================= */

function initSatelliteOrbitBackground(targetCanvasId) {
    if (typeof window === "undefined") return;
    const canvas = document.getElementById(targetCanvasId || "satelliteOrbitCanvas");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const parent = canvas.parentElement || document.body;
    let width = (canvas.width = parent.clientWidth || window.innerWidth);
    let height = (canvas.height = parent.clientHeight || window.innerHeight);

    window.addEventListener("resize", () => {
        if (canvas && canvas.parentElement) {
            width = canvas.width = canvas.parentElement.clientWidth || window.innerWidth;
            height = canvas.height = canvas.parentElement.clientHeight || window.innerHeight;
        }
    });

    // STARS IN SPACE WITH SHARPER BRIGHTNESS
    const stars = Array.from({ length: 160 }, () => ({
        x: Math.random() * width,
        y: Math.random() * height,
        radius: Math.random() * 1.8 + 0.6,
        alpha: Math.random() * 0.9 + 0.3,
        speed: Math.random() * 0.05 + 0.01
    }));

    // VIVID CITY LIGHT CLUSTERS ON EARTH CURVATURE
    const cityLights = Array.from({ length: 120 }, () => ({
        angle: Math.random() * Math.PI * 0.65 + Math.PI * 0.9,
        dist: Math.random() * 95 + 310,
        size: Math.random() * 2.5 + 1.2,
        color: Math.random() > 0.35 ? "#fbbf24" : "#38bdf8"
    }));

    let orbitAngle = 0;
    let scanPulse = 0;

    function draw() {
        ctx.clearRect(0, 0, width, height);

        // 1. DEEP SPACE & STARFIELD
        stars.forEach(s => {
            s.alpha += Math.sin(Date.now() * 0.002 + s.x) * 0.01;
            ctx.fillStyle = `rgba(255, 255, 255, ${Math.max(0.2, Math.min(1.0, s.alpha))})`;
            ctx.beginPath();
            ctx.arc(s.x, s.y, s.radius, 0, Math.PI * 2);
            ctx.fill();
        });

        // EARTH CURVATURE AT BOTTOM-RIGHT (NON-OBSCURING CORNER PLACEMENT)
        const isFullscreenCanvas = !targetCanvasId || targetCanvasId === "satelliteOrbitCanvas";
        const earthX = isFullscreenCanvas ? width * 0.92 : width * 0.82;
        const earthY = isFullscreenCanvas ? height * 1.25 : height * 1.12;
        const earthRadius = isFullscreenCanvas ? Math.min(width, height) * 0.52 : Math.min(width, height) * 0.68;

        // EARTH ATMOSPHERE INTENSE OUTER GLOW
        const atmGlow = ctx.createRadialGradient(earthX, earthY, earthRadius * 0.88, earthX, earthY, earthRadius * 1.25);
        atmGlow.addColorStop(0, "rgba(56, 189, 248, 0.65)");
        atmGlow.addColorStop(0.4, "rgba(16, 185, 129, 0.35)");
        atmGlow.addColorStop(0.75, "rgba(56, 189, 248, 0.15)");
        atmGlow.addColorStop(1, "rgba(56, 189, 248, 0)");

        ctx.fillStyle = atmGlow;
        ctx.beginPath();
        ctx.arc(earthX, earthY, earthRadius * 1.25, 0, Math.PI * 2);
        ctx.fill();

        // EARTH BODY GRADIENT WITH BLUE-GREEN OCEAN ILLUMINATION
        const earthGrad = ctx.createRadialGradient(earthX - 140, earthY - 140, 40, earthX, earthY, earthRadius);
        earthGrad.addColorStop(0, "#1e40af");
        earthGrad.addColorStop(0.35, "#0f766e");
        earthGrad.addColorStop(0.65, "#0b2a4a");
        earthGrad.addColorStop(0.9, "#041224");
        earthGrad.addColorStop(1, "#020712");

        ctx.fillStyle = earthGrad;
        ctx.beginPath();
        ctx.arc(earthX, earthY, earthRadius, 0, Math.PI * 2);
        ctx.fill();

        // BRIGHT CLOUD & CONTINENTAL CURVATURE ARCS
        ctx.save();
        ctx.strokeStyle = "rgba(255, 255, 255, 0.18)";
        ctx.lineWidth = 14;
        ctx.beginPath();
        ctx.arc(earthX, earthY, earthRadius - 20, Math.PI * 1.05, Math.PI * 1.45);
        ctx.stroke();

        ctx.strokeStyle = "rgba(56, 189, 248, 0.25)";
        ctx.lineWidth = 8;
        ctx.beginPath();
        ctx.arc(earthX, earthY, earthRadius - 45, Math.PI * 1.15, Math.PI * 1.55);
        ctx.stroke();
        ctx.restore();

        // VIVID CITY LIGHTS WITH NEON GLOW
        cityLights.forEach(cl => {
            const lx = earthX + Math.cos(cl.angle) * cl.dist;
            const ly = earthY + Math.sin(cl.angle) * cl.dist;
            ctx.fillStyle = cl.color;
            ctx.shadowBlur = 12;
            ctx.shadowColor = cl.color;
            ctx.beginPath();
            ctx.arc(lx, ly, cl.size, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;
        });

        // 2. ORBIT TRAJECTORY HIGH-VISIBILITY DASHED LINE
        orbitAngle += 0.0035;
        scanPulse = (scanPulse + 0.02) % (Math.PI * 2);
        const rx = width * 0.44;
        const ry = height * 0.40;
        const cx = width * 0.54;
        const cy = height * 0.50;

        ctx.save();
        ctx.strokeStyle = "rgba(56, 189, 248, 0.55)";
        ctx.lineWidth = 2;
        ctx.shadowBlur = 10;
        ctx.shadowColor = "#38bdf8";
        ctx.setLineDash([10, 6]);
        ctx.beginPath();
        ctx.ellipse(cx, cy, rx, ry, -Math.PI / 10, 0, Math.PI * 2);
        ctx.stroke();
        ctx.restore();

        // 3. ILLUMINATED SATELLITE POSITION CALCULATION
        const satX = cx + Math.cos(orbitAngle) * rx;
        const satY = cy + Math.sin(orbitAngle) * ry;

        // VIVID LASER SCAN TELEMETRY BEAM TO EARTH
        const beamPulse = (Math.sin(scanPulse) + 1) / 2 * 0.4 + 0.4;
        ctx.save();
        ctx.strokeStyle = `rgba(56, 189, 248, ${beamPulse})`;
        ctx.lineWidth = 2;
        ctx.shadowBlur = 14;
        ctx.shadowColor = "#38bdf8";
        ctx.beginPath();
        ctx.moveTo(satX, satY);
        ctx.lineTo(earthX - earthRadius * 0.28, earthY - earthRadius * 0.42);
        ctx.stroke();

        // SECONDARY SCAN CONE
        ctx.fillStyle = `rgba(56, 189, 248, ${beamPulse * 0.15})`;
        ctx.beginPath();
        ctx.moveTo(satX, satY);
        ctx.lineTo(earthX - earthRadius * 0.35, earthY - earthRadius * 0.35);
        ctx.lineTo(earthX - earthRadius * 0.22, earthY - earthRadius * 0.48);
        if (ctx.closePath) ctx.closePath();
        ctx.fill();
        ctx.restore();

        // ILLUMINATED SATELLITE WITH HIGH-CONTRAST SOLAR PANELS
        ctx.save();
        ctx.translate(satX, satY);
        ctx.rotate(orbitAngle + Math.PI / 4);

        // SOLAR PANEL GLOW
        ctx.shadowBlur = 16;
        ctx.shadowColor = "#38bdf8";

        // LEFT EXTENDED SOLAR ARRAY PANEL
        ctx.fillStyle = "#0284c7";
        ctx.strokeStyle = "#38bdf8";
        ctx.lineWidth = 1.5;
        ctx.fillRect(-46, -8, 32, 16);
        ctx.strokeRect(-46, -8, 32, 16);

        // RIGHT EXTENDED SOLAR ARRAY PANEL
        ctx.fillRect(14, -8, 32, 16);
        ctx.strokeRect(14, -8, 32, 16);

        // SOLAR PANEL PHOTON CELL GRID
        ctx.strokeStyle = "rgba(255, 255, 255, 0.7)";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(-35, -8); ctx.lineTo(-35, 8);
        ctx.moveTo(-24, -8); ctx.lineTo(-24, 8);
        ctx.moveTo(25, -8); ctx.lineTo(25, 8);
        ctx.moveTo(36, -8); ctx.lineTo(36, 8);
        ctx.stroke();

        // MAIN SATELLITE CHASSIS METALLIC GOLD/SILVER BODY
        ctx.fillStyle = "#f8fafc";
        ctx.fillRect(-12, -10, 24, 20);
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 2;
        ctx.strokeRect(-12, -10, 24, 20);

        // GOLD THERMAL FOIL STRIP
        ctx.fillStyle = "#f59e0b";
        ctx.fillRect(-8, -6, 16, 12);

        // SENSOR APERTURE DISH
        ctx.fillStyle = "#10b981";
        ctx.shadowColor = "#10b981";
        ctx.beginPath();
        ctx.arc(0, 12, 5, 0, Math.PI * 2);
        ctx.fill();

        ctx.restore();

        // CRISP HIGH-CONTRAST TELEMETRY BADGE TEXT
        ctx.save();
        ctx.font = "bold 11px Outfit, sans-serif";
        ctx.fillStyle = "#38bdf8";
        ctx.shadowBlur = 10;
        ctx.shadowColor = "rgba(0, 0, 0, 0.9)";
        ctx.fillText("🛰 NIRVAAN SAT-1 :: ALT 686 km :: SENSOR SENTINEL-2 L2A", satX + 22, satY - 16);
        ctx.restore();

        requestAnimationFrame(draw);
    }

    draw();
}

/* =========================================================
   INITIAL PAGE
========================================================= */

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
        initSatelliteOrbitBackground();
        loadPage("dashboard");
    });
} else {
    initSatelliteOrbitBackground();
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
   SATELLITE MONITORING & DISASTER ANALYSIS MODULE
========================================================= */

function getSatState() {
    if (typeof window === "undefined") return {};
    if (!window.satState) {
        window.satState = {
            uploadedImage: null,
            activeImage: "assets/after.jpg",
            beforeImage: "assets/before.jpg",
            disasterType: "Flood Inundation",
            disasterIcon: "🌊",
            confidence: 94.7,
            affectedArea: "14.2 km²",
            populationRisk: "12,500",
            severityScore: "65.0 / 100",
            severityBand: "HIGH RISK",
            location: "Surat, Gujarat (Tapi River Basin)",
            sensor: "Sentinel-2 L2A (10m)",
            coordinates: "21.1702° N, 72.8311° E",
            showHeatmap: true,
            showBoundingBoxes: true,
            showComparison: false,
            isAnalyzing: false
        };
    }
    return window.satState;
}

function triggerSatImageUpload() {
    const input = document.getElementById("satImageUploadInput");
    if (input) {
        input.click();
    }
}

function handleSatImageUpload(event) {
    const file = event.target.files && event.target.files[0];
    if (!file) return;

    const s = getSatState();
    const reader = new FileReader();
    reader.onload = function(e) {
        s.uploadedImage = e.target.result;
        s.activeImage = e.target.result;
        s.showComparison = false;
        s.disasterType = "Uploaded Scene Analysis";
        s.disasterIcon = "🛰️";
        s.confidence = 96.2;
        s.affectedArea = "18.6 km²";
        s.populationRisk = "14,200";
        s.severityScore = "72.4 / 100";
        s.severityBand = "HIGH SEVERITY";
        s.location = file.name || "Custom Satellite Pass";
        s.sensor = "User Raster Swath (High-Res)";
        
        refreshSatelliteMonitoringUI();
    };
    reader.readAsDataURL(file);
}

function runSatDisasterAnalysis() {
    const s = getSatState();
    s.isAnalyzing = true;
    refreshSatelliteMonitoringUI();

    setTimeout(() => {
        s.isAnalyzing = false;
        s.confidence = parseFloat((Math.min(99.4, Math.max(90.0, s.confidence + (Math.random() * 1.5 - 0.5)))).toFixed(1));
        s.showHeatmap = true;
        s.showBoundingBoxes = true;
        refreshSatelliteMonitoringUI();
    }, 700);
}

function toggleSatComparisonView() {
    const s = getSatState();
    s.showComparison = !s.showComparison;
    refreshSatelliteMonitoringUI();
}

function toggleSatHeatmap() {
    const s = getSatState();
    s.showHeatmap = !s.showHeatmap;
    refreshSatelliteMonitoringUI();
}

function toggleSatBoundingBoxes() {
    const s = getSatState();
    s.showBoundingBoxes = !s.showBoundingBoxes;
    refreshSatelliteMonitoringUI();
}

function refreshSatelliteMonitoringUI() {
    const container = document.getElementById("satMonitoringSectionContainer");
    if (container) {
        container.innerHTML = renderSatelliteMonitoringHTML();
        setTimeout(() => {
            initSatelliteOrbitBackground("embeddedOrbitCanvas");
        }, 50);
    }
}

function renderSatelliteMonitoringHTML() {
    const s = getSatState();

    return `
        <div class="sat-monitoring-grid" id="satMonitoringGrid">

            <!-- MAIN SATELLITE MONITORING PANEL (LEFT) -->
            <div class="sat-main-panel">

                <input type="file" id="satImageUploadInput" style="display:none;" accept="image/*,.tif,.tiff" onchange="handleSatImageUpload(event)">

                <div class="sat-toolbar-actions">
                    <!-- TOP ROW: TITLE & SUBTITLE -->
                    <div class="sat-toolbar-title-row">
                        <h3><span>🛰️</span> Satellite Monitoring</h3>
                        <p>${s.location} — ${s.sensor}</p>
                    </div>

                    <!-- BOTTOM ROW: BUTTON CONTROLS (PRIMARY ACTIONS LEFT, TOGGLES RIGHT) -->
                    <div class="sat-toolbar-controls-row">
                        <div class="sat-btn-group-primary">
                            <button class="sat-action-btn upload" onclick="triggerSatImageUpload()">
                                <span>📁</span> Upload Image
                            </button>
                            <button class="sat-action-btn analyze" onclick="runSatDisasterAnalysis()">
                                <span>${s.isAnalyzing ? "⌛" : "⚡"}</span> ${s.isAnalyzing ? "Analyzing..." : "Analyze Disaster"}
                            </button>
                            <button class="sat-action-btn compare ${s.showComparison ? "active" : ""}" onclick="toggleSatComparisonView()">
                                <span>⚖️</span> ${s.showComparison ? "Single View" : "Compare Before/After"}
                            </button>
                        </div>

                        <div class="sat-btn-group-toggles">
                            <button class="sat-action-btn toggle ${s.showHeatmap ? "active" : ""}" onclick="toggleSatHeatmap()" title="Toggle Heatmap Layer">
                                <span>🔥</span> Heatmap
                            </button>
                            <button class="sat-action-btn toggle ${s.showBoundingBoxes ? "active" : ""}" onclick="toggleSatBoundingBoxes()" title="Toggle Bounding Boxes">
                                <span>🎯</span> Bounding Boxes
                            </button>
                        </div>
                    </div>
                </div>

                <!-- VIEWPORT BOX CONTAINING EMBEDDED DYNAMIC SATELLITE ORBIT CANVAS -->
                <div class="sat-viewport-box">
                    <div class="embedded-orbit-box-wrapper">
                        <canvas id="embeddedOrbitCanvas" class="embedded-orbit-canvas"></canvas>
                        <div class="embedded-orbit-translucent-overlay"></div>

                        <div class="embedded-raster-overlay-content">
                            ${s.showComparison ? `
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px; width: 100%; height: 100%;">
                                    <div style="position: relative; height: 100%;">
                                        <span style="position: absolute; top: 12px; left: 12px; z-index: 20; background: rgba(0,0,0,0.7); color: #ffffff; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700;">BEFORE (PRE-EVENT)</span>
                                        <img src="${s.beforeImage}" class="sat-viewport-img" alt="Before Satellite Pass">
                                    </div>
                                    <div style="position: relative; height: 100%;">
                                        <span style="position: absolute; top: 12px; left: 12px; z-index: 20; background: rgba(239,68,68,0.85); color: #ffffff; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700;">AFTER (POST-EVENT INUNDATED)</span>
                                        <img src="${s.activeImage}" class="sat-viewport-img" alt="After Satellite Pass">
                                    </div>
                                </div>
                            ` : `
                                <img src="${s.activeImage}" class="sat-viewport-img ${s.showHeatmap ? "with-blend" : ""}" alt="Live Satellite Monitoring Swath">
                                ${s.showHeatmap ? `<div class="sat-heatmap-overlay"></div>` : ""}
                                ${s.showBoundingBoxes ? `
                                    <svg class="sat-bbox-svg" viewBox="0 0 800 450" preserveAspectRatio="none">
                                        <rect x="240" y="140" width="310" height="200" class="sat-bbox-rect-red" />
                                        <rect x="250" y="150" width="130" height="24" rx="4" fill="#ef4444" />
                                        <text x="256" y="166" class="sat-bbox-text">FLOOD INUNDATION: 94.7%</text>

                                        <rect x="110" y="80" width="180" height="130" class="sat-bbox-rect-amber" />
                                        <rect x="120" y="90" width="140" height="24" rx="4" fill="#f59e0b" />
                                        <text x="126" y="106" class="sat-bbox-text">INFRASTRUCTURE RISK</text>
                                    </svg>
                                ` : ""}
                            `}
                        </div>
                    </div>
                </div>

            </div>

            <!-- DISASTER ANALYSIS SIDEBAR (RIGHT SIDE) -->
            <div class="disaster-analysis-sidebar">
                <div class="sidebar-title-header">
                    <span>Disaster Analysis</span>
                    <span style="font-size: 11px; color: #10b981; font-weight: 700;">● LIVE TELEMETRY</span>
                </div>

                <div class="analysis-type-card">
                    <span class="analysis-type-icon">${s.disasterIcon}</span>
                    <div class="analysis-type-info">
                        <h4>${s.disasterType}</h4>
                        <p>Detected via Sentinel-2 Spectral Fusion</p>
                    </div>
                </div>

                <div class="analysis-confidence-card">
                    <div class="confidence-header">
                        <span>AI Confidence Score</span>
                        <strong>${s.confidence}%</strong>
                    </div>
                    <div class="confidence-bar-track">
                        <div class="confidence-bar-fill" style="width: ${s.confidence}%;"></div>
                    </div>
                </div>

                <div class="analysis-metrics-list">
                    <div class="analysis-metric-row">
                        <span>Affected Area</span>
                        <strong class="highlight-orange">${s.affectedArea}</strong>
                    </div>

                    <div class="analysis-metric-row">
                        <span>Population at Risk</span>
                        <strong class="highlight-cyan">${s.populationRisk}</strong>
                    </div>

                    <div class="analysis-metric-row">
                        <span>Severity Index</span>
                        <strong class="highlight-red">${s.severityScore}</strong>
                    </div>

                    <div class="analysis-metric-row">
                        <span>Coordinates</span>
                        <strong style="font-size: 11px; opacity: 0.9;">${s.coordinates}</strong>
                    </div>
                </div>
            </div>

        </div>
    `;
}

/* =========================================================
   DASHBOARD
========================================================= */

async function showDashboard() {

    const stats = nirvaanData.statistics;
    const latest = await getLatestDisaster();
    const satellite = await getSatelliteImages();

    const affectedArea = (latest && latest.affectedArea) ? latest.affectedArea : "14.2 km²";
    const popRisk = "12,500";
    const accuracy = "94.7%";

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

        <section class="dashboard-section nirvaan-dashboard-container">

            <div style="margin-bottom: 4px;">
                <h1 class="page-title" style="margin-bottom: 4px;">
                    Dashboard
                </h1>
                <p class="page-subtitle" style="margin: 0;">
                    Real-time AI Disaster Monitoring, Geospatial Satellite Telemetry & Risk Intelligence
                </p>
            </div>

            <!-- THREE TOP METRIC CARDS WITH TREND ARROWS & PERCENTAGE CHANGES -->
            <div class="metric-cards-grid">
                <div class="metric-card-box">
                    <div class="metric-card-icon area">📍</div>
                    <div class="metric-card-info">
                        <span class="metric-card-label">Affected Area</span>
                        <span class="metric-card-val">${affectedArea}</span>
                        <span class="metric-card-trend up-orange">↑ 12.6% vs yesterday</span>
                    </div>
                </div>

                <div class="metric-card-box">
                    <div class="metric-card-icon pop">👥</div>
                    <div class="metric-card-info">
                        <span class="metric-card-label">Population at Risk</span>
                        <span class="metric-card-val">${popRisk}</span>
                        <span class="metric-card-trend up-cyan">↑ 8.4% vs yesterday</span>
                    </div>
                </div>

                <div class="metric-card-box">
                    <div class="metric-card-icon accuracy">◎</div>
                    <div class="metric-card-info">
                        <span class="metric-card-label">Detection Accuracy</span>
                        <span class="metric-card-val">${accuracy}</span>
                        <span class="metric-card-trend up-green">↑ 3.2% vs yesterday</span>
                    </div>
                </div>
            </div>

            <!-- SATELLITE MONITORING PANEL & DISASTER ANALYSIS SIDEBAR -->
            <div id="satMonitoringSectionContainer">
                ${renderSatelliteMonitoringHTML()}
            </div>

            <!-- RISK ANALYSIS SECTION WITH ICONS FOR INFRASTRUCTURE, HEALTH, AND EVACUATION -->
            <div class="risk-analysis-section">
                <div class="risk-section-header">
                    <h2><span>🛡️</span> Risk Analysis</h2>
                    <p>Multi-hazard structural, health, and evacuation intelligence synthesized from real-time raster telemetry</p>
                </div>

                <div class="risk-cards-grid">
                    <!-- INFRASTRUCTURE IMPACT -->
                    <div class="risk-card-item">
                        <div class="risk-card-header">
                            <div class="risk-icon-badge infra">🏗️</div>
                            <span class="risk-badge-tag amber">2 CRITICAL ASSETS</span>
                        </div>
                        <div class="risk-card-body">
                            <h3>Infrastructure Impact</h3>
                            <p>Geospatial Structural Assessment</p>
                            <div class="risk-bullets">
                                <div class="risk-bullet-row">
                                    <span>⚠️</span>
                                    <span><strong>SP25 Highway Bridge</strong>: 0.8 km from hotspot — Structural inundation alert</span>
                                </div>
                                <div class="risk-bullet-row">
                                    <span>⚡</span>
                                    <span><strong>Regional Substation 4</strong>: Flood perimeter encroachment risk</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- HEALTH RISKS -->
                    <div class="risk-card-item">
                        <div class="risk-card-header">
                            <div class="risk-icon-badge health">🏥</div>
                            <span class="risk-badge-tag cyan">MODERATE HAZARD</span>
                        </div>
                        <div class="risk-card-body">
                            <h3>Health Risks</h3>
                            <p>Waterborne Hazards & Contamination</p>
                            <div class="risk-bullets">
                                <div class="risk-bullet-row">
                                    <span>🌊</span>
                                    <span><strong>Waterborne Exposure</strong>: High NDWI anomaly indicates drainage backup</span>
                                </div>
                                <div class="risk-bullet-row">
                                    <span>🏥</span>
                                    <span><strong>Hospital Access</strong>: Perimeter clearance required for Regional Facility</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- EVACUATION SUGGESTED -->
                    <div class="risk-card-item">
                        <div class="risk-card-header">
                            <div class="risk-icon-badge evac">🚨</div>
                            <span class="risk-badge-tag red">ZONE B-4 DISPATCH</span>
                        </div>
                        <div class="risk-card-body">
                            <h3>Evacuation Suggested</h3>
                            <p>Emergency Dispatch & Advisory</p>
                            <div class="risk-bullets">
                                <div class="risk-bullet-row">
                                    <span>📢</span>
                                    <span><strong>Sector B-4 Lowlands</strong>: Priority 1 evacuation advised (~12,500 residents)</span>
                                </div>
                                <div class="risk-bullet-row">
                                    <span>🚗</span>
                                    <span><strong>Corridor Route</strong>: Proceed North via SP25 Bypass Clearway</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- MULTI-TEMPORAL SATELLITE COMPARISON SHOWCASE -->
            <div class="panel" style="width: 100%;">
                <div class="panel-header">
                    <h2>🛰 Multi-Temporal Satellite Image Showcase</h2>
                    <button onclick="loadPage('satellite')">View Fullscreen Monitor</button>
                </div>
                ${satelliteHtml}
            </div>

            <!-- ABOUT NIRVAAN SECTION -->
            <div class="panel" style="width: 100%; padding: 32px; border-radius: 16px; margin-top: 24px; background: rgba(13, 19, 33, 0.72); border: 1px solid rgba(56, 189, 248, 0.28);">
                <h2 style="margin-bottom: 16px; color: #38bdf8; font-size: 22px; font-weight: 800; display: flex; align-items: center; gap: 10px;">
                    <span>🌐</span> About Nirvaan
                </h2>
                <p style="font-size: 16px; line-height: 1.8; color: #e0e0e0; margin-bottom: 24px;">
                    <strong>Nirvaan</strong> is an advanced, satellite-driven disaster intelligence engine engineered to perform <strong>rapid disaster detection</strong>, <strong>inundated area mapping</strong>, and <strong>real-time situational risk assessment</strong>. By fusing multi-spectral satellite imagery (Copernicus Sentinel-2, USGS Landsat-9) with deep learning segmentation neural networks, Nirvaan equips emergency response managers with sub-hour actionable intelligence.
                </p>

                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20px;">
                    <div class="card" style="padding: 24px; border-radius: 14px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08);">
                        <h3 style="margin-bottom: 10px; color: #38bdf8; font-size: 17px; font-weight: 700;">🛰 Multi-Spectral Imagery</h3>
                        <p style="font-size: 14.5px; line-height: 1.7; color: #a1a1aa;">
                            Automated extraction of <strong>NDWI (Water Index)</strong> and <strong>SAR (Synthetic Aperture Radar)</strong> masks to detect flood extent through heavy cloud cover.
                        </p>
                    </div>

                    <div class="card" style="padding: 24px; border-radius: 14px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08);">
                        <h3 style="margin-bottom: 10px; color: #38bdf8; font-size: 17px; font-weight: 700;">⚡ Rapid Early Warning</h3>
                        <p style="font-size: 14.5px; line-height: 1.7; color: #a1a1aa;">
                            Sub-hour automated pipeline processing raw satellite swaths into <strong>high-resolution vector risk maps</strong> and automated broadcasts.
                        </p>
                    </div>

                    <div class="card" style="padding: 24px; border-radius: 14px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08);">
                        <h3 style="margin-bottom: 10px; color: #38bdf8; font-size: 17px; font-weight: 700;">📊 Population & Asset Risk</h3>
                        <p style="font-size: 14.5px; line-height: 1.7; color: #a1a1aa;">
                            Spatial demographic overlay calculating <strong>affected populations</strong>, <strong>submerged roadways</strong>, and <strong>critical infrastructure</strong>.
                        </p>
                    </div>

                    <div class="card" style="padding: 24px; border-radius: 14px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08);">
                        <h3 style="margin-bottom: 10px; color: #38bdf8; font-size: 17px; font-weight: 700;">🛡️ Inter-Agency Interoperability</h3>
                        <p style="font-size: 14.5px; line-height: 1.7; color: #a1a1aa;">
                            Seamless GIS spatial telemetry exchange with <strong>NDMA</strong>, <strong>ISRO</strong>, and <strong>State Disaster Relief Forces</strong>.
                        </p>
                    </div>
                </div>
            </div>

            <!-- FREQUENTLY ASKED QUESTIONS (FAQ) SECTION -->
            <div class="panel" style="width: 100%; padding: 32px; border-radius: 16px; margin-top: 24px; background: rgba(13, 19, 33, 0.72); border: 1px solid rgba(56, 189, 248, 0.28);">
                <h2 style="margin-bottom: 16px; color: #38bdf8; font-size: 22px; font-weight: 800; display: flex; align-items: center; gap: 10px;">
                    <span>❓</span> Frequently Asked Questions (FAQ)
                </h2>
                <p style="font-size: 15px; margin-bottom: 24px; color: #94a3b8;">Learn more about Nirvaan satellite intelligence, metrics, and emergency response workflows.</p>

                <div style="display: flex; flex-direction: column; gap: 16px;">
                    <div style="padding: 20px; border-radius: 12px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08);">
                        <h4 style="margin-bottom: 8px; color: #38bdf8; font-size: 16px; font-weight: 800;">Q1: How does Nirvaan detect disaster affected zones?</h4>
                        <p style="font-size: 14.5px; line-height: 1.7; color: #e0e0e0; margin: 0;">
                            Nirvaan compares pre-event baseline scenes with post-event satellite imagery using optical spectral indices (<strong>NDWI</strong> for floods, <strong>dNBR</strong> for burn severity) and synthetic aperture radar (<strong>SAR</strong>) to identify flooded surfaces regardless of cloud cover.
                        </p>
                    </div>

                    <div style="padding: 20px; border-radius: 12px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08);">
                        <h4 style="margin-bottom: 8px; color: #38bdf8; font-size: 16px; font-weight: 800;">Q2: What satellite constellations are supported?</h4>
                        <p style="font-size: 14.5px; line-height: 1.7; color: #e0e0e0; margin: 0;">
                            Nirvaan natively ingests <strong>Copernicus Sentinel-2</strong> (Optical), <strong>Sentinel-1</strong> (C-Band Radar), <strong>USGS Landsat-8/9</strong>, and high-resolution <strong>PlanetScope (3m)</strong> imagery feeds via automated REST APIs.
                        </p>
                    </div>

                    <div style="padding: 20px; border-radius: 12px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08);">
                        <h4 style="margin-bottom: 8px; color: #38bdf8; font-size: 16px; font-weight: 800;">Q3: How frequently is the disaster risk map updated?</h4>
                        <p style="font-size: 14.5px; line-height: 1.7; color: #e0e0e0; margin: 0;">
                            Automated background tasks ingest new satellite passes as soon as they become available from orbital feeds (typically <strong>12 to 24-hour revisit cadence</strong>), instantly recalculating hazard boundaries.
                        </p>
                    </div>

                    <div style="padding: 20px; border-radius: 12px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08);">
                        <h4 style="margin-bottom: 8px; color: #38bdf8; font-size: 16px; font-weight: 800;">Q4: Can SITREP situational reports be exported?</h4>
                        <p style="font-size: 14.5px; line-height: 1.7; color: #e0e0e0; margin: 0;">
                            Yes, under the <strong>Reports</strong> tab, response leads can generate and export <strong>JSON metadata</strong>, <strong>GeoJSON impact vector boundaries</strong>, or formatted <strong>SITREP situation reports</strong>.
                        </p>
                    </div>

                    <div style="padding: 20px; border-radius: 12px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08);">
                        <h4 style="margin-bottom: 8px; color: #38bdf8; font-size: 16px; font-weight: 800;">Q5: How do first responders receive critical warnings?</h4>
                        <p style="font-size: 14.5px; line-height: 1.7; color: #e0e0e0; margin: 0;">
                            Whenever the AI neural network detects inundation confidence exceeding <strong>85%</strong>, automated push notifications and SMS warning broadcasts are immediately dispatched to registered emergency commanders.
                        </p>
                    </div>
                </div>
            </div>

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

            <h1 class="page-title" style="font-size: 28px; font-weight: 900; margin-bottom: 8px;">
                Satellite Monitor
            </h1>

            <p class="page-subtitle" style="font-size: 16px; margin-bottom: 24px;">
                Real-Time Orbital Swath Monitoring, Image Ingestion, AI Disaster Detection & Spectral Analysis
            </p>

            <!-- FULL SATELLITE MONITORING PANEL MODULE WITH EMBEDDED ORBIT CANVAS & AI CONTROLS -->
            <div id="satMonitoringSectionContainer" style="margin-bottom: 28px;">
                ${renderSatelliteMonitoringHTML()}
            </div>

            <!-- MULTI-SPECTRAL COMPARISON PANEL -->
            <div class="panel">
                <div class="panel-header">
                    <h2>
                        🛰 Live Satellite Multi-Spectral Analysis
                    </h2>
                    <button onclick="loadPage('satellite')">
                        ↻ Refresh Feed
                    </button>
                </div>
                ${satelliteContent}
            </div>

        </div>

    `);

    setTimeout(() => {
        initSatelliteOrbitBackground("embeddedOrbitCanvas");
    }, 50);

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
        initSatelliteOrbitBackground("embeddedOrbitCanvas");
    }, 50);
}


/* =========================================================
   INTERACTIVE DISASTER RISK MAP MODULE
========================================================= */

function showRiskMap() {

    setPageContent(`

        <h1 class="page-title" style="font-size: 28px; font-weight: 900; margin-bottom: 8px;">
            Disaster Risk Map
        </h1>

        <p class="page-subtitle" style="font-size: 16px; margin-bottom: 24px;">
            High-contrast geospatial intelligence, animated hazard overlays, glowing risk gradients & live spatial analytics
        </p>

        <!-- INTERACTIVE RISK MAP & SIDEBAR GRID -->
        <div class="risk-map-layout-grid">

            <!-- MAIN MAP VIEWPORT CONTAINER -->
            <div class="panel" style="padding: 24px; border-radius: 16px;">
                <!-- CONTROLS & LAYER FILTER TOOLBAR -->
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 18px; padding-bottom: 14px; border-bottom: 1px solid rgba(255,255,255,0.08);">
                    <div>
                        <h3 style="font-size: 17px; font-weight: 800; color: #38bdf8; margin: 0 0 4px 0; display: flex; align-items: center; gap: 8px;">
                            <span>🗺️</span> Interactive Geospatial Risk Engine
                        </h3>
                        <p style="font-size: 12px; color: #94a3b8; margin: 0;">Multi-hazard layer fusion with real-time telemetry updates</p>
                    </div>

                    <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                        <select id="mapLocationSelect" onchange="updateRiskMapLocation(this.value)" style="background: #1e2433; border: 1px solid rgba(255,255,255,0.15); color: #f1f5f9; padding: 8px 14px; border-radius: 8px; font-size: 12px; font-weight: 700; cursor: pointer;">
                            <option value="surat" selected>Surat Tapi Basin (Flood - HIGH)</option>
                            <option value="bhuj">Bhuj Kutch Fault Line (Seismic - HIGH)</option>
                            <option value="guwahati">Guwahati Brahmaputra (Flood - EXTREME)</option>
                            <option value="chennai">Chennai Coastal Zone (Tsunami - WATCH)</option>
                        </select>

                        <div class="sat-btn-group-toggles">
                            <button onclick="toggleMapLayer('flood')" class="sat-action-btn toggle active" id="layerBtnFlood">🌊 Flood</button>
                            <button onclick="toggleMapLayer('fault')" class="sat-action-btn toggle" id="layerBtnFault">⚡ Fault Line</button>
                            <button onclick="toggleMapLayer('tsunami')" class="sat-action-btn toggle" id="layerBtnTsunami">🏖️ Tsunami</button>
                            <button onclick="toggleMapLayer('all')" class="sat-action-btn toggle" id="layerBtnAll">🎯 All Hazards</button>
                        </div>
                    </div>
                </div>

                <!-- VIEWPORT MAP DISPLAY CANVAS -->
                <div class="risk-map-viewport" id="riskMapViewport">
                    <div class="risk-map-bg-grid"></div>

                    <!-- VECTOR HAZARD OVERLAY SVG -->
                    <svg style="position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none;" viewBox="0 0 800 520">
                        <!-- RIVER / FLOOD INUNDATION PATH -->
                        <path id="svgPathFlood" d="M -50 260 Q 200 180 400 280 T 850 240" fill="none" stroke="rgba(56, 189, 248, 0.45)" stroke-width="28" stroke-linecap="round" />
                        <path id="svgPathFloodCore" d="M -50 260 Q 200 180 400 280 T 850 240" fill="none" stroke="rgba(239, 68, 68, 0.55)" stroke-width="12" stroke-linecap="round" stroke-dasharray="8 4" />

                        <!-- SEISMIC FAULT LINE -->
                        <path id="svgPathFault" d="M 120 -50 L 320 220 L 520 380 L 780 580" fill="none" stroke="rgba(245, 158, 11, 0.6)" stroke-width="3" stroke-dasharray="10 6" />

                        <!-- TSUNAMI COASTLINE SURGE BOUNDARY -->
                        <path id="svgPathTsunami" d="M 680 -50 C 640 180 720 340 620 580" fill="none" stroke="rgba(6, 182, 212, 0.7)" stroke-width="18" stroke-dasharray="14 6" />
                    </svg>

                    <!-- GLOWING RADIAL GRADIENT RISK ZONES -->
                    <!-- RED ZONE (CRITICAL) -->
                    <div class="risk-zone-radial red" id="mapZoneRed" style="top: 52%; left: 48%; width: 180px; height: 180px;" onclick="showMapTooltip('red')"></div>
                    <div class="risk-map-pin red" style="top: 52%; left: 48%;" onclick="showMapTooltip('red')" title="Click for Flood Depth & Confidence">📍</div>

                    <!-- ORANGE ZONE (WARNING BUFFER) -->
                    <div class="risk-zone-radial orange" id="mapZoneOrange" style="top: 38%; left: 34%; width: 240px; height: 240px;" onclick="showMapTooltip('orange')"></div>
                    <div class="risk-map-pin orange" style="top: 38%; left: 34%;" onclick="showMapTooltip('orange')" title="Click for Flood Depth & Confidence">⚠️</div>

                    <!-- GREEN ZONE (SAFE RELIEF ZONE) -->
                    <div class="risk-zone-radial green" id="mapZoneGreen" style="top: 24%; left: 20%; width: 300px; height: 300px;" onclick="showMapTooltip('green')"></div>
                    <div class="risk-map-pin green" style="top: 24%; left: 20%;" onclick="showMapTooltip('green')" title="Click for Relief Shelter Info">🟢</div>

                    <!-- INTERACTIVE TOOLTIP MODAL -->
                    <div class="map-tooltip-card" id="mapTooltipCard" style="bottom: 24px; left: 24px; opacity: 1;">
                        <div class="map-tooltip-header">
                            <h4 id="tooltipTitle">📍 Surat Tapi River Basin</h4>
                            <span class="map-tooltip-badge" id="tooltipBadge" style="background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid #ef4444;">CRITICAL RISK</span>
                        </div>
                        <div class="map-tooltip-row"><span>Hazard Type:</span><strong id="tooltipHazard">Flood Inundation</strong></div>
                        <div class="map-tooltip-row"><span>Water Depth:</span><strong id="tooltipDepth" style="color: #ef4444;">2.4 meters</strong></div>
                        <div class="map-tooltip-row"><span>AI Confidence:</span><strong id="tooltipConfidence" style="color: #38bdf8;">94.7% (U-Net)</strong></div>
                        <div class="map-tooltip-row"><span>Population at Risk:</span><strong id="tooltipPop">12,500 residents</strong></div>
                        <div style="font-size: 10px; color: #94a3b8; margin-top: 8px; text-align: right;">Updated 12 mins ago (Sentinel-2 L2A)</div>
                    </div>

                    <!-- CLICKABLE LEGEND BADGE -->
                    <div style="position: absolute; top: 16px; right: 16px; background: rgba(11, 16, 28, 0.9); backdrop-filter: blur(12px); padding: 12px 16px; border-radius: 12px; border: 1px solid rgba(56, 189, 248, 0.3); font-size: 11px;">
                        <div style="font-weight: 800; color: #38bdf8; margin-bottom: 8px; letter-spacing: 0.5px;">MAP LEGEND</div>
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px; cursor: pointer;" onclick="showMapTooltip('red')"><span style="width: 12px; height: 12px; background: #ef4444; border-radius: 50%; display: inline-block; box-shadow: 0 0 8px #ef4444;"></span> <strong>Critical Risk Zone</strong> (High Depth)</div>
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px; cursor: pointer;" onclick="showMapTooltip('orange')"><span style="width: 12px; height: 12px; background: #f97316; border-radius: 50%; display: inline-block; box-shadow: 0 0 8px #f97316;"></span> <strong>Warning Buffer</strong> (Perimeter)</div>
                        <div style="display: flex; align-items: center; gap: 8px; cursor: pointer;" onclick="showMapTooltip('green')"><span style="width: 12px; height: 12px; background: #22c55e; border-radius: 50%; display: inline-block; box-shadow: 0 0 8px #22c55e;"></span> <strong>Safe Relief Zone</strong> (0.0m Depth)</div>
                    </div>
                </div>
            </div>

            <!-- LIVE SPATIAL ANALYTICS SIDEBAR -->
            <div class="spatial-analytics-sidebar">
                <div>
                    <h3 style="font-size: 16px; color: #38bdf8; font-weight: 800; margin: 0 0 16px 0; display: flex; align-items: center; gap: 8px;">
                        <span>📊</span> Spatial Analytics
                    </h3>

                    <div style="display: flex; flex-direction: column; gap: 16px;">
                        <!-- ACTIVE MONITORED ZONES -->
                        <div style="background: rgba(255,255,255,0.04); padding: 14px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.08);">
                            <span style="font-size: 11px; color: #94a3b8; font-weight: 700;">ACTIVE RISK HOTSPOTS</span>
                            <div style="font-size: 22px; font-weight: 900; color: #ef4444; margin-top: 4px;" id="riskHotspotsVal">3 Zones Active</div>
                            <span style="font-size: 11px; color: #cbd5e1;">Critical inundation in Tapi river corridor</span>
                        </div>

                        <!-- LAST SATELLITE PASS TIME -->
                        <div style="background: rgba(255,255,255,0.04); padding: 14px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.08);">
                            <span style="font-size: 11px; color: #94a3b8; font-weight: 700;">LAST SATELLITE PASS TIME</span>
                            <div style="font-size: 15px; font-weight: 800; color: #38bdf8; margin-top: 4px;">12 mins ago</div>
                            <span style="font-size: 11px; color: #cbd5e1;">Sentinel-2 L2A (Swath #4829)</span>
                        </div>

                        <!-- SPATIAL TREND GAUGES -->
                        <div style="background: rgba(255,255,255,0.04); padding: 14px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.08);">
                            <div style="display: flex; justify-content: space-between; font-size: 12px;">
                                <span style="color: #94a3b8; font-weight: 700;">Inundation Velocity</span>
                                <strong style="color: #ef4444;">+14.2% / hr</strong>
                            </div>
                            <div class="trend-progress-bar">
                                <div class="trend-progress-fill" style="width: 76%; background: linear-gradient(90deg, #f97316, #ef4444);"></div>
                            </div>
                        </div>

                        <div style="background: rgba(255,255,255,0.04); padding: 14px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.08);">
                            <div style="display: flex; justify-content: space-between; font-size: 12px;">
                                <span style="color: #94a3b8; font-weight: 700;">Relief Center Readiness</span>
                                <strong style="color: #22c55e;">91% Ready</strong>
                            </div>
                            <div class="trend-progress-bar">
                                <div class="trend-progress-fill" style="width: 91%; background: linear-gradient(90deg, #10b981, #22c55e);"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <button class="sat-action-btn upload" style="width: 100%; justify-content: center; padding: 12px; font-size: 13px;" onclick="alert('Exporting high-resolution GeoJSON risk map layer...')">
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