"""
NIRVAAN Flood Detection Module (TASK-008)

Implements NDWI (Normalized Difference Water Index) disaster detection for flood events
using Sentinel-2 Green (B03) and NIR (B08) spectral bands.
"""

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import numpy as np

from data.event_schema import DisasterEvent
from data.loader import load_event
from preprocessing.preprocess import MultispectralPreprocessor, ProcessedRaster
from preprocessing.raster_validator import validate_event_images


@dataclass
class FloodDetectionResult:
    """
    Structured detection output for NIRVAAN flood detection tasks.
    """
    event_id: str
    disaster_type: str
    method: str
    index_name: str
    threshold_used: float
    CRS: str
    resolution_m: float
    dimensions: Tuple[int, int]
    valid_pixel_count: int
    affected_pixel_count: int
    affected_ratio: float
    flood_mask: np.ndarray          # Boolean/uint8 mask (1 = affected/flooded, 0 = unaffected)
    before_ndwi: np.ndarray         # NDWI float array for pre-event image
    after_ndwi: np.ndarray          # NDWI float array for post-event image
    transform: Optional[Tuple[float, ...]] = None
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes summary metadata without huge raw pixel arrays."""
        return {
            "event_id": self.event_id,
            "disaster_type": self.disaster_type,
            "method": self.method,
            "index_name": self.index_name,
            "threshold_used": self.threshold_used,
            "CRS": self.CRS,
            "resolution_m": self.resolution_m,
            "dimensions": self.dimensions,
            "valid_pixel_count": self.valid_pixel_count,
            "affected_pixel_count": self.affected_pixel_count,
            "affected_ratio": round(self.affected_ratio, 6),
            "provenance": self.provenance,
        }


class FloodDetector:
    """
    NDWI Flood Detector engine.
    """

    def __init__(self, config_path: Optional[Union[str, Path]] = None, threshold_override: Optional[float] = None):
        """
        Initialize FloodDetector with configuration.

        :param config_path: Optional path to config/detection_config.json.
        :param threshold_override: Optional threshold override for testing.
        """
        self.config = self._load_config(config_path)

        flood_cfg = self.config.get("flood", {})
        proto_thresh = flood_cfg.get("prototype_thresholds", {})

        if threshold_override is not None:
            self.ndwi_threshold = threshold_override
        else:
            self.ndwi_threshold = float(proto_thresh.get("ndwi_water_threshold", 0.0))

        self.preprocessor = MultispectralPreprocessor()

    def _load_config(self, config_path: Optional[Union[str, Path]]) -> Dict[str, Any]:
        """Loads detection configuration from JSON file."""
        if config_path:
            p = Path(config_path)
        else:
            p = Path(__file__).resolve().parent.parent / "config" / "detection_config.json"

        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)

        return {"flood": {"prototype_thresholds": {"ndwi_water_threshold": 0.0}}}

    def calculate_ndwi(self, raster: ProcessedRaster) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculates NDWI index = (B03 - B08) / (B03 + B08).

        Handles zero denominators and nodata masks safely.
        :param raster: ProcessedRaster object containing B03 (Green) and B08 (NIR) bands.
        :return: Tuple of (ndwi_array, valid_mask).
        """
        green = raster.get_band("B03").astype(np.float32)
        nir = raster.get_band("B08").astype(np.float32)

        denom = green + nir
        valid = (raster.valid_mask if raster.valid_mask is not None else np.ones(green.shape, dtype=bool))
        valid = valid & ~np.isnan(green) & ~np.isnan(nir)

        # Zero denominator safety mask
        zero_denom = np.isclose(denom, 0.0) | (denom < 1e-7)
        valid = valid & ~zero_denom

        ndwi = np.zeros_like(green, dtype=np.float32)
        np.divide(green - nir, np.maximum(denom, 1e-7), out=ndwi, where=valid)

        # Sanitize any residual NaNs or Infs
        ndwi[~valid] = 0.0

        return ndwi, valid

    def detect(self, event_or_id: Union[str, DisasterEvent]) -> FloodDetectionResult:
        """
        Executes end-to-end flood detection pipeline for an event or event_id.

        Pipeline:
        1. Load event using TASK-005 loader
        2. Validate imagery using TASK-006 validation layer
        3. Preprocess imagery using TASK-007 preprocessor
        4. Calculate before and after NDWI
        5. Apply prototype threshold to detect newly inundated water pixels
        6. Return structured FloodDetectionResult

        :param event_or_id: Event ID string or loaded DisasterEvent instance.
        :return: FloodDetectionResult object.
        """
        if isinstance(event_or_id, str):
            event = load_event(event_or_id)
        else:
            event = event_or_id

        # 1. Validate raster inputs
        val_res = validate_event_images(event)
        if not val_res.is_valid:
            err_msgs = "; ".join(str(e) for e in val_res.errors)
            raise ValueError(f"Event '{event.event_id}' failed raster validation: {err_msgs}")

        # 2. Preprocess before and after rasters
        before_raster, after_raster = self.preprocessor.preprocess_event(event)

        # 3. Calculate NDWI for before and after
        before_ndwi, before_valid = self.calculate_ndwi(before_raster)
        after_ndwi, after_valid = self.calculate_ndwi(after_raster)

        combined_valid = before_valid & after_valid

        # 4. Generate deterministic flood mask
        # Water in after image (after_ndwi > threshold) AND newly flooded (or post-event water extent)
        post_water = (after_ndwi > self.ndwi_threshold) & combined_valid
        pre_water = (before_ndwi > self.ndwi_threshold) & combined_valid

        # Newly inundated pixels (water in after image that was not water in before image)
        newly_flooded = post_water & (~pre_water)

        # Binary uint8 mask (1 = affected/flooded, 0 = unaffected)
        flood_mask = newly_flooded.astype(np.uint8)

        valid_count = int(np.sum(combined_valid))
        affected_count = int(np.sum(flood_mask))
        affected_ratio = float(affected_count / valid_count) if valid_count > 0 else 0.0

        provenance = {
            "source_provider": event.source,
            "product_id": event.product_id,
            "tile_id": event.tile_id,
            "before_date": event.before_date,
            "after_date": event.after_date,
            "provenance_url": event.provenance_url,
        }

        return FloodDetectionResult(
            event_id=event.event_id,
            disaster_type="flood",
            method="NDWI_DIFFERENCE",
            index_name="NDWI",
            threshold_used=self.ndwi_threshold,
            CRS=event.CRS,
            resolution_m=event.resolution_m,
            dimensions=before_raster.dimensions,
            valid_pixel_count=valid_count,
            affected_pixel_count=affected_count,
            affected_ratio=affected_ratio,
            flood_mask=flood_mask,
            before_ndwi=before_ndwi,
            after_ndwi=after_ndwi,
            transform=before_raster.transform,
            provenance=provenance,
        )


def detect_flood(event_or_id: Union[str, DisasterEvent], config_path: Optional[Union[str, Path]] = None) -> FloodDetectionResult:
    """Public helper API function for executing flood detection."""
    detector = FloodDetector(config_path=config_path)
    return detector.detect(event_or_id)
