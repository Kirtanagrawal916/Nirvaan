"""
NIRVAAN Disaster Hotspot Extraction Module (TASK-014)

Extracts spatial hotspots (contiguous clusters of affected pixels) from
validated disaster masks, converting raster pixel centroids into geographic
latitude/longitude coordinates.
"""

from collections import deque
from dataclasses import dataclass, field
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

from analysis.mask_generator import DisasterMask, generate_disaster_mask
from data.loader import load_event


def utm_to_latlon(easting: float, northing: float, zone: int, northern: bool = True) -> Tuple[float, float]:
    """
    Pure Python WGS84 UTM to Geographic Latitude/Longitude conversion.

    :param easting: UTM Easting in meters.
    :param northing: UTM Northing in meters.
    :param zone: UTM Zone number (e.g., 32, 35).
    :param northern: True for Northern hemisphere, False for Southern.
    :return: Tuple of (latitude, longitude) in degrees.
    """
    a = 6378137.0  # WGS84 semi-major axis
    f = 1 / 298.257223563  # Flattening
    k0 = 0.9996

    e = math.sqrt(2 * f - f * f)
    e1 = (1 - math.sqrt(1 - e * e)) / (1 + math.sqrt(1 - e * e))

    x = easting - 500000.0  # Remove false easting
    y = northing if northern else northing - 10000000.0

    long_origin = (zone - 1) * 6 - 180 + 3

    M = y / k0
    mu = M / (a * (1 - e ** 2 / 4 - 3 * e ** 4 / 64 - 5 * e ** 6 / 256))

    phi1 = (
        mu
        + (3 * e1 / 2 - 27 * e1 ** 3 / 32) * math.sin(2 * mu)
        + (21 * e1 ** 2 / 16 - 55 * e1 ** 4 / 32) * math.sin(4 * mu)
        + (151 * e1 ** 3 / 96) * math.sin(6 * mu)
    )

    N1 = a / math.sqrt(1 - e ** 2 * math.sin(phi1) ** 2)
    T1 = math.tan(phi1) ** 2
    C1 = (e ** 2 / (1 - e ** 2)) * math.cos(phi1) ** 2
    R1 = a * (1 - e ** 2) / (1 - e ** 2 * math.sin(phi1) ** 2) ** 1.5
    D = x / (N1 * k0)

    lat = phi1 - (N1 * math.tan(phi1) / R1) * (
        D ** 2 / 2
        - (5 + 3 * T1 + 10 * C1 - 4 * C1 ** 2 - 9 * (e ** 2 / (1 - e ** 2))) * D ** 4 / 24
        + (61 + 90 * T1 + 298 * C1 + 45 * T1 ** 2 - 252 * (e ** 2 / (1 - e ** 2)) - 3 * C1 ** 2) * D ** 6 / 720
    )

    lon = long_origin + math.degrees(
        (
            D
            - (1 + 2 * T1 + C1) * D ** 3 / 6
            + (5 - 2 * C1 + 28 * T1 - 3 * C1 ** 2 + 8 * (e ** 2 / (1 - e ** 2)) + 24 * T1 ** 2) * D ** 5 / 120
        )
        / math.cos(phi1)
    )

    return math.degrees(lat), lon


@dataclass
class Hotspot:
    """
    Structured spatial hotspot entity representing a localized disaster cluster.
    """
    hotspot_id: str
    event_id: str
    disaster_type: str
    centroid_latitude: float
    centroid_longitude: float
    pixel_count: int
    area_m2: float
    area_hectares: float
    severity: str
    bounding_box: Tuple[int, int, int, int]  # (min_row, min_col, max_row, max_col)
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes hotspot to a clean dictionary."""
        return {
            "hotspot_id": self.hotspot_id,
            "event_id": self.event_id,
            "disaster_type": self.disaster_type,
            "centroid_latitude": round(self.centroid_latitude, 6),
            "centroid_longitude": round(self.centroid_longitude, 6),
            "pixel_count": self.pixel_count,
            "area_m2": round(self.area_m2, 2),
            "area_hectares": round(self.area_hectares, 4),
            "severity": self.severity,
            "bounding_box": list(self.bounding_box),
            "provenance": self.provenance,
        }


@dataclass
class HotspotExtractionResult:
    """
    Container for extracted disaster hotspots.
    """
    event_id: str
    disaster_type: str
    total_hotspots: int
    hotspots: List[Hotspot]
    CRS: str
    resolution_m: float
    min_pixels_filter: int
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes hotspots result without circular dependencies."""
        return {
            "event_id": self.event_id,
            "disaster_type": self.disaster_type,
            "total_hotspots": self.total_hotspots,
            "hotspots": [h.to_dict() for h in self.hotspots],
            "CRS": self.CRS,
            "resolution_m": self.resolution_m,
            "min_pixels_filter": self.min_pixels_filter,
            "provenance": self.provenance,
        }


class HotspotExtractor:
    """
    Engine for extracting connected spatial hotspots from disaster masks.
    """

    def __init__(self, min_pixels: int = 10, max_hotspots: int = 20):
        """
        Initialize HotspotExtractor.

        :param min_pixels: Minimum pixel count threshold to filter out noise clusters.
        :param max_hotspots: Maximum number of top hotspots to return.
        """
        self.min_pixels = min_pixels
        self.max_hotspots = max_hotspots

    def extract_hotspots(
        self,
        mask_obj: DisasterMask,
        event_center_lat: Optional[float] = None,
        event_center_lon: Optional[float] = None,
    ) -> HotspotExtractionResult:
        """
        Extracts contiguous hotspots from a DisasterMask object.

        :param mask_obj: DisasterMask from TASK-011.
        :param event_center_lat: Optional event center latitude for fallback coordinate mapping.
        :param event_center_lon: Optional event center longitude for fallback coordinate mapping.
        :return: HotspotExtractionResult object.
        """
        if not isinstance(mask_obj, DisasterMask):
            raise TypeError(f"Input must be a DisasterMask object, got {type(mask_obj)}")

        binary_mask = (mask_obj.mask > 0).astype(np.uint8)
        h, w = mask_obj.dimensions

        if np.sum(binary_mask) == 0:
            return HotspotExtractionResult(
                event_id=mask_obj.event_id,
                disaster_type=mask_obj.disaster_type,
                total_hotspots=0,
                hotspots=[],
                CRS=mask_obj.CRS,
                resolution_m=mask_obj.resolution_m,
                min_pixels_filter=self.min_pixels,
                provenance=mask_obj.provenance,
            )

        # Connected component labeling (8-connectivity BFS)
        visited = np.zeros((h, w), dtype=bool)
        clusters = []

        for r in range(h):
            for c in range(w):
                if binary_mask[r, c] == 1 and not visited[r, c]:
                    # BFS cluster extraction
                    cluster_pixels = []
                    queue = deque([(r, c)])
                    visited[r, c] = True

                    min_r, max_r = r, r
                    min_c, max_c = c, c

                    while queue:
                        curr_r, curr_c = queue.popleft()
                        cluster_pixels.append((curr_r, curr_c))

                        min_r = min(min_r, curr_r)
                        max_r = max(max_r, curr_r)
                        min_c = min(min_c, curr_c)
                        max_c = max(max_c, curr_c)

                        # 8-neighbor offsets
                        for dr in (-1, 0, 1):
                            for dc in (-1, 0, 1):
                                if dr == 0 and dc == 0:
                                    continue
                                nr, nc = curr_r + dr, curr_c + dc
                                if 0 <= nr < h and 0 <= nc < w:
                                    if binary_mask[nr, nc] == 1 and not visited[nr, nc]:
                                        visited[nr, nc] = True
                                        queue.append((nr, nc))

                    if len(cluster_pixels) >= self.min_pixels:
                        clusters.append({
                            "pixels": cluster_pixels,
                            "bbox": (min_r, min_c, max_r, max_c),
                            "count": len(cluster_pixels),
                        })

        # Rank clusters by pixel count descending
        clusters.sort(key=lambda x: x["count"], reverse=True)
        top_clusters = clusters[: self.max_hotspots]

        # Extract UTM zone if present in CRS string
        utm_zone = 32
        if "32N" in mask_obj.CRS or "32" in mask_obj.CRS:
            utm_zone = 32
        elif "35N" in mask_obj.CRS or "35" in mask_obj.CRS:
            utm_zone = 35

        hotspots_list = []
        res_m = float(mask_obj.resolution_m)
        pixel_area = res_m * res_m

        for idx, cl in enumerate(top_clusters, start=1):
            pixel_list = cl["pixels"]
            count = cl["count"]
            bbox = cl["bbox"]

            # Compute centroid in pixel space
            r_center = sum(p[0] for p in pixel_list) / count
            c_center = sum(p[1] for p in pixel_list) / count

            # Convert pixel centroid to spatial coordinates
            lat, lon = self._pixel_to_latlon(
                r_center,
                c_center,
                h,
                w,
                res_m,
                mask_obj.CRS,
                mask_obj.transform,
                utm_zone,
                event_center_lat,
                event_center_lon,
            )

            area_m2 = count * pixel_area
            area_ha = area_m2 / 10000.0

            # Assign severity rank based on cluster size / density
            if count > 500:
                sev = "HIGH"
            elif count > 100:
                sev = "MODERATE"
            else:
                sev = "LOW"

            hotspots_list.append(
                Hotspot(
                    hotspot_id=f"hotspot-{idx:02d}",
                    event_id=mask_obj.event_id,
                    disaster_type=mask_obj.disaster_type,
                    centroid_latitude=lat,
                    centroid_longitude=lon,
                    pixel_count=count,
                    area_m2=area_m2,
                    area_hectares=area_ha,
                    severity=sev,
                    bounding_box=bbox,
                    provenance=mask_obj.provenance,
                )
            )

        return HotspotExtractionResult(
            event_id=mask_obj.event_id,
            disaster_type=mask_obj.disaster_type,
            total_hotspots=len(hotspots_list),
            hotspots=hotspots_list,
            CRS=mask_obj.CRS,
            resolution_m=res_m,
            min_pixels_filter=self.min_pixels,
            provenance=mask_obj.provenance,
        )

    def _pixel_to_latlon(
        self,
        r: float,
        c: float,
        h: int,
        w: int,
        res_m: float,
        crs_str: str,
        transform: Optional[Tuple[float, ...]],
        utm_zone: int,
        default_lat: Optional[float],
        default_lon: Optional[float],
    ) -> Tuple[float, float]:
        """Converts pixel row/col centroid to geographic (lat, lon)."""
        is_geographic = "EPSG:4326" in crs_str or "GEOGRAPHIC" in crs_str

        if is_geographic:
            # Geographic coordinate system directly maps to lon/lat
            lon = (default_lon or 0.0) + (c - w / 2.0) * res_m
            lat = (default_lat or 0.0) - (r - h / 2.0) * res_m
            return lat, lon

        # Projected UTM coordinate system (e.g. EPSG:32632 or EPSG:32635)
        if transform and len(transform) >= 6 and transform[1] > 0:
            easting = transform[0] + (c + 0.5) * transform[1]
            northing = transform[3] + (r + 0.5) * transform[5]
        else:
            # Default center UTM offset simulation if transform not embedded
            base_easting = 500000.0 + (c - w / 2.0) * res_m
            base_northing = 4900000.0 - (r - h / 2.0) * res_m
            easting, northing = base_easting, base_northing

        try:
            lat, lon = utm_to_latlon(easting, northing, zone=utm_zone, northern=True)
            return lat, lon
        except Exception:
            # Fallback to default event center if provided
            lat = default_lat if default_lat is not None else 44.5
            lon = default_lon if default_lon is not None else 11.3
            return lat, lon


def extract_hotspots(
    event_or_mask: Any,
    min_pixels: int = 10,
    config_path: Optional[Union[str, Path]] = None,
) -> HotspotExtractionResult:
    """
    Public helper function API for extracting disaster hotspots.
    """
    extractor = HotspotExtractor(min_pixels=min_pixels)

    if isinstance(event_or_mask, DisasterMask):
        return extractor.extract_hotspots(event_or_mask)

    # Generate mask from event_id or result object
    mask_obj = generate_disaster_mask(event_or_mask, config_path=config_path)

    center_lat, center_lon = None, None
    if isinstance(event_or_mask, str):
        try:
            ev = load_event(event_or_mask)
            center_lat, center_lon = ev.latitude, ev.longitude
        except Exception:
            pass

    return extractor.extract_hotspots(mask_obj, event_center_lat=center_lat, event_center_lon=center_lon)
