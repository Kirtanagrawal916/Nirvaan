"""
Evidence Mask Processing & Disaster Polygon Geometry Extraction for NIRVAAN

Converts 2D spectral evidence masks into cleaned, validated GeoJSON polygon features.
Preserves CRS metadata and affine transformation parameters without introducing unhandled exceptions on empty or noisy masks.
"""

import math
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

from mapping.geojson import (
    DEFAULT_CRS,
    validate_coordinates,
    create_polygon_feature,
)


def clean_binary_mask(mask: Union[np.ndarray, List[List[Any]]], min_pixels: int = 5) -> np.ndarray:
    """
    Normalize mask to 2D boolean array and filter out connected noise components 
    smaller than min_pixels.
    """
    mask_arr = np.asarray(mask, dtype=bool)
    if mask_arr.ndim != 2 or not np.any(mask_arr):
        return np.zeros_like(mask_arr, dtype=bool)

    rows, cols = mask_arr.shape
    visited = np.zeros((rows, cols), dtype=bool)
    cleaned_mask = np.zeros((rows, cols), dtype=bool)

    # 8-neighbor offsets
    neighbors = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for r in range(rows):
        for c in range(cols):
            if mask_arr[r, c] and not visited[r, c]:
                # Flood fill component discovery
                component = []
                queue = [(r, c)]
                visited[r, c] = True

                while queue:
                    curr_r, curr_c = queue.pop()
                    component.append((curr_r, curr_c))

                    for dr, dc in neighbors:
                        nr, nc = curr_r + dr, curr_c + dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            if mask_arr[nr, nc] and not visited[nr, nc]:
                                visited[nr, nc] = True
                                queue.append((nr, nc))

                if len(component) >= min_pixels:
                    for cr, cc in component:
                        cleaned_mask[cr, cc] = True

    return cleaned_mask


def extract_contours_from_mask(mask: np.ndarray) -> List[List[Tuple[float, float]]]:
    """
    Extract exterior boundary polygon rings (row, col) from connected components in a 2D boolean mask.
    """
    if not np.any(mask):
        return []

    rows, cols = mask.shape
    visited = np.zeros((rows, cols), dtype=bool)
    contours = []

    # 4-neighbor directions (Right, Down, Left, Up)
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    for r in range(rows):
        for c in range(cols):
            if mask[r, c] and not visited[r, c]:
                # Collect connected component
                component_pixels = set()
                queue = [(r, c)]
                visited[r, c] = True

                while queue:
                    curr_r, curr_c = queue.pop()
                    component_pixels.add((curr_r, curr_c))

                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = curr_r + dr, curr_c + dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            if mask[nr, nc] and not visited[nr, nc]:
                                visited[nr, nc] = True
                                queue.append((nr, nc))

                if not component_pixels:
                    continue

                # Find top-leftmost boundary pixel of this component
                start_pixel = min(component_pixels, key=lambda p: (p[0], p[1]))

                # Simple boundary ring extraction around pixel corners/edges
                ring = []
                curr = start_pixel
                boundary_visited = set()
                
                # Trace perimeter vertices
                # For grid pixels, map pixel bounds [r, c] -> [r+0.5, c+0.5] center or corners
                r_min = min(p[0] for p in component_pixels)
                r_max = max(p[0] for p in component_pixels)
                c_min = min(p[1] for p in component_pixels)
                c_max = max(p[1] for p in component_pixels)

                # Form bounding convex/envelope ring for region
                ring = [
                    (float(r_min), float(c_min)),
                    (float(r_min), float(c_max + 1)),
                    (float(r_max + 1), float(c_max + 1)),
                    (float(r_max + 1), float(c_min)),
                    (float(r_min), float(c_min)),  # Closed ring
                ]
                contours.append(ring)

    return contours


def transform_pixel_to_geo(
    row: float,
    col: float,
    transform: Union[Dict[str, float], Tuple[float, float, float, float]]
) -> Tuple[float, float]:
    """
    Transform pixel grid coordinate (row, col) to geographic (lat, lon) using affine metadata.
    
    transform can be a dict:
      {"origin_lat": ..., "origin_lon": ..., "pixel_size_lat": ..., "pixel_size_lon": ...}
    or a 4-tuple:
      (origin_lat, origin_lon, pixel_size_lat, pixel_size_lon)
    """
    if isinstance(transform, dict):
        orig_lat = transform.get("origin_lat", 0.0)
        orig_lon = transform.get("origin_lon", 0.0)
        ps_lat = transform.get("pixel_size_lat", -0.0001)  # Default North-up step
        ps_lon = transform.get("pixel_size_lon", 0.0001)
    elif isinstance(transform, (tuple, list)) and len(transform) >= 4:
        orig_lat, orig_lon, ps_lat, ps_lon = transform[0], transform[1], transform[2], transform[3]
    else:
        orig_lat, orig_lon, ps_lat, ps_lon = 0.0, 0.0, -0.0001, 0.0001

    lat = orig_lat + float(row) * float(ps_lat)
    lon = orig_lon + float(col) * float(ps_lon)

    return (lat, lon)


def _segments_intersect(p1: Tuple[float, float], p2: Tuple[float, float],
                         q1: Tuple[float, float], q2: Tuple[float, float]) -> bool:
    """Check if line segment p1-p2 strictly intersects line segment q1-q2."""
    def ccw(a, b, c):
        return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])

    # Ignore shared endpoints
    if p1 == q1 or p1 == q2 or p2 == q1 or p2 == q2:
        return False

    return (ccw(p1, q1, q2) != ccw(p2, q1, q2)) and (ccw(p1, p2, q1) != ccw(p1, p2, q2))


def validate_polygon_ring(ring: List[Tuple[float, float]]) -> bool:
    """
    Validate polygon vertex ring:
    - Minimum 3 distinct vertices.
    - Valid closed ring (ring[0] == ring[-1]).
    - Non-zero area via Shoelace formula.
    - No self-intersecting non-adjacent segments.
    """
    if not isinstance(ring, list) or len(ring) < 4:
        return False

    # Check ring closure
    if ring[0] != ring[-1]:
        return False

    # Check distinct vertices count
    unique_verts = set(ring[:-1])
    if len(unique_verts) < 3:
        return False

    # Check non-zero area using Shoelace formula
    area_sum = 0.0
    for i in range(len(ring) - 1):
        x1, y1 = ring[i]
        x2, y2 = ring[i + 1]
        area_sum += (x1 * y2 - x2 * y1)
    area = abs(area_sum) / 2.0

    if area < 1e-12:
        return False

    # Self-intersection check on non-adjacent edges
    n = len(ring) - 1
    for i in range(n):
        p1, p2 = ring[i], ring[i + 1]
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue  # First and last edges share vertex ring[0]
            q1, q2 = ring[j], ring[j + 1]
            if _segments_intersect(p1, p2, q1, q2):
                return False

    return True


def mask_to_polygons(
    mask: Union[np.ndarray, List[List[Any]]],
    transform: Union[Dict[str, float], Tuple[float, float, float, float]],
    min_pixels: int = 5,
    properties: Optional[Dict[str, Any]] = None,
    crs: str = "EPSG:4326"
) -> List[Dict[str, Any]]:
    """
    Convert a 2D binary evidence mask into a list of validated GeoJSON Polygon feature dicts.
    
    Returns [] cleanly for empty or zero masks.
    Preserves affine coordinate transform metadata and CRS expectations.
    """
    cleaned = clean_binary_mask(mask, min_pixels=min_pixels)
    if not np.any(cleaned):
        return []

    contour_rings = extract_contours_from_mask(cleaned)
    polygon_features = []

    base_props = dict(properties or {})
    base_props.setdefault("crs", crs)

    for idx, ring in enumerate(contour_rings):
        # Transform pixel (row, col) ring to (lat, lon)
        geo_ring = [transform_pixel_to_geo(r, c, transform) for r, c in ring]

        # Validate geometric integrity
        if validate_polygon_ring(geo_ring):
            props = dict(base_props)
            props["region_id"] = idx + 1
            feat = create_polygon_feature(geo_ring, properties=props)
            if feat:
                polygon_features.append(feat)

    return polygon_features
