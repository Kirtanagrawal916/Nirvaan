"""
NIRVAAN Wildfire Detection Module (TASK-009)

Implements NBR (Normalized Burn Ratio) and dNBR (Delta NBR) change detection
for wildfire events using Sentinel-2 NIR (B08) and SWIR-2 (B12) spectral bands.
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
class WildfireDetectionResult:
    """
    Structured detection output for NIRVAAN wildfire detection tasks.
    """
    event_id: str
    disaster_type: str
    method: str
    index_name: str
    threshold_used: Union[float, Dict[str, Any]]
    CRS: str
    resolution_m: float
    dimensions: Tuple[int, int]
    valid_pixel_count: int
    affected_pixel_count: int
    affected_ratio: float
    burn_mask: np.ndarray                 # Boolean/uint8 mask (1 = affected/burned, 0 = unaffected)
    dnbr_array: np.ndarray                # Float32 dNBR array (pre_fire_nbr - post_fire_nbr)
    pre_fire_nbr: np.ndarray              # Float32 pre-fire NBR array
    post_fire_nbr: np.ndarray             # Float32 post-fire NBR array
    severity_breakdown: Dict[str, int]    # Class name -> pixel count dictionary
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
            "severity_breakdown": self.severity_breakdown,
            "provenance": self.provenance,
        }


class WildfireDetector:
    """
    NBR and dNBR Wildfire & Burn Scar Detector engine.
    """

    def __init__(
        self,
        config_path: Optional[Union[str, Path]] = None,
        nir_band: str = "B08",
        swir_band: str = "B12",
    ):
        """
        Initialize WildfireDetector with configuration.

        :param config_path: Optional path to config/detection_config.json.
        :param nir_band: Band name for NIR (default 'B08').
        :param swir_band: Band name for SWIR (default 'B12').
        """
        self.config = self._load_config(config_path)

        wildfire_cfg = self.config.get("wildfire", {})
        proto_thresh = wildfire_cfg.get("prototype_thresholds", {})
        self.severity_classes = proto_thresh.get(
            "dnbr_severity_classes",
            {
                "unburned": {"min": -0.1, "max": 0.1, "label": "UNBURNED / LOW RISK"},
                "low_severity": {"min": 0.1, "max": 0.27, "label": "LOW SEVERITY"},
                "moderate_severity": {"min": 0.27, "max": 0.66, "label": "MODERATE SEVERITY"},
                "high_severity": {"min": 0.66, "max": 2.0, "label": "HIGH SEVERITY / CRITICAL"},
            },
        )

        req_bands_cfg = wildfire_cfg.get("required_bands", {})
        self.nir_band = req_bands_cfg.get("nir", nir_band).upper().strip()
        self.swir_band = req_bands_cfg.get("swir2", swir_band).upper().strip()

        # Burn threshold starts at low severity minimum (0.1)
        self.burn_threshold = float(self.severity_classes.get("low_severity", {}).get("min", 0.1))

        self.preprocessor = MultispectralPreprocessor()

    def _load_config(self, config_path: Optional[Union[str, Path]]) -> Dict[str, Any]:
        """Loads wildfire detection configuration from JSON file."""
        if config_path:
            p = Path(config_path)
        else:
            p = Path(__file__).resolve().parent.parent / "config" / "detection_config.json"

        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)

        return {"wildfire": {}}

    def calculate_nbr(self, raster: ProcessedRaster) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculates NBR index = (NIR - SWIR) / (NIR + SWIR).

        Handles zero denominators and nodata masks safely.
        :param raster: ProcessedRaster object containing NIR (B08) and SWIR (B12/B11) bands.
        :return: Tuple of (nbr_array, valid_mask).
        """
        nir = raster.get_band(self.nir_band).astype(np.float32)

        # Fallback to B11 if B12 not present
        if self.swir_band in raster.bands:
            swir = raster.get_band(self.swir_band).astype(np.float32)
        elif "B11" in raster.bands:
            swir = raster.get_band("B11").astype(np.float32)
        else:
            swir = raster.get_band("SWIR").astype(np.float32)

        valid = (raster.valid_mask if raster.valid_mask is not None else np.ones(nir.shape, dtype=bool))
        valid = valid & np.isfinite(nir) & np.isfinite(swir)

        denom = np.zeros_like(nir, dtype=np.float32)
        denom[valid] = nir[valid] + swir[valid]

        # Zero denominator safety mask
        zero_denom = np.isclose(denom, 0.0) | (denom < 1e-7) | ~np.isfinite(denom)
        valid = valid & ~zero_denom

        nbr = np.zeros_like(nir, dtype=np.float32)
        safe_denom = np.where(valid, np.maximum(denom, 1e-7), 1.0)
        np.divide(nir - swir, safe_denom, out=nbr, where=valid)

        # Sanitize residual NaNs/Infs
        nbr[~valid] = 0.0

        return nbr, valid

    def detect(self, event_or_id: Union[str, DisasterEvent]) -> WildfireDetectionResult:
        """
        Executes end-to-end wildfire change detection pipeline for an event or event_id.

        Pipeline:
        1. Load event using TASK-005 loader
        2. Validate imagery using TASK-006 validation layer
        3. Preprocess imagery using TASK-007 preprocessor
        4. Calculate pre-fire and post-fire NBR
        5. Calculate dNBR = pre_fire_nbr - post_fire_nbr
        6. Apply severity thresholds to generate burn mask and severity breakdown
        7. Return structured WildfireDetectionResult

        :param event_or_id: Event ID string or loaded DisasterEvent instance.
        :return: WildfireDetectionResult object.
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

        # 3. Calculate NBR for before and after
        pre_fire_nbr, before_valid = self.calculate_nbr(before_raster)
        post_fire_nbr, after_valid = self.calculate_nbr(after_raster)

        combined_valid = before_valid & after_valid

        # 4. Calculate dNBR = pre_fire_nbr - post_fire_nbr
        dnbr = np.zeros_like(pre_fire_nbr, dtype=np.float32)
        dnbr[combined_valid] = pre_fire_nbr[combined_valid] - post_fire_nbr[combined_valid]

        # 5. Generate burn mask (dNBR >= burn_threshold)
        burned = (dnbr >= self.burn_threshold) & combined_valid
        burn_mask = burned.astype(np.uint8)

        # 6. Calculate severity breakdown counts
        severity_breakdown = {}
        for class_key, class_info in self.severity_classes.items():
            min_v = float(class_info.get("min", -1.0))
            max_v = float(class_info.get("max", 2.0))
            class_mask = (dnbr >= min_v) & (dnbr < max_v) & combined_valid
            severity_breakdown[class_key] = int(np.sum(class_mask))

        valid_count = int(np.sum(combined_valid))
        affected_count = int(np.sum(burn_mask))
        affected_ratio = float(affected_count / valid_count) if valid_count > 0 else 0.0

        provenance = {
            "source_provider": event.source,
            "product_id": event.product_id,
            "tile_id": event.tile_id,
            "before_date": event.before_date,
            "after_date": event.after_date,
            "provenance_url": event.provenance_url,
        }

        return WildfireDetectionResult(
            event_id=event.event_id,
            disaster_type="wildfire",
            method="NBR_DNBR_DIFFERENCE",
            index_name="dNBR",
            threshold_used=self.severity_classes,
            CRS=event.CRS,
            resolution_m=event.resolution_m,
            dimensions=before_raster.dimensions,
            valid_pixel_count=valid_count,
            affected_pixel_count=affected_count,
            affected_ratio=affected_ratio,
            burn_mask=burn_mask,
            dnbr_array=dnbr,
            pre_fire_nbr=pre_fire_nbr,
            post_fire_nbr=post_fire_nbr,
            severity_breakdown=severity_breakdown,
            transform=before_raster.transform,
            provenance=provenance,
        )


def detect_wildfire(event_or_id: Union[str, DisasterEvent], config_path: Optional[Union[str, Path]] = None) -> WildfireDetectionResult:
    """Public helper API function for executing wildfire detection."""
    detector = WildfireDetector(config_path=config_path)
    return detector.detect(event_or_id)
