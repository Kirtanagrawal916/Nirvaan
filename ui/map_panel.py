"""
Streamlit Map Panel Component for NIRVAAN

Wraps the Folium map builder for seamless rendering in Streamlit dashboards using streamlit-folium.
Includes fallback handling when outside an active Streamlit app session.
"""

from typing import Any, Dict, List, Optional
import folium

try:
    from mapping.map_builder import build_folium_map
except ImportError:
    from ..mapping.map_builder import build_folium_map


def render_map_panel(
    event_location: Optional[Dict[str, Any]] = None,
    affected_polygons: Optional[List[Dict[str, Any]]] = None,
    hotspots: Optional[List[Dict[str, Any]]] = None,
    severity_level: Optional[str] = "High",
    height: int = 500,
    returned_objects: Optional[List[str]] = None,
    map_key: Optional[str] = None,
    use_container_width: bool = True
) -> Any:
    """
    Build and render the interactive Folium map in Streamlit.
    
    If running inside an active Streamlit app session (`st.runtime.exists()`), renders the map via `st_folium`.
    Otherwise (e.g. in test suites, CLI tools, or headless scripts), returns the `folium.Map` object.
    """
    folium_map = build_folium_map(
        event_location=event_location,
        affected_polygons=affected_polygons,
        hotspots=hotspots,
        severity_level=severity_level,
    )

    try:
        import streamlit as st
        # Only use streamlit rendering if running inside an active Streamlit server runtime
        if st.runtime.exists():
            from streamlit_folium import st_folium
            return st_folium(
                folium_map,
                use_container_width=use_container_width,
                height=height,
                returned_objects=returned_objects or [],
                key=map_key or "nirvaan_disaster_map"
            )
    except (ImportError, Exception):
        pass

    return folium_map
