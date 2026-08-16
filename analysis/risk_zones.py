"""
Risk-Zone Generation Module for NIRVAAN

Generates concentric risk zones (High/Extreme core, Moderate buffer, Low buffer)
from validated disaster evidence polygons. Preserves CRS and geometry validity.
"""

import math
from typing import Any, Dict, List, Optional, Tuple, Union

from detection.mask import validate_polygon_ring
from mapping.geojson import (
    DEFAULT_CRS,
    create_polygon_feature,
    create_feature_collection,
)

# Optional Shapely import for advanced geometric operations
try:
    from shapely.geometry import Polygon as ShapelyPolygon, mapping as shapely_mapping
    HAS_SHAPELY = True
except ImportError:
    HAS_SHAPELY = False


def buffer_polygon_vertices(
    ring: List[Tuple[float, float]],
    offset_dist: float
) -> List[Tuple[float, float]]:
    """
    Offset a closed polygon vertex ring outwards by offset_dist degrees.
    Uses Shapely if available, or pure Python vertex normal calculation fallback.
    """
    if offset_dist <= 0.0:
        return list(ring)

    if HAS_SHAPELY:
        try:
            # Shapely coordinates are [lon, lat]
            shapely_coords = [(pt[1], pt[0]) for pt in ring]
            poly = ShapelyPolygon(shapely_coords)
            if poly.is_valid and not poly.is_empty:
                buffered = poly.buffer(offset_dist, join_style=2)  # Mitred/square join
                if buffered.is_valid and not buffered.is_empty:
                    ext_coords = list(buffered.exterior.coords)
                    # Convert back to (lat, lon)
                    return [(pt[1], pt[0]) for pt in ext_coords]
        except Exception:
            pass

    # Pure Python vertex normal offset fallback
    if len(ring) < 4:
        return list(ring)

    # Ensure closed ring
    ring_clean = list(ring)
    if ring_clean[0] != ring_clean[-1]:
        ring_clean.append(ring_clean[0])

    n = len(ring_clean) - 1
    buffered_verts = []

    for i in range(n):
        p_prev = ring_clean[i - 1]
        p_curr = ring_clean[i]
        p_next = ring_clean[i + 1]

        # Edge vectors
        dx1, dy1 = p_curr[0] - p_prev[0], p_curr[1] - p_prev[1]
        dx2, dy2 = p_next[0] - p_curr[0], p_next[1] - p_curr[1]

        len1 = math.hypot(dx1, dy1)
        len2 = math.hypot(dx2, dy2)

        if len1 == 0 or len2 == 0:
            buffered_verts.append(p_curr)
            continue

        # Outward normals
        n1 = (-dy1 / len1, dx1 / len1)
        n2 = (-dy2 / len2, dx2 / len2)

        # Average normal
        nx = n1[0] + n2[0]
        ny = n1[1] + n2[1]
        norm_len = math.hypot(nx, ny)

        if norm_len == 0:
            nx, ny = n1[0], n1[1]
        else:
            nx, ny = nx / norm_len, ny / norm_len

        lat_off = p_curr[0] + nx * offset_dist
        lon_off = p_curr[1] + ny * offset_dist
        buffered_verts.append((lat_off, lon_off))

    # Close ring
    buffered_verts.append(buffered_verts[0])
    return buffered_verts


def generate_risk_zones(
    polygons: Union[List[Dict[str, Any]], List[List[Tuple[float, float]]]],
    buffer_config: Optional[List[Dict[str, Any]]] = None,
    crs: str = "EPSG:4326"
) -> List[Dict[str, Any]]:
    """
    Generate multi-tier concentric risk zones from input disaster polygons.
    
    Default Buffer Configuration Tiers:
    1. Core: Original evidence polygon (Severity: High / Extreme)
    2. Moderate Buffer: +0.01° offset (~1.1 km) (Severity: Moderate)
    3. Low Buffer: +0.025° offset (~2.7 km) (Severity: Low)
    
    Returns list of GeoJSON Polygon feature dictionaries.
    Returns [] cleanly for empty or invalid input polygon lists.
    """
    if not isinstance(polygons, list) or not polygons:
        return []

    # Default buffer distance tiers (~111km per degree latitude)
    default_config = [
        {"zone_type": "core", "severity_band": "High", "buffer_deg": 0.0, "buffer_km": 0.0},
        {"zone_type": "buffer_moderate", "severity_band": "Moderate", "buffer_deg": 0.01, "buffer_km": 1.1},
        {"zone_type": "buffer_low", "severity_band": "Low", "buffer_deg": 0.025, "buffer_km": 2.7},
    ]
    tiers = buffer_config or default_config

    risk_zone_features = []

    # Normalize inputs to vertex ring lists
    input_rings = []
    for item in polygons:
        if isinstance(item, dict):
            # Extract from GeoJSON feature or geometry dict
            geom = item.get("geometry", item)
            coords = geom.get("coordinates", [])
            if geom.get("type") == "Polygon" and coords:
                # GeoJSON coordinates are [lon, lat] -> convert to (lat, lon)
                ring = [(pt[1], pt[0]) for pt in coords[0]]
                input_rings.append(ring)
            elif "coordinates" in item:
                # Raw list of (lat, lon) tuples
                input_rings.append(item["coordinates"])
        elif isinstance(item, (list, tuple)):
            input_rings.append(item)

    if not input_rings:
        return []

    for ring_idx, base_ring in enumerate(input_rings):
        # Validate base ring
        if not validate_polygon_ring(base_ring):
            continue

        for tier in tiers:
            buf_deg = float(tier.get("buffer_deg", 0.0))
            buf_km = float(tier.get("buffer_km", 0.0))
            sev = tier.get("severity_band", "Moderate")
            zone_type = tier.get("zone_type", "buffer")

            # Offset geometry
            buf_ring = buffer_polygon_vertices(base_ring, buf_deg)

            if validate_polygon_ring(buf_ring):
                props = {
                    "source_polygon_id": ring_idx + 1,
                    "zone_type": zone_type,
                    "severity": sev,
                    "severity_band": sev,
                    "buffer_deg": buf_deg,
                    "buffer_km": buf_km,
                    "crs": crs,
                }
                feat = create_polygon_feature(buf_ring, properties=props)
                if feat:
                    risk_zone_features.append(feat)

    return risk_zone_features


def to_geojson_risk_zones(
    risk_zones: List[Dict[str, Any]],
    include_crs: bool = True
) -> Dict[str, Any]:
    """
    Serialize generated risk zones list into a standard GeoJSON FeatureCollection.
    """
    return create_feature_collection(risk_zones, include_crs=include_crs)
