"""
Infrastructure Impact & Proximity Analysis Module for NIRVAAN

Evaluates proximity of critical infrastructure (hospitals, schools, roads, bridges, settlements)
to disaster hotspots and risk zones.
Enforces safety guidelines: never claims confirmed damage; labels findings as field verification recommended.
Skips gracefully if local infrastructure data is unavailable.
"""

import math
from typing import Any, Dict, List, Optional, Tuple, Union

from detection.mask import validate_polygon_ring
from mapping.geojson import DEFAULT_CRS, validate_coordinates


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on the earth in kilometers.
    """
    if not (validate_coordinates(lat1, lon1, allow_null_island=True) and validate_coordinates(lat2, lon2, allow_null_island=True)):
        return float("inf")

    # Earth radius in kilometers
    r = 6371.0

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


def create_synthetic_infrastructure_layer() -> Dict[str, Any]:
    """
    Construct a synthetic local critical infrastructure GeoJSON dataset dictionary for testing.
    """
    features = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [92.915, 26.210]},
            "properties": {"name": "Assam District Hospital", "category": "hospital", "capacity_beds": 150}
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [92.925, 26.220]},
            "properties": {"name": "Central Secondary School", "category": "school", "students": 450}
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [92.905, 26.205]},
            "properties": {"name": "Brahmaputra Highway Bridge", "category": "bridge", "type": "highway"}
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [92.930, 26.215]},
            "properties": {"name": "Nirvaan Village Settlement", "category": "settlement", "households": 120}
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [92.890, 26.190]},
            "properties": {"name": "National Highway 27", "category": "road", "type": "primary"}
        }
    ]
    return {
        "type": "FeatureCollection",
        "features": features,
        "crs": DEFAULT_CRS
    }


def analyze_infrastructure_impact(
    polygons_or_hotspots: Optional[Union[List[Dict[str, Any]], List[Tuple[float, float]]]],
    infrastructure_data: Optional[Dict[str, Any]] = None,
    max_threshold_km: float = 5.0,
    crs: str = "EPSG:4326"
) -> Dict[str, Any]:
    """
    Analyze proximity of critical infrastructure to disaster features.
    
    If infrastructure_data is None or empty, skips gracefully returning status "DATA_UNAVAILABLE".
    Generates advisory findings with mandatory field verification warnings.
    """
    # 1. Skip gracefully if infrastructure dataset is unavailable
    if not infrastructure_data or not isinstance(infrastructure_data, dict):
        return {
            "status": "DATA_UNAVAILABLE",
            "impacted_infrastructure": [],
            "advisory_statements": [],
            "field_verification_recommended": True,
            "reason": "Local infrastructure dataset is unavailable — skipped gracefully",
            "crs": crs
        }

    features = infrastructure_data.get("features", [])
    if not features or not isinstance(features, list):
        return {
            "status": "DATA_UNAVAILABLE",
            "impacted_infrastructure": [],
            "advisory_statements": [],
            "field_verification_recommended": True,
            "reason": "Infrastructure dataset contains no feature records",
            "crs": crs
        }

    # 2. Extract query points (hotspots / polygon vertices)
    query_points: List[Tuple[float, float]] = []
    if polygons_or_hotspots and isinstance(polygons_or_hotspots, list):
        for item in polygons_or_hotspots:
            if isinstance(item, dict):
                lat = item.get("lat") or item.get("latitude")
                lon = item.get("lon") or item.get("longitude")
                if lat is not None and lon is not None:
                    query_points.append((float(lat), float(lon)))
                else:
                    # Check GeoJSON geometry
                    geom = item.get("geometry", item)
                    coords = geom.get("coordinates", [])
                    if geom.get("type") == "Point" and len(coords) >= 2:
                        query_points.append((float(coords[1]), float(coords[0])))
                    elif geom.get("type") == "Polygon" and coords:
                        for pt in coords[0]:
                            query_points.append((float(pt[1]), float(pt[0])))
            elif isinstance(item, (list, tuple)) and len(item) >= 2:
                query_points.append((float(item[0]), float(item[1])))

    if not query_points:
        return {
            "status": "NO_DISASTER_POINTS",
            "impacted_infrastructure": [],
            "advisory_statements": [],
            "field_verification_recommended": True,
            "reason": "No valid disaster hotspot or polygon coordinates provided",
            "crs": crs
        }

    # 3. Analyze proximity for each infrastructure feature
    impacted_facilities = []
    advisory_statements = []

    for feat in features:
        if not isinstance(feat, dict):
            continue

        props = feat.get("properties", {})
        name = props.get("name", "Unknown Facility")
        category = props.get("category", "infrastructure").capitalize()

        geom = feat.get("geometry", {})
        coords = geom.get("coordinates", [])

        # Get facility point location
        fac_lat, fac_lon = None, None
        if geom.get("type") == "Point" and len(coords) >= 2:
            fac_lat, fac_lon = float(coords[1]), float(coords[0])
        elif "lat" in props and "lon" in props:
            fac_lat, fac_lon = float(props["lat"]), float(props["lon"])

        if fac_lat is None or fac_lon is None:
            continue

        # Find minimum distance to any disaster query point
        min_dist_km = min(haversine_distance(fac_lat, fac_lon, q[0], q[1]) for q in query_points)

        if min_dist_km <= max_threshold_km:
            facility_entry = {
                "name": name,
                "category": category.lower(),
                "distance_km": round(min_dist_km, 2),
                "latitude": fac_lat,
                "longitude": fac_lon,
                "field_verification_recommended": True
            }
            impacted_facilities.append(facility_entry)

            # Standard required advisory text format
            advis_text = f"{category} ('{name}') within {min_dist_km:.1f} km of affected disaster zone — field verification recommended."
            advisory_statements.append(advis_text)

    # Sort by distance
    impacted_facilities.sort(key=lambda x: x["distance_km"])

    return {
        "status": "SUCCESS",
        "facilities_analyzed": len(features),
        "impacted_facilities_count": len(impacted_facilities),
        "impacted_infrastructure": impacted_facilities,
        "advisory_statements": advisory_statements,
        "field_verification_recommended": True,
        "crs": crs
    }
