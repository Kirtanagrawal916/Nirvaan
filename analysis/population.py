"""
Population Impact Estimation Module for NIRVAAN

Intersects disaster evidence polygons or risk zones with trusted population grid/vector datasets.
Labels all derived values explicitly as ESTIMATE and gracefully rejects invalid/missing population data.
"""

import math
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

from detection.mask import transform_pixel_to_geo, validate_polygon_ring
from mapping.geojson import DEFAULT_CRS


def create_synthetic_population_grid(
    rows: int,
    cols: int,
    transform: Union[Dict[str, float], Tuple[float, float, float, float]],
    density_per_pixel: float = 50.0
) -> Dict[str, Any]:
    """
    Construct a synthetic population grid dataset dictionary for testing.
    """
    grid = np.full((rows, cols), fill_value=density_per_pixel, dtype=float)
    return {
        "type": "raster_grid",
        "grid": grid,
        "transform": transform,
        "unit": "people_per_pixel",
        "crs": "EPSG:4326"
    }


def _point_in_polygon(lat: float, lon: float, ring: List[Tuple[float, float]]) -> bool:
    """Ray-casting point in polygon test."""
    n = len(ring)
    inside = False
    p1x, p1y = ring[0]
    for i in range(n + 1):
        p2x, p2y = ring[i % n]
        if lat > min(p1x, p2x):
            if lat <= max(p1x, p2x):
                if lon <= max(p1y, p2y):
                    if p1x != p2x:
                        xinters = (lat - p1x) * (p2y - p1y) / (p2x - p1x) + p1y
                    if p1y == p2y or lon <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside


def estimate_affected_population(
    polygons_or_risk_zones: Optional[Union[List[Dict[str, Any]], List[List[Tuple[float, float]]]]],
    population_data: Optional[Dict[str, Any]] = None,
    crs: str = "EPSG:4326"
) -> Dict[str, Any]:
    """
    Estimate population impact by intersecting disaster polygons or risk zones with population data.
    
    All output numbers are explicitly labeled with "provenance_label": "ESTIMATE".
    If population_data is None, empty, or malformed, rejects calculation with status "DATA_UNAVAILABLE".
    """
    # 1. Reject if population dataset is missing or malformed
    if not population_data or not isinstance(population_data, dict):
        return {
            "status": "DATA_UNAVAILABLE",
            "estimated_affected_population": None,
            "provenance_label": "ESTIMATE",
            "reason": "Population dataset is unavailable or invalid",
            "crs": crs
        }

    # 2. Reject if polygons are missing
    if not polygons_or_risk_zones or not isinstance(polygons_or_risk_zones, list):
        return {
            "status": "NO_AFFECTED_POLYGONS",
            "estimated_affected_population": 0,
            "provenance_label": "ESTIMATE",
            "reason": "No valid affected polygons or risk zones provided",
            "crs": crs
        }

    # Extract polygon rings & metadata
    parsed_items = []
    for item in polygons_or_risk_zones:
        ring = None
        props = {}
        if isinstance(item, dict):
            props = item.get("properties", {})
            geom = item.get("geometry", item)
            if geom.get("type") == "Polygon" and geom.get("coordinates"):
                # GeoJSON coordinates are [lon, lat] -> convert to (lat, lon)
                ring = [(pt[1], pt[0]) for pt in geom["coordinates"][0]]
            elif "coordinates" in item:
                ring = item["coordinates"]
        elif isinstance(item, (list, tuple)):
            ring = item

        if ring and validate_polygon_ring(ring):
            parsed_items.append({"ring": ring, "properties": props})

    if not parsed_items:
        return {
            "status": "NO_VALID_POLYGONS",
            "estimated_affected_population": 0,
            "provenance_label": "ESTIMATE",
            "reason": "No geometrically valid polygons could be extracted",
            "crs": crs
        }

    # 3. Process raster grid population data
    grid = population_data.get("grid")
    transform = population_data.get("transform")

    if grid is None or not isinstance(grid, np.ndarray) or not transform:
        return {
            "status": "DATA_UNAVAILABLE",
            "estimated_affected_population": None,
            "provenance_label": "ESTIMATE",
            "reason": "Population raster grid or transform metadata is missing",
            "crs": crs
        }

    rows, cols = grid.shape
    total_affected_pop = 0.0
    zone_breakdown = []

    for item in parsed_items:
        ring = item["ring"]
        props = item["properties"]
        zone_type = props.get("zone_type", "disaster_polygon")
        severity = props.get("severity", props.get("severity_band", "High"))

        # Find grid bounding box for efficiency
        lats = [pt[0] for pt in ring]
        lons = [pt[1] for pt in ring]
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)

        zone_pop = 0.0
        pixels_intersected = 0

        # Scan grid pixels
        for r in range(rows):
            for c in range(cols):
                plat, plon = transform_pixel_to_geo(r, c, transform)
                if min_lat <= plat <= max_lat and min_lon <= plon <= max_lon:
                    if _point_in_polygon(plat, plon, ring):
                        pop_val = float(grid[r, c])
                        if not math.isnan(pop_val) and pop_val > 0:
                            zone_pop += pop_val
                            pixels_intersected += 1

        total_affected_pop += zone_pop
        zone_breakdown.append({
            "zone_type": zone_type,
            "severity_band": severity,
            "estimated_affected_population": round(zone_pop, 1),
            "intersected_pixels": pixels_intersected,
            "provenance_label": "ESTIMATE"
        })

    return {
        "status": "SUCCESS",
        "estimated_affected_population": round(total_affected_pop, 1),
        "total_zones_analyzed": len(parsed_items),
        "zone_breakdown": zone_breakdown,
        "provenance_label": "ESTIMATE",
        "crs": crs
    }
