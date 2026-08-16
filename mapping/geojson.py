"""
GeoJSON Utilities for NIRVAAN Mapping

Provides strict coordinate validation, bounding box extraction,
and GeoJSON feature construction without introducing external GIS dependencies.
"""

import math
from typing import Any, Dict, List, Optional, Tuple, Union


def validate_coordinates(lat: Any, lon: Any) -> bool:
    """
    Validate latitude and longitude values.
    
    Latitude must be in [-90.0, 90.0].
    Longitude must be in [-180.0, 180.0].
    Values must be numeric and non-NaN.
    """
    if lat is None or lon is None:
        return False
    try:
        lat_f = float(lat)
        lon_f = float(lon)
    except (ValueError, TypeError):
        return False

    if math.isnan(lat_f) or math.isnan(lon_f) or math.isinf(lat_f) or math.isinf(lon_f):
        return False

    return -90.0 <= lat_f <= 90.0 and -180.0 <= lon_f <= 180.0


def extract_all_coordinates(data: Any) -> List[Tuple[float, float]]:
    """
    Recursively extract (lat, lon) pairs from raw numbers, lists, tuples, or GeoJSON objects.
    """
    coords = []
    if isinstance(data, dict):
        if data.get("type") == "FeatureCollection":
            for feat in data.get("features", []):
                coords.extend(extract_all_coordinates(feat))
        elif data.get("type") == "Feature":
            coords.extend(extract_all_coordinates(data.get("geometry", {})))
        elif "coordinates" in data:
            coords.extend(extract_all_coordinates(data["coordinates"]))
        elif "lat" in data and "lon" in data:
            if validate_coordinates(data["lat"], data["lon"]):
                coords.append((float(data["lat"]), float(data["lon"])))
        elif "latitude" in data and "longitude" in data:
            if validate_coordinates(data["latitude"], data["longitude"]):
                coords.append((float(data["latitude"]), float(data["longitude"])))
    elif isinstance(data, (list, tuple)):
        if len(data) == 2 and isinstance(data[0], (int, float)) and isinstance(data[1], (int, float)):
            # Check if order is [lon, lat] or [lat, lon]
            v1, v2 = float(data[0]), float(data[1])
            if validate_coordinates(v1, v2):  # v1=lat, v2=lon
                coords.append((v1, v2))
            elif validate_coordinates(v2, v1):  # GeoJSON format: [lon, lat] -> (lat, lon)
                coords.append((v2, v1))
        else:
            for item in data:
                coords.extend(extract_all_coordinates(item))
    return coords


def calculate_bounds(data: Any) -> Optional[List[List[float]]]:
    """
    Calculate bounding box [[min_lat, min_lon], [max_lat, max_lon]] from coordinate payloads.
    Returns None if no valid coordinates are found.
    """
    coords = extract_all_coordinates(data)
    if not coords:
        return None

    lats = [c[0] for c in coords]
    lons = [c[1] for c in coords]

    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)

    # Avoid zero-area bounds for single points
    if min_lat == max_lat:
        min_lat -= 0.01
        max_lat += 0.01
    if min_lon == max_lon:
        min_lon -= 0.01
        max_lon += 0.01

    return [[min_lat, min_lon], [max_lat, max_lon]]


def create_point_feature(
    lat: float,
    lon: float,
    properties: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    Create a GeoJSON Point feature safely. Returns None if coordinates are invalid.
    """
    if not validate_coordinates(lat, lon):
        return None

    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [float(lon), float(lat)]  # GeoJSON standards specify [lon, lat]
        },
        "properties": properties or {}
    }


def create_polygon_feature(
    coordinates: List[Tuple[float, float]],
    properties: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    Create a GeoJSON Polygon feature safely from a list of (lat, lon) coordinates.
    Returns None if coordinates are invalid or fewer than 3 vertices are provided.
    """
    valid_ring = []
    for pt in coordinates:
        if isinstance(pt, (list, tuple)) and len(pt) >= 2:
            lat, lon = float(pt[0]), float(pt[1])
            if validate_coordinates(lat, lon):
                valid_ring.append([lon, lat])

    if len(valid_ring) < 3:
        return None

    # Ensure closed ring for valid GeoJSON Polygon
    if valid_ring[0] != valid_ring[-1]:
        valid_ring.append(valid_ring[0])

    return {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [valid_ring]
        },
        "properties": properties or {}
    }


def create_feature_collection(features: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Package a list of features into a GeoJSON FeatureCollection, filtering out None values.
    """
    valid_features = [f for f in features if isinstance(f, dict) and f.get("type") == "Feature"]
    return {
        "type": "FeatureCollection",
        "features": valid_features
    }
