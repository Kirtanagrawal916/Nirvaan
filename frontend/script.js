function setPageContent(html) {
    const container = document.getElementById("pageContent");

    if (container) {
        container.innerHTML = html;
    }
}


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
        prov =
            dataOrProvenance.data_provenance ||
            (dataOrProvenance.provenance &&
                dataOrProvenance.provenance.data_provenance) ||
            (dataOrProvenance.event_metadata &&
                dataOrProvenance.event_metadata.data_provenance) ||
            "SYNTHETIC_FALLBACK";
    }

    if (prov === "REAL_SATELLITE_DATA") {
        banner.className = "provenance-banner real-mode";

        banner.innerHTML = `
            <span class="banner-icon">🛰️</span>
            <span class="banner-text">
                <strong>REAL SATELLITE DATA</strong> —
                Processing genuine Sentinel-2 Level-2A surface reflectance imagery.
            </span>
        `;

        banner.style.display = "flex";
    } else {
        banner.className = "provenance-banner synthetic-mode";

        banner.innerHTML = `
            <span class="banner-icon">⚠️</span>
            <span class="banner-text">
                <strong>DEMO MODE: SYNTHETIC DATA</strong> —
                This view displays simulated/synthetic placeholder satellite data
                for demonstration purposes.
            </span>
        `;

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
    const savedTheme =
        localStorage.getItem("nirvaan_theme") || "dark";

    applyTheme(savedTheme);

    const themeSwitchWrapper =
        document.getElementById("themeSwitchWrapper");

    if (themeSwitchWrapper) {
        themeSwitchWrapper.addEventListener("click", () => {
            const currentTheme =
                document.documentElement.getAttribute("data-theme") ||
                "dark";

            const newTheme =
                currentTheme === "dark" ? "light" : "dark";

            applyTheme(newTheme);

            localStorage.setItem("nirvaan_theme", newTheme);
        });
    }

    const themePillBtns =
        document.querySelectorAll(".theme-pill-btn");

    themePillBtns.forEach((btn) => {
        btn.addEventListener("click", () => {
            const targetTheme = btn.dataset.themeSet;

            if (targetTheme) {
                applyTheme(targetTheme);
                localStorage.setItem(
                    "nirvaan_theme",
                    targetTheme
                );
            }
        });
    });
}


function applyTheme(theme) {
    document.documentElement.setAttribute(
        "data-theme",
        theme
    );

    const themeText =
        document.getElementById("themeToggleText");

    if (themeText) {
        themeText.textContent =
            theme === "dark" ? "Light Mode" : "Dark Mode";
    }

    const themePillBtns =
        document.querySelectorAll(".theme-pill-btn");

    themePillBtns.forEach((btn) => {
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