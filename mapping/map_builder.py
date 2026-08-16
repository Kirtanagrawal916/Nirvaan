"""
Folium Map Builder for NIRVAAN

Builds interactive maps rendering disaster event locations, affected polygons,
hotspots, custom severity legends, tooltips, and popups.
Handles missing or malformed metadata without crashing.
"""

from typing import Any, Dict, List, Optional, Tuple
import folium
from folium import plugins

from mapping.geojson import (
    validate_coordinates,
    calculate_bounds,
    create_point_feature,
    create_polygon_feature,
    create_feature_collection,
)

# Palette mapping for severity levels
SEVERITY_COLORS = {
    "low": "#f1c40f",       # Yellow
    "moderate": "#e67e22",  # Orange
    "high": "#e74c3c",      # Red
    "extreme": "#8e44ad",   # Purple
    "unknown": "#95a5a6",   # Gray
}


def get_severity_color(severity: Optional[str]) -> str:
    """Return hex color code corresponding to severity level."""
    if not severity or not isinstance(severity, str):
        return SEVERITY_COLORS["unknown"]
    sev_clean = severity.strip().lower()
    return SEVERITY_COLORS.get(sev_clean, SEVERITY_COLORS["high"])


def generate_severity_legend_html() -> str:
    """
    Generate accessible HTML legend for severity categories.
    """
    legend_html = """
    <div style="
        position: fixed; 
        bottom: 25px; 
        left: 25px; 
        width: 170px; 
        background-color: rgba(20, 24, 33, 0.9);
        color: #ffffff;
        border: 1px solid #34495e;
        border-radius: 8px;
        padding: 10px;
        font-family: Arial, sans-serif;
        font-size: 12px;
        z-index: 9999;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    " aria-label="Disaster Severity Legend" role="region">
        <div style="font-weight: bold; margin-bottom: 8px; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px;">
            Severity Index
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <span style="background-color: #8e44ad; width: 12px; height: 12px; display: inline-block; margin-right: 8px; border-radius: 2px;"></span>
            <span>Extreme</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <span style="background-color: #e74c3c; width: 12px; height: 12px; display: inline-block; margin-right: 8px; border-radius: 2px;"></span>
            <span>High</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <span style="background-color: #e67e22; width: 12px; height: 12px; display: inline-block; margin-right: 8px; border-radius: 2px;"></span>
            <span>Moderate</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <span style="background-color: #f1c40f; width: 12px; height: 12px; display: inline-block; margin-right: 8px; border-radius: 2px;"></span>
            <span>Low</span>
        </div>
    </div>
    """
    return legend_html


def build_folium_map(
    event_location: Optional[Dict[str, Any]] = None,
    affected_polygons: Optional[List[Dict[str, Any]]] = None,
    hotspots: Optional[List[Dict[str, Any]]] = None,
    severity_level: Optional[str] = "High",
    default_center: Tuple[float, float] = (20.0, 0.0),
    zoom_start: int = 10
) -> folium.Map:
    """
    Construct a Folium Map with layers for:
    - Event Location marker & popup
    - Affected Polygons (styled by severity)
    - Hotspots / Hotspot Clusters
    - Accessible HTML Severity Legend
    
    Fits map bounds automatically if valid geospatial coordinates exist.
    If geospatial metadata is missing or invalid, renders a default fallback map with a warning popup.
    """
    # Initialize base map centered on default location
    m = folium.Map(
        location=[default_center[0], default_center[1]],
        zoom_start=zoom_start,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    all_coordinates = []
    has_valid_geospatial_data = False

    # 1. Process Event Location Marker
    if event_location and isinstance(event_location, dict):
        lat = event_location.get("lat") or event_location.get("latitude")
        lon = event_location.get("lon") or event_location.get("longitude")
        name = event_location.get("name", "Disaster Event Location")
        disaster_type = event_location.get("type", "Disaster Event")
        
        if validate_coordinates(lat, lon):
            lat_f, lon_f = float(lat), float(lon)
            all_coordinates.append((lat_f, lon_f))
            has_valid_geospatial_data = True

            # Custom icon based on disaster type
            icon_name = "fire" if "fire" in str(disaster_type).lower() else "info-sign"
            icon_color = "red" if "fire" in str(disaster_type).lower() else "blue"

            popup_html = f"""
            <div style="font-family: Arial, sans-serif; width: 180px;">
                <h4 style="margin: 0 0 5px 0; color: #2c3e50;">{name}</h4>
                <p style="margin: 0; font-size: 12px;"><b>Type:</b> {disaster_type}</p>
                <p style="margin: 0; font-size: 12px;"><b>Severity:</b> {severity_level}</p>
                <p style="margin: 0; font-size: 11px; color: #7f8c8d;"><b>Lat/Lon:</b> {lat_f:.4f}, {lon_f:.4f}</p>
            </div>
            """
            
            folium.Marker(
                location=[lat_f, lon_f],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"{name} ({disaster_type})",
                icon=folium.Icon(color=icon_color, icon=icon_name, prefix="glyphicon")
            ).add_to(m)

    # 2. Process Affected Polygons Layer
    if affected_polygons and isinstance(affected_polygons, list):
        polygon_group = folium.FeatureGroup(name="Affected Areas")
        
        for idx, poly_data in enumerate(affected_polygons):
            coords = poly_data.get("coordinates", [])
            poly_sev = poly_data.get("severity", severity_level)
            area_km2 = poly_data.get("area_km2", "N/A")
            color = get_severity_color(poly_sev)

            valid_ring = []
            for pt in coords:
                if isinstance(pt, (list, tuple)) and len(pt) >= 2:
                    if validate_coordinates(pt[0], pt[1]):
                        lat, lon = float(pt[0]), float(pt[1])
                        valid_ring.append([lat, lon])
                        all_coordinates.append((lat, lon))

            if len(valid_ring) >= 3:
                has_valid_geospatial_data = True
                tooltip_text = f"Affected Area #{idx+1} | Severity: {poly_sev}"
                popup_html = f"""
                <div style="font-family: Arial, sans-serif;">
                    <h4 style="margin: 0 0 5px 0;">Affected Zone #{idx+1}</h4>
                    <p style="margin: 0; font-size: 12px;"><b>Severity:</b> {poly_sev}</p>
                    <p style="margin: 0; font-size: 12px;"><b>Estimated Area:</b> {area_km2} km²</p>
                </div>
                """
                folium.Polygon(
                    locations=valid_ring,
                    color=color,
                    weight=2,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.4,
                    tooltip=tooltip_text,
                    popup=folium.Popup(popup_html, max_width=250)
                ).add_to(polygon_group)
        
        polygon_group.add_to(m)

    # 3. Process Hotspots Layer
    if hotspots and isinstance(hotspots, list):
        hotspot_group = folium.FeatureGroup(name="Hotspots")

        for idx, hs in enumerate(hotspots):
            lat = hs.get("lat") or hs.get("latitude")
            lon = hs.get("lon") or hs.get("longitude")
            intensity = hs.get("intensity", hs.get("confidence", "High"))

            if validate_coordinates(lat, lon):
                lat_f, lon_f = float(lat), float(lon)
                all_coordinates.append((lat_f, lon_f))
                has_valid_geospatial_data = True

                popup_html = f"""
                <div style="font-family: Arial, sans-serif;">
                    <h5 style="margin: 0 0 4px 0; color: #c0392b;">Hotspot #{idx+1}</h5>
                    <p style="margin: 0; font-size: 11px;"><b>Intensity:</b> {intensity}</p>
                    <p style="margin: 0; font-size: 11px;"><b>Coords:</b> {lat_f:.4f}, {lon_f:.4f}</p>
                </div>
                """
                folium.CircleMarker(
                    location=[lat_f, lon_f],
                    radius=6,
                    color="#d35400",
                    fill=True,
                    fill_color="#e74c3c",
                    fill_opacity=0.8,
                    tooltip=f"Hotspot #{idx+1} (Intensity: {intensity})",
                    popup=folium.Popup(popup_html, max_width=200)
                ).add_to(hotspot_group)

        hotspot_group.add_to(m)

    # 4. Handle Map Fit Bounds or Graceful Missing Metadata Fallback
    bounds = calculate_bounds(all_coordinates) if all_coordinates else None
    if bounds:
        m.fit_bounds(bounds, padding=(30, 30))
    elif not has_valid_geospatial_data:
        # Add a warning marker if geospatial data is completely missing
        folium.Marker(
            location=[default_center[0], default_center[1]],
            popup=folium.Popup(
                "<b>No valid geospatial coordinates available</b><br>Displaying fallback regional view.",
                max_width=250
            ),
            tooltip="Geospatial Data Missing (Fallback View)",
            icon=folium.Icon(color="orange", icon="warning-sign", prefix="glyphicon")
        ).add_to(m)

    # 5. Add Legend and Layer Control
    folium.LayerControl(position="topright").add_to(m)
    m.get_root().html.add_child(folium.Element(generate_severity_legend_html()))

    return m
