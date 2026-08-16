"""
NIRVAAN Mapping Package
Provides GeoJSON utilities, geographic coordinate validation, Folium map builders, and Streamlit map display components.
"""

from mapping.geojson import (
    DEFAULT_CRS,
    validate_coordinates,
    parse_event_coordinates,
    parse_hotspot_coordinates,
    calculate_bounds,
    create_point_feature,
    create_polygon_feature,
    create_feature_collection,
)
from mapping.map_builder import build_folium_map

__all__ = [
    "DEFAULT_CRS",
    "validate_coordinates",
    "parse_event_coordinates",
    "parse_hotspot_coordinates",
    "calculate_bounds",
    "create_point_feature",
    "create_polygon_feature",
    "create_feature_collection",
    "build_folium_map",
]
