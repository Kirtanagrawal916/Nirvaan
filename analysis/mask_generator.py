"""
NIRVAAN Disaster Mask Generator & Visualization Module (TASK-011)

Converts disaster detection and change outputs into clean, deterministic
spatial mask representations and visualization-ready RGBA color overlays.
"""

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import numpy as np

from detection.change_detection import ChangeDetectionResult, detect_change
from detection.flood_detector import FloodDetectionResult, detect_flood
from detection.wildfire_detector import WildfireDetectionResult, detect_wildfire


# Default hex color palette matching config/detection_config.json
DEFAULT_LAYER_COLORS = {
    "flood_mask": "#0066FF",
    "unburned": "#2ECC71",
    "low_severity": "#F1C40F",
    "moderate_severity": "#E67E22",
    "high_severity": "#E74C3C",
    "background": "#000000",
}


def hex_to_rgba(hex_code: str, alpha: int = 200) -> Tuple[int, int, int, int]:
    """Converts hex color string (e.g. '#0066FF') to (R, G, B, A) uint8 tuple."""
    clean_hex = hex_code.lstrip("#")
    if len(clean_hex) == 6:
        r = int(clean_hex[0:2], 16)
        g = int(clean_hex[2:4], 16)
        b = int(clean_hex[4:6], 16)
        return r, g, b, alpha
    return 0, 0, 0, 0


@dataclass
class DisasterMask:
    """
    Structured spatial mask object for NIRVAAN disaster impact analysis.
    """
    event_id: str
    disaster_type: str
    mask: np.ndarray                         # Uint8 categorical or binary spatial mask
    dimensions: Tuple[int, int]
    CRS: str
    resolution_m: float
    valid_pixel_count: int
    affected_pixel_count: int
    transform: Optional[Tuple[float, ...]] = None
    category_labels: Dict[int, str] = field(default_factory=dict)
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes summary metadata without huge raw mask arrays."""
        return {
            "event_id": self.event_id,
            "disaster_type": self.disaster_type,
            "dimensions": self.dimensions,
            "CRS": self.CRS,
            "resolution_m": self.resolution_m,
            "valid_pixel_count": self.valid_pixel_count,
            "affected_pixel_count": self.affected_pixel_count,
            "category_labels": self.category_labels,
            "provenance": self.provenance,
        }


class MaskGenerator:
    """
    Mask Generator and Visualization Renderer engine.
    """

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """Initialize MaskGenerator with centralized configuration colors."""
        self.config = self._load_config(config_path)

        mapping_cfg = self.config.get("mapping", {})
        self.layer_colors = mapping_cfg.get("layer_colors", DEFAULT_LAYER_COLORS)

    def _load_config(self, config_path: Optional[Union[str, Path]]) -> Dict[str, Any]:
        """Loads configuration from JSON file."""
        if config_path:
            p = Path(config_path)
        else:
            p = Path(__file__).resolve().parent.parent / "config" / "detection_config.json"

        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)

        return {"mapping": {"layer_colors": DEFAULT_LAYER_COLORS}}

    def from_flood_result(self, result: FloodDetectionResult) -> DisasterMask:
        """Constructs a DisasterMask from a FloodDetectionResult."""
        labels = {0: "Unaffected / Land", 1: "Inundated Water"}

        return DisasterMask(
            event_id=result.event_id,
            disaster_type="flood",
            mask=result.flood_mask.astype(np.uint8),
            dimensions=result.dimensions,
            CRS=result.CRS,
            resolution_m=result.resolution_m,
            valid_pixel_count=result.valid_pixel_count,
            affected_pixel_count=result.affected_pixel_count,
            transform=result.transform,
            category_labels=labels,
            provenance=result.provenance,
        )

    def from_wildfire_result(self, result: WildfireDetectionResult) -> DisasterMask:
        """Constructs a categorical severity DisasterMask from a WildfireDetectionResult."""
        h, w = result.dimensions
        cat_mask = np.zeros((h, w), dtype=np.uint8)

        # Map dNBR severity categories to uint8 codes:
        # 0: Unburned / Low Risk
        # 1: Low Severity
        # 2: Moderate Severity
        # 3: High Severity
        dnbr = result.dnbr_array

        cat_mask[(dnbr >= 0.1) & (dnbr < 0.27)] = 1
        cat_mask[(dnbr >= 0.27) & (dnbr < 0.66)] = 2
        cat_mask[dnbr >= 0.66] = 3

        labels = {
            0: "Unburned / Low Risk",
            1: "Low Severity Burn",
            2: "Moderate Severity Burn",
            3: "High Severity Burn",
        }

        affected_count = int(np.sum(cat_mask > 0))

        return DisasterMask(
            event_id=result.event_id,
            disaster_type="wildfire",
            mask=cat_mask,
            dimensions=result.dimensions,
            CRS=result.CRS,
            resolution_m=result.resolution_m,
            valid_pixel_count=result.valid_pixel_count,
            affected_pixel_count=affected_count,
            transform=result.transform,
            category_labels=labels,
            provenance=result.provenance,
        )

    def from_change_result(self, result: ChangeDetectionResult) -> DisasterMask:
        """Constructs a DisasterMask from a ChangeDetectionResult."""
        labels = {0: "No Change", 1: "Detected Change"}

        return DisasterMask(
            event_id=result.event_id,
            disaster_type=result.disaster_type,
            mask=result.change_mask.astype(np.uint8),
            dimensions=result.dimensions,
            CRS=result.CRS,
            resolution_m=result.resolution_m,
            valid_pixel_count=result.valid_pixel_count,
            affected_pixel_count=result.changed_pixel_count,
            transform=result.transform,
            category_labels=labels,
            provenance=result.provenance,
        )

    def render_mask_rgba(self, mask_obj: DisasterMask) -> np.ndarray:
        """
        Renders a DisasterMask as an RGBA uint8 image array (height, width, 4).
        Uses centralized configured colors for categories.

        :param mask_obj: DisasterMask instance.
        :return: (H, W, 4) uint8 NumPy array suitable for visualization.
        """
        h, w = mask_obj.dimensions
        rgba = np.zeros((h, w, 4), dtype=np.uint8)

        if mask_obj.disaster_type == "flood":
            color = hex_to_rgba(self.layer_colors.get("flood_mask", "#0066FF"), alpha=200)
            rgba[mask_obj.mask == 1] = color

        elif mask_obj.disaster_type == "wildfire":
            c_low = hex_to_rgba(self.layer_colors.get("low_severity", "#F1C40F"), alpha=200)
            c_mod = hex_to_rgba(self.layer_colors.get("moderate_severity", "#E67E22"), alpha=200)
            c_high = hex_to_rgba(self.layer_colors.get("high_severity", "#E74C3C"), alpha=220)

            rgba[mask_obj.mask == 1] = c_low
            rgba[mask_obj.mask == 2] = c_mod
            rgba[mask_obj.mask == 3] = c_high

        else:
            color = hex_to_rgba(self.layer_colors.get("flood_mask", "#0066FF"), alpha=200)
            rgba[mask_obj.mask == 1] = color

        return rgba


# Helper function API
def generate_disaster_mask(
    event_or_result: Any, config_path: Optional[Union[str, Path]] = None
) -> DisasterMask:
    """Public helper function API for generating a DisasterMask from detection or change results."""
    generator = MaskGenerator(config_path=config_path)

    if isinstance(event_or_result, FloodDetectionResult):
        return generator.from_flood_result(event_or_result)
    elif isinstance(event_or_result, WildfireDetectionResult):
        return generator.from_wildfire_result(event_or_result)
    elif isinstance(event_or_result, ChangeDetectionResult):
        return generator.from_change_result(event_or_result)
    elif isinstance(event_or_result, str):
        # Auto-detect change from event_id string
        change_res = detect_change(event_or_result, config_path=config_path)
        return generator.from_change_result(change_res)
    else:
        raise TypeError(f"Unsupported input type for mask generation: {type(event_or_result)}")
