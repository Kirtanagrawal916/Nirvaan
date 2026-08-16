"""
NIRVAAN Disaster Change Detection Module (TASK-010)

Provides a unified change detection layer consuming outputs from disaster-specific
detection pipelines (NDWI for flood, NBR/dNBR for wildfire).
"""

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import numpy as np

from data.event_schema import DisasterEvent
from data.loader import load_event
from detection.flood_detector import FloodDetectionResult, FloodDetector
from detection.wildfire_detector import WildfireDetectionResult, WildfireDetector


@dataclass
class ChangeDetectionResult:
    """
    Structured output for NIRVAAN change detection tasks.
    """
    event_id: str
    disaster_type: str
    method: str
    threshold: Union[float, Dict[str, Any]]
    CRS: str
    resolution_m: float
    dimensions: Tuple[int, int]
    valid_pixel_count: int
    changed_pixel_count: int
    changed_ratio: float
    change_mask: np.ndarray                 # Boolean/uint8 mask (1 = change detected, 0 = no change)
    before_index: np.ndarray                # Float32 spectral index before event
    after_index: np.ndarray                 # Float32 spectral index after event
    difference_index: np.ndarray            # Float32 index difference (after - before or dNBR)
    transform: Optional[Tuple[float, ...]] = None
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes summary metadata without huge raw pixel arrays."""
        return {
            "event_id": self.event_id,
            "disaster_type": self.disaster_type,
            "method": self.method,
            "threshold": self.threshold,
            "CRS": self.CRS,
            "resolution_m": self.resolution_m,
            "dimensions": self.dimensions,
            "valid_pixel_count": self.valid_pixel_count,
            "changed_pixel_count": self.changed_pixel_count,
            "changed_ratio": round(self.changed_ratio, 6),
            "provenance": self.provenance,
        }


class ChangeDetector:
    """
    Unified Change Detector engine for flood and wildfire disaster events.
    """

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """Initialize ChangeDetector with detectors."""
        self.flood_detector = FloodDetector(config_path=config_path)
        self.wildfire_detector = WildfireDetector(config_path=config_path)

    def compute_difference(
        self,
        before: np.ndarray,
        after: np.ndarray,
        valid_mask: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Computes numeric difference (after - before) with NaN/Inf and nodata safety.

        :param before: Float array of pre-event values.
        :param after: Float array of post-event values.
        :param valid_mask: Optional boolean valid mask.
        :return: Tuple of (difference_array, combined_valid_mask).
        """
        b_arr = before.astype(np.float32)
        a_arr = after.astype(np.float32)

        valid = ~np.isnan(b_arr) & ~np.isnan(a_arr) & ~np.isinf(b_arr) & ~np.isinf(a_arr)
        if valid_mask is not None:
            valid = valid & valid_mask

        diff = np.zeros_like(b_arr, dtype=np.float32)
        np.subtract(a_arr, b_arr, out=diff, where=valid)

        diff[~valid] = 0.0
        return diff, valid

    def detect_change(self, event_or_id: Union[str, DisasterEvent]) -> ChangeDetectionResult:
        """
        Executes change detection pipeline based on disaster type.

        :param event_or_id: Event ID string or DisasterEvent object.
        :return: ChangeDetectionResult object.
        """
        if isinstance(event_or_id, str):
            event = load_event(event_or_id)
        else:
            event = event_or_id

        disaster_type = event.disaster_type.lower().strip()

        if disaster_type == "flood":
            return self._detect_flood_change(event)
        elif disaster_type == "wildfire":
            return self._detect_wildfire_change(event)
        else:
            raise ValueError(f"Unsupported disaster type for change detection: {disaster_type}")

        def _detect_flood_change(self, event: DisasterEvent) -> ChangeDetectionResult:
            flood_res: FloodDetectionResult = self.flood_detector.detect(event)

            diff, valid = self.compute_difference(
                flood_res.before_ndwi, flood_res.after_ndwi
            )

            return ChangeDetectionResult(
                event_id=flood_res.event_id,
                disaster_type="flood",
                method="NDWI_CHANGE_DETECTION",
                threshold=flood_res.threshold_used,
                CRS=flood_res.CRS,
                resolution_m=flood_res.resolution_m,
                dimensions=flood_res.dimensions,
                valid_pixel_count=flood_res.valid_pixel_count,
                changed_pixel_count=flood_res.affected_pixel_count,
                changed_ratio=flood_res.affected_ratio,
                change_mask=flood_res.flood_mask,
                before_index=flood_res.before_ndwi,
                after_index=flood_res.after_ndwi,
                difference_index=diff,
                transform=flood_res.transform,
                provenance=flood_res.provenance,
            )

    def _detect_flood_change(self, event: DisasterEvent) -> ChangeDetectionResult:
        flood_res: FloodDetectionResult = self.flood_detector.detect(event)

        diff, valid = self.compute_difference(
            flood_res.before_ndwi, flood_res.after_ndwi
        )

        return ChangeDetectionResult(
            event_id=flood_res.event_id,
            disaster_type="flood",
            method="NDWI_CHANGE_DETECTION",
            threshold=flood_res.threshold_used,
            CRS=flood_res.CRS,
            resolution_m=flood_res.resolution_m,
            dimensions=flood_res.dimensions,
            valid_pixel_count=flood_res.valid_pixel_count,
            changed_pixel_count=flood_res.affected_pixel_count,
            changed_ratio=flood_res.affected_ratio,
            change_mask=flood_res.flood_mask,
            before_index=flood_res.before_ndwi,
            after_index=flood_res.after_ndwi,
            difference_index=diff,
            transform=flood_res.transform,
            provenance=flood_res.provenance,
        )

    def _detect_wildfire_change(self, event: DisasterEvent) -> ChangeDetectionResult:
        wildfire_res: WildfireDetectionResult = self.wildfire_detector.detect(event)

        return ChangeDetectionResult(
            event_id=wildfire_res.event_id,
            disaster_type="wildfire",
            method="DNBR_CHANGE_DETECTION",
            threshold=wildfire_res.threshold_used,
            CRS=wildfire_res.CRS,
            resolution_m=wildfire_res.resolution_m,
            dimensions=wildfire_res.dimensions,
            valid_pixel_count=wildfire_res.valid_pixel_count,
            changed_pixel_count=wildfire_res.affected_pixel_count,
            changed_ratio=wildfire_res.affected_ratio,
            change_mask=wildfire_res.burn_mask,
            before_index=wildfire_res.pre_fire_nbr,
            after_index=wildfire_res.post_fire_nbr,
            difference_index=wildfire_res.dnbr_array,
            transform=wildfire_res.transform,
            provenance=wildfire_res.provenance,
        )


def detect_change(event_or_id: Union[str, DisasterEvent], config_path: Optional[Union[str, Path]] = None) -> ChangeDetectionResult:
    """Public helper function API for executing change detection."""
    detector = ChangeDetector(config_path=config_path)
    return detector.detect_change(event_or_id)
