"""
GeoJSON Utilities & Geographic Coordinate Handling for NIRVAAN Mapping

Provides strict coordinate validation, CRS expectations (WGS 84 / EPSG:4326),
event and hotspot coordinate extraction, bounding box computation,
and GeoJSON feature serialization.
"""

import math
from typing import Any, Dict, List, Optional, Tuple, Union

# Default Coordinate Reference System per GeoJSON RFC 7946 (WGS 84)
DEFAULT_CRS: Dict[str, Any] = {
    "type": "name",
    "properties": {
        "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
    }
}


def validate_coordinates(lat: Any, lon: Any, allow_null_island: bool = False) -> bool:
    """
    Validate latitude and longitude values.
    
    Latitude must be in [-90.0, 90.0].
    Longitude must be in [-180.0, 180.0].
    Values must be numeric, finite, and non-NaN.
    
    If allow_null_island is False, (0.0, 0.0) is rejected to prevent uninitialized/dummy coordinates.
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

    if not (-90.0 <= lat_f <= 90.0 and -180.0 <= lon_f <= 180.0):
        return False

    if not allow_null_island and lat_f == 0.0 and lon_f == 0.0:
        return False

    return True


def parse_event_coordinates(event_data: Optional[Dict[str, Any]]) -> Optional[Tuple[float, float]]:
    """
    Safely extract and validate (lat, lon) for an event location.
    Returns (lat, lon) tuple if valid, or None if missing or malformed.
    """
    if not isinstance(event_data, dict):
        return None
    lat = event_data.get("lat") if "lat" in event_data else event_data.get("latitude")
    lon = event_data.get("lon") if "lon" in event_data else event_data.get("longitude")

    if validate_coordinates(lat, lon):
        return (float(lat), float(lon))
    return None


def parse_hotspot_coordinates(hotspots: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Parse and validate a list of hotspot items.
    Returns a list of validated hotspot dicts with clean float lat and lon values.
    """
    if not isinstance(hotspots, list):
        return []

    valid_hotspots = []
    for hs in hotspots:
        if isinstance(hs, dict):
            lat = hs.get("lat") if "lat" in hs else hs.get("latitude")
            lon = hs.get("lon") if "lon" in hs else hs.get("longitude")
            if validate_coordinates(lat, lon):
                clean_hs = dict(hs)
                clean_hs["lat"] = float(lat)
                clean_hs["lon"] = float(lon)
                valid_hotspots.append(clean_hs)
    return valid_hotspots


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
        elif ("lat" in data or "latitude" in data) and ("lon" in data or "longitude" in data):
            parsed = parse_event_coordinates(data)
            if parsed:
                coords.append(parsed)
    elif isinstance(data, (list, tuple)):
        if len(data) == 2 and isinstance(data[0], (int, float)) and isinstance(data[1], (int, float)):
            v1, v2 = float(data[0]), float(data[1])
            if validate_coordinates(v1, v2, allow_null_island=True):
                coords.append((v1, v2))
            elif validate_coordinates(v2, v1, allow_null_island=True):
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
    properties: Optional[Dict[str, Any]] = None,
    allow_null_island: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Create a GeoJSON Point feature safely.
    Coordinates are formatted as [longitude, latitude] per GeoJSON RFC 7946 standard.
    Returns None if coordinates are invalid.
    """
    if not validate_coordinates(lat, lon, allow_null_island=allow_null_island):
        return None

    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [float(lon), float(lat)]
        },
        "properties": properties or {}
    }


def create_polygon_feature(
    coordinates: List[Tuple[float, float]],
    properties: Optional[Dict[str, Any]] = None,
    allow_null_island: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Create a GeoJSON Polygon feature safely from a list of (lat, lon) vertices.
    Output ring is formatted as [[lon, lat], ...] per GeoJSON standard.
    Returns None if coordinates are invalid or fewer than 3 unique vertices are provided.
    """
    valid_ring = []
    for pt in coordinates:
        if isinstance(pt, (list, tuple)) and len(pt) >= 2:
            lat, lon = float(pt[0]), float(pt[1])
            if validate_coordinates(lat, lon, allow_null_island=allow_null_island):
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


def create_feature_collection(
    features: List[Dict[str, Any]],
    include_crs: bool = True
) -> Dict[str, Any]:
    """
    Package a list of features into a GeoJSON FeatureCollection with optional CRS header.
    Filters out None values or non-feature items.
    """
    valid_features = [f for f in features if isinstance(f, dict) and f.get("type") == "Feature"]
    fc: Dict[str, Any] = {
        "type": "FeatureCollection",
        "features": valid_features
    }
    if include_crs:
        fc["crs"] = DEFAULT_CRS
    return fc
