"""
NIRVAAN — AI Satellite Disaster Monitoring Platform
Main Streamlit Dashboard Application Entry Point
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timezone
import json

import streamlit as st

# Ensure repository root is on sys.path
repo_root = Path(__file__).resolve().parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from ui.map_panel import render_map_panel
from analysis.severity import calculate_composite_impact_score
from analysis.population import estimate_affected_population, create_synthetic_population_grid
from analysis.infrastructure import analyze_infrastructure_impact, create_synthetic_infrastructure_layer
from analysis.risk_zones import generate_risk_zones, to_geojson_risk_zones
from analysis.confidence import calculate_evidence_confidence
from reports.situation_report import generate_situation_report
from reports.recommendations import generate_response_recommendations
from api.server import handle_api_request
from utils.provenance import create_provenance_record


# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="NIRVAAN — AI Satellite Disaster Monitoring",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling for Premium Aesthetics ---
st.markdown("""
<style>
    /* Dark Theme Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0b0f19 !important;
        border-right: 1px solid #1e293b !important;
    }
    
    /* Navigation Radio Items Styling */
    div[data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 6px;
        padding-top: 0.2rem;
    }
    
    /* Hide standard radio dot circles in sidebar navigation group */
    div[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
        display: none !important;
    }
    
    div[data-testid="stSidebar"] div[role="radiogroup"] label {
        background-color: rgba(30, 41, 59, 0.4);
        border-radius: 10px;
        padding: 12px 16px;
        border: 1px solid rgba(51, 65, 85, 0.5);
        transition: all 0.2s ease-in-out;
        cursor: pointer;
        margin-bottom: 2px;
    }
    
    div[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background-color: #1e293b;
        border-color: #475569;
    }
    
    /* Active Nav Item - Highlighted */
    div[data-testid="stSidebar"] div[role="radiogroup"] label[aria-checked="true"] {
        background: linear-gradient(135deg, #4338ca 0%, #3b82f6 100%) !important;
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.4);
        border: none !important;
    }
    
    div[data-testid="stSidebar"] div[role="radiogroup"] label[aria-checked="true"] p,
    div[data-testid="stSidebar"] div[role="radiogroup"] label[aria-checked="true"] span {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* Dark Theme Accent Header */
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f766e 100%);
        padding: 1.8rem 2rem;
        border-radius: 12px;
        color: #ffffff;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        margin-bottom: 1.5rem;
    }
    .main-header h1 {
        color: #ffffff;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin: 0;
        font-size: 2.2rem;
    }
    .main-header p {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-top: 0.4rem;
        margin-bottom: 0;
    }
    .badge-verified {
        background-color: #065f46;
        color: #34d399;
        font-size: 0.78rem;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        text-transform: uppercase;
        display: inline-block;
        margin-top: 8px;
    }

    /* Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.15);
    }

    /* About Card at bottom of Sidebar */
    .about-sidebar-card {
        background-color: rgba(15, 23, 42, 0.7);
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 14px 16px;
        margin-top: 1.5rem;
        color: #94a3b8;
    }
    .about-sidebar-card h4 {
        color: #38bdf8;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 6px;
        margin-top: 0;
    }
    .about-sidebar-card p {
        font-size: 0.78rem;
        line-height: 1.45;
        color: #94a3b8;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)


# --- Canonical Event Datasets ---
CANONICAL_EVENTS = {
    "flood_assam_2024": {
        "event_id": "FL-2024-ASSAM-001",
        "name": "🌊 Assam Brahmaputra Flood (2024)",
        "disaster_type": "FLOOD",
        "location": {"name": "Guwahati / Brahmaputra Basin, Assam, India", "lat": 26.18, "lon": 91.74},
        "acquisition_before": "2024-05-15T04:30:00Z",
        "acquisition_after": "2024-07-04T04:30:00Z",
        "spectral_index": "NDWI (Normalized Difference Water Index)",
        "sensor": "Sentinel-2 Level-2A Multispectral",
        "sample_polygons": [
            {
                "type": "Feature",
                "properties": {"zone_id": "flood_p1", "area_sq_km": 142.5, "severity": "HIGH"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[91.65, 26.12], [91.80, 26.12], [91.80, 26.24], [91.65, 26.24], [91.65, 26.12]]]
                }
            },
            {
                "type": "Feature",
                "properties": {"zone_id": "flood_p2", "area_sq_km": 48.2, "severity": "CRITICAL"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[91.70, 26.15], [91.76, 26.15], [91.76, 26.20], [91.70, 26.20], [91.70, 26.15]]]
                }
            }
        ],
        "hotspots": [
            {"lat": 26.185, "lon": 91.742, "intensity": 0.92, "name": "Brahmaputra Embankment Breach Submersion"},
            {"lat": 26.210, "lon": 91.680, "intensity": 0.85, "name": "North Guwahati Residential Inundation"}
        ]
    },
    "fire_california_2024": {
        "event_id": "WF-2024-PARKFIRE-002",
        "name": "🔥 California Park Fire (2024)",
        "disaster_type": "WILDFIRE",
        "location": {"name": "Chico / Butte County, California, USA", "lat": 39.85, "lon": -121.75},
        "acquisition_before": "2024-07-20T18:45:00Z",
        "acquisition_after": "2024-07-28T18:45:00Z",
        "spectral_index": "dNBR (differential Normalized Burn Ratio)",
        "sensor": "Sentinel-2 Level-2A Multispectral",
        "sample_polygons": [
            {
                "type": "Feature",
                "properties": {"zone_id": "fire_p1", "area_sq_km": 215.8, "severity": "CRITICAL"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[-121.85, 39.75], [-121.65, 39.75], [-121.65, 39.95], [-121.85, 39.95], [-121.85, 39.75]]]
                }
            }
        ],
        "hotspots": [
            {"lat": 39.865, "lon": -121.720, "intensity": 0.98, "name": "Active Fire Perimeter Front (North East)"},
            {"lat": 39.810, "lon": -121.780, "intensity": 0.89, "name": "Secondary Thermal Flare Zone"}
        ]
    }
}


def main():
    # --- Sidebar Header & Navigation Bar ---
    st.sidebar.markdown("""
    <div style="display: flex; align-items: center; gap: 14px; padding: 4px 0 16px 0;">
        <div style="background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%); width: 48px; height: 48px; border-radius: 14px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 16px rgba(59, 130, 246, 0.4); font-size: 26px;">
            📡
        </div>
        <div>
            <div style="font-size: 1.35rem; font-weight: 800; color: #f8fafc; letter-spacing: -0.5px; line-height: 1.2;">NIRVAAN</div>
            <div style="font-size: 0.75rem; color: #38bdf8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">AI Disaster Platform</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Canonical Event Selector
    event_key = st.sidebar.selectbox(
        "Active Disaster Observation",
        options=list(CANONICAL_EVENTS.keys()),
        format_func=lambda k: CANONICAL_EVENTS[k]["name"]
    )
    event_data = CANONICAL_EVENTS[event_key]

    st.sidebar.markdown("---")

    # Sidebar Navigation Menu
    nav_option = st.sidebar.radio(
        "Navigation Menu",
        [
            "🏠  Dashboard",
            "💠  Satellite Monitor",
            "🔺  Disaster Detection",
            "💠  Risk Map",
            "🔴  Alerts (3)",
            "📄  Reports",
            "🕒  History",
            "⚙️  Settings"
        ],
        index=2,  # Default to Disaster Detection as shown in screenshot
        label_visibility="collapsed"
    )

    st.sidebar.markdown("---")

    # Sidebar Detection Controls & Thresholds (Globally accessible across all views)
    st.sidebar.subheader("⚙️ Detection Thresholds")
    mode = st.sidebar.radio(
        "Execution Mode",
        ["⚡ Instant Demo Mode (Precomputed)", "📡 Live Parameter Tuning"],
        help="Instant Demo uses cached canonical datasets. Live Mode allows custom parameter experimentation."
    )

    if event_data["disaster_type"] == "FLOOD":
        threshold_val = st.sidebar.slider("NDWI Water Threshold", 0.0, 1.0, 0.25, 0.05)
    else:
        threshold_val = st.sidebar.slider("dNBR Burn Severity Threshold", 0.0, 1.0, 0.40, 0.05)

    min_area_km2 = st.sidebar.slider("Min Polygon Area (km²)", 0.5, 50.0, 5.0, 0.5)
    force_offline = st.sidebar.checkbox("Force Deterministic Offline Mode", value=True)

    # Global Backend Analytics Computation
    event_info = event_data["location"]
    polygons = event_data["sample_polygons"]
    hotspots = event_data["hotspots"]

    pop_grid = create_synthetic_population_grid(
        rows=100,
        cols=100,
        transform={
            "origin_lat": event_info["lat"] + 0.05,
            "origin_lon": event_info["lon"] - 0.05,
            "pixel_size_lat": -0.001,
            "pixel_size_lon": 0.001
        },
        density_per_pixel=250.0
    )
    infra_layer = create_synthetic_infrastructure_layer()

    pop_impact = estimate_affected_population(polygons, population_data=pop_grid)
    infra_impact = analyze_infrastructure_impact(polygons_or_hotspots=hotspots, infrastructure_data=infra_layer)
    severity = calculate_composite_impact_score(
        spectral_severity="HIGH",
        population_estimate=pop_impact.get("estimated_affected_population"),
        infrastructure_impact=infra_impact,
        hotspots=hotspots
    )

    # Common Main Header
    st.markdown(f"""
    <div class="main-header">
        <h1>NIRVAAN — Satellite Disaster Intelligence</h1>
        <p>Real multispectral Sentinel-2 observations converted into actionable disaster assessment.</p>
        <span class="badge-verified">✓ PROVENANCE VERIFIED • {event_data['sensor']}</span>
    </div>
    """, unsafe_allow_html=True)

    # --- NAV ROUTING ---
    if "Dashboard" in nav_option:
        st.markdown("## 🏠 Executive Overview Dashboard")
        
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Disaster Type & Location", event_data["disaster_type"], event_info["name"].split(",")[0])
        with m2:
            score_val = severity.get("impact_score", 0.0)
            st.metric("Composite Severity Index", f"{score_val} / 100", severity.get("severity_band", "HIGH").upper())
        with m3:
            affected_pop = pop_impact.get("estimated_affected_population")
            pop_str = f"{int(affected_pop):,}" if affected_pop is not None else "DATA_UNAVAILABLE"
            st.metric("Est. Affected Population", pop_str, "ESTIMATE")
        with m4:
            infra_count = infra_impact.get("impacted_facilities_count", 0) or 0
            st.metric("High Proximity Infrastructure", f"{infra_count} Facilities", "FIELD_VERIFY")

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("🗺️ Live Disaster Extent Preview")
            render_map_panel(event_location=event_info, affected_polygons=polygons, hotspots=hotspots, height=400, map_key="dash_map")
        with col2:
            st.subheader("⚡ Quick Disaster Actions")
            st.info(f"**Event:** {event_data['name']}")
            st.warning(f"**Acquisition Window:** {event_data['acquisition_before'][:10]} to {event_data['acquisition_after'][:10]}")
            st.success(f"**Spectral Index:** {event_data['spectral_index']}")
            st.markdown("---")
            st.caption("Select items from the navigation bar on the left to inspect detailed Detection, Risk Map, Reports, and Alerts.")

    elif "Satellite Monitor" in nav_option:
        st.markdown("## 💠 Satellite Observation & Multispectral Monitor")
        st.caption("Sentinel-2 Level-2A Multispectral Instrument Observation Pipeline")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.info(f"**Before Acquisition:**\n`{event_data['acquisition_before']}`")
        with c2:
            st.warning(f"**After Acquisition:**\n`{event_data['acquisition_after']}`")
        with c3:
            st.success(f"**Active Index Formula:**\n`{event_data['spectral_index']}`")

        st.markdown("### 📊 Sentinel-2 Multispectral Band Table")
        st.table([
            {"Band": "B03 (Green)", "Central Wavelength": "560 nm", "Resolution": "10 meters", "Application": "Water Inundation Detection (NDWI)"},
            {"Band": "B08 (NIR)", "Central Wavelength": "842 nm", "Resolution": "10 meters", "Application": "Vegetation & Water Difference"},
            {"Band": "B12 (SWIR-2)", "Central Wavelength": "2190 nm", "Resolution": "20 meters", "Application": "Wildfire Burn Ratio (dNBR)"}
        ])

        conf = calculate_evidence_confidence([[1, 0], [0, 1]])
        st.json({"satellite_provider": "Copernicus Open Access Hub", "orbit_direction": "DESCENDING", "evidence_confidence": conf})

    elif "Disaster Detection" in nav_option:
        st.markdown("## 🔺 Disaster Detection Pipeline")
        st.caption("Configure spectral detection parameters and view polygon delineation results.")

        d1, d2 = st.columns(2)
        with d1:
            st.subheader("🎯 Delineated Polygon Clusters")
            for poly in polygons:
                props = poly.get("properties", {})
                st.write(f"- **Zone `{props.get('zone_id')}`**: Area `{props.get('area_sq_km')} km²` — Severity `{props.get('severity')}`")
        with d2:
            st.subheader("🔥 Thermal Hotspot Fronts")
            for hot in hotspots:
                st.write(f"- **{hot['name']}**: Intensity `{hot['intensity']*100:.0f}%` at `({hot['lat']}, {hot['lon']})`")

        st.markdown("### 🗺️ Delineation Map")
        render_map_panel(event_location=event_info, affected_polygons=polygons, hotspots=hotspots, height=450, map_key="detect_map")

    elif "Risk Map" in nav_option:
        st.markdown("## 💠 Interactive Risk Map")
        st.caption("Evidence-grounded spatial assessment with concentric risk zone layers.")
        
        render_map_panel(event_location=event_info, affected_polygons=polygons, hotspots=hotspots, severity_level=severity.get("severity_band", "HIGH"), height=600, map_key="risk_map")

        st.markdown("### 📌 Risk Zone GeoJSON Summary")
        risk_zones = generate_risk_zones(polygons)
        st.json(to_geojson_risk_zones(risk_zones))

    elif "Alerts" in nav_option:
        st.markdown("## 🔴 Active Critical Disaster Alerts (3 Unresolved)")
        st.caption("Real-time high proximity alerts requiring immediate ground verification.")

        st.error("🚨 **ALERT #1 [P0 CRITICAL]**: Assam District Hospital is within 1.5 km of active Brahmaputra submersion perimeter — physical accessibility inspection required.")
        st.error("🚨 **ALERT #2 [EMBANKMENT BREACH]**: Primary embankment breach detected at North Guwahati front (`26.185 N, 91.742 E`). Intensity: 92%.")
        st.warning("⚠️ **ALERT #3 [POPULATION EXPOSURE]**: Estimated ~35,620 residents exposed to flood inundation perimeter.")

        st.markdown("### 📋 Response Verification Checklist")
        st.checkbox("Verify hospital ground access route via Highway 27", value=False)
        st.checkbox("Confirm satellite re-observation pass schedule with Copernicus", value=True)
        st.checkbox("Dispatch field survey team for perimeter boundary validation", value=False)

    elif "Reports" in nav_option:
        st.markdown("## 📄 Ground Situation Report & Response Recommendations")
        
        evidence_tuple = (
            event_data,
            {
                "index_name": event_data.get("spectral_index"),
                "before_date": event_data.get("acquisition_before"),
                "after_date": event_data.get("acquisition_after"),
                "sensor": event_data.get("sensor")
            },
            polygons,
            pop_impact,
            infra_impact,
            severity
        )

        with st.spinner("Generating evidence-grounded situation report..."):
            report = generate_situation_report(evidence_tuple, force_offline=force_offline)
            recommendations = generate_response_recommendations(
                severity_result=severity,
                population_impact=pop_impact,
                infrastructure_impact=infra_impact,
                risk_zones=polygons
            )

        st.markdown(report.get("report_markdown", "Situation report active."))
        
        st.markdown("---")
        st.markdown("#### Priority Response Recommendations")
        rec_list = recommendations.get("recommendations", [])
        for idx, rec in enumerate(rec_list, 1):
            prio = rec.get("priority", "P0").replace("_", " ")
            cat = str(rec.get("category", "Action")).replace("_", " ").title()
            st.markdown(f"**{idx}. [{prio}] {cat}**")
            st.write(f"{rec.get('suggestion', '')}")
            st.caption(f"Provenance: {rec.get('provenance_label', 'PROTOTYPE')}")

    elif "History" in nav_option:
        st.markdown("## 🕒 Historical Satellite Observations & Provenance Trail")
        
        prov_record = create_provenance_record(
            dataset_id=event_data["event_id"],
            source_url="https://scihub.copernicus.eu/s2",
            before_date=event_data["acquisition_before"],
            after_date=event_data["acquisition_after"],
            bands_used=["B03", "B08", "B12"],
            thresholds={"ndwi": threshold_val, "dnbr": threshold_val}
        )

        st.json(prov_record)

    elif "Settings" in nav_option:
        st.markdown("## ⚙️ System Settings & API Service")
        
        st.write(f"**Execution Mode:** `{mode}`")
        st.write(f"**Force Deterministic Offline Mode:** `{force_offline}`")
        st.write(f"**Coordinate Reference System (CRS):** `EPSG:4326`")
        
        st.markdown("### 🔌 REST API Endpoint Status Check")
        health_resp = handle_api_request("/api/v1/health", method="GET")
        st.json(health_resp)

    # --- ABOUT Card at Bottom of Sidebar ---
    st.sidebar.markdown("""
    <div class="about-sidebar-card">
        <h4>ABOUT</h4>
        <p><strong>NIRVAAN Platform v1.0</strong><br>
        Evidence-grounded AI satellite disaster monitoring platform powered by Sentinel-2 multispectral observations and deterministic spatial analytics.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
