"""
NIRVAAN Affected Area Calculation Module (TASK-012)

Calculates geospatially accurate physical affected area (m², hectares, km²)
from validated disaster detection masks (TASK-011).
"""

from dataclasses import dataclass, field
import math
from pathlib import Path
from typing import Any, Dict, Optional, Union

import numpy as np

from analysis.mask_generator import DisasterMask, generate_disaster_mask
from data.loader import load_event


@dataclass
class AffectedAreaResult:
    """
    Structured container for affected physical area calculations.
    """
    event_id: str
    disaster_type: str
    affected_pixel_count: int
    pixel_area_m2: float
    affected_area_m2: float
    affected_area_hectares: float
    affected_area_km2: float
    CRS: str
    resolution_m: float
    method: str
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes area metrics to a clean dictionary."""
        return {
            "event_id": self.event_id,
            "disaster_type": self.disaster_type,
            "affected_pixel_count": self.affected_pixel_count,
            "pixel_area_m2": round(self.pixel_area_m2, 4),
            "affected_area_m2": round(self.affected_area_m2, 2),
            "affected_area_hectares": round(self.affected_area_hectares, 4),
            "affected_area_km2": round(self.affected_area_km2, 6),
            "CRS": self.CRS,
            "resolution_m": self.resolution_m,
            "method": self.method,
            "provenance": self.provenance,
        }


class AreaCalculator:
    """
    Geospatial Area Calculator engine.
    """

    def calculate_area(
        self,
        mask_obj: DisasterMask,
        latitude: Optional[float] = None,
    ) -> AffectedAreaResult:
        """
        Calculates physical ground area from a validated DisasterMask.

        :param mask_obj: DisasterMask object from TASK-011.
        :param latitude: Optional latitude float for geographic CRS cosine scaling.
        :return: AffectedAreaResult dataclass object.
        """
        if not isinstance(mask_obj, DisasterMask):
            raise TypeError(f"Input must be a DisasterMask object, got {type(mask_obj)}")

        if mask_obj.resolution_m <= 0:
            raise ValueError(f"Invalid raster resolution_m: {mask_obj.resolution_m}. Must be > 0.")

        crs_str = mask_obj.CRS.upper()
        res_m = float(mask_obj.resolution_m)

        # Count affected pixels (where mask > 0)
        if mask_obj.mask is not None and mask_obj.mask.size > 0:
            affected_count = int(np.sum(mask_obj.mask > 0))
        else:
            affected_count = 0

        # Determine CRS type and pixel area in square meters
        is_geographic = "EPSG:4326" in crs_str or "GEOGRAPHIC" in crs_str or "DEGREE" in crs_str

        if is_geographic:
            # Check if resolution is in decimal degrees (e.g. < 0.1) or meters
            if res_m < 0.1:
                lat = latitude if latitude is not None else 0.0
                lat_rad = math.radians(lat)
                dy = res_m * 111320.0  # ~111.32 km per degree latitude
                dx = res_m * 111320.0 * math.cos(lat_rad)
                pixel_area_m2 = abs(dx * dy)
                calc_method = "GEODESIC_LATITUDE_COSINE_SCALED"
            else:
                pixel_area_m2 = res_m * res_m
                calc_method = "GEOGRAPHIC_EXPLICIT_METRIC_RESOLUTION"
        else:
            # Standard Projected CRS (e.g., UTM EPSG:32632)
            pixel_area_m2 = res_m * res_m
            calc_method = "PROJECTED_UTM_SQUARE_PIXEL"

        affected_m2 = affected_count * pixel_area_m2
        affected_ha = affected_m2 / 10000.0
        affected_km2 = affected_m2 / 1000000.0

        return AffectedAreaResult(
            event_id=mask_obj.event_id,
            disaster_type=mask_obj.disaster_type,
            affected_pixel_count=affected_count,
            pixel_area_m2=pixel_area_m2,
            affected_area_m2=affected_m2,
            affected_area_hectares=affected_ha,
            affected_area_km2=affected_km2,
            CRS=mask_obj.CRS,
            resolution_m=res_m,
            method=calc_method,
            provenance=mask_obj.provenance,
        )


def calculate_affected_area(
    event_or_mask: Any, latitude: Optional[float] = None, config_path: Optional[Union[str, Path]] = None
) -> AffectedAreaResult:
    """
    Public helper function API for calculating affected area.

    Accepts a DisasterMask, detection result, or event_id string.
    """
    calculator = AreaCalculator()

    if isinstance(event_or_mask, DisasterMask):
        return calculator.calculate_area(event_or_mask, latitude=latitude)

    # Generate mask first if input is event_id or detection result
    mask_obj = generate_disaster_mask(event_or_mask, config_path=config_path)

    # Extract latitude from event if available
    if latitude is None and isinstance(event_or_mask, str):
        try:
            ev = load_event(event_or_mask)
            latitude = ev.latitude
        except Exception:
            pass

    return calculator.calculate_area(mask_obj, latitude=latitude)
