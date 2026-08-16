"""
NIRVAAN Orchestrated Detection Pipeline (TASK-016)

Orchestrates dataset loading, raster validation, multispectral preprocessing,
disaster detection, change detection, mask generation, affected area calculation,
severity classification, and hotspot extraction into a unified execution pipeline
returning a validated TASK-015 DetectionResultContract.
"""

from datetime import datetime, timezone
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

from analysis.affected_area import AffectedAreaResult, AreaCalculator
from analysis.hotspots import HotspotExtractionResult, HotspotExtractor
from analysis.mask_generator import DisasterMask, MaskGenerator
from data.event_schema import DisasterEvent
from data.loader import DatasetLoader, load_event
from detection.change_detection import ChangeDetectionResult, ChangeDetector
from detection.flood_detector import FloodDetectionResult, FloodDetector
from detection.result_contract import DetectionResultContract
from detection.severity import SeverityClassifier, SeverityResult
from detection.wildfire_detector import WildfireDetectionResult, WildfireDetector
from preprocessing.preprocess import MultispectralPreprocessor, ProcessedRaster
from preprocessing.raster_validator import validate_event_images


logger = logging.getLogger("nirvaan.pipeline")


class DetectionPipeline:
    """
    End-to-end satellite imagery disaster detection pipeline orchestrator.
    """

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """Initialize pipeline components with configuration."""
        self.config_path = config_path
        self.loader = DatasetLoader()
        self.preprocessor = MultispectralPreprocessor()
        self.flood_detector = FloodDetector(config_path=config_path)
        self.wildfire_detector = WildfireDetector(config_path=config_path)
        self.change_detector = ChangeDetector(config_path=config_path)
        self.mask_generator = MaskGenerator(config_path=config_path)
        self.area_calculator = AreaCalculator()
        self.severity_classifier = SeverityClassifier(config_path=config_path)
        self.hotspot_extractor = HotspotExtractor()

    def run(
        self,
        event_or_id: Union[str, DisasterEvent],
        mode: str = "LIVE_ANALYZE",
    ) -> DetectionResultContract:
        """
        Executes complete end-to-end detection pipeline for a given event.

        :param event_or_id: Event ID string or DisasterEvent instance.
        :param mode: Execution mode ('LIVE_ANALYZE' or 'INSTANT_DEMO').
        :return: DetectionResultContract object.
        """
        warnings = []
        limitations = [
            "Hackathon prototype pipeline; not an official emergency dispatch system."
        ]

        # 1. Dataset Loading Stage
        try:
            if isinstance(event_or_id, str):
                event = self.loader.load_event(event_or_id)
            else:
                event = event_or_id
        except Exception as e:
            return self._build_failed_contract(
                event_id=str(event_or_id) if isinstance(event_or_id, str) else "unknown-event",
                disaster_type="flood",
                stage="Dataset Loading",
                error_msg=str(e),
            )

        event_id = event.event_id
        disaster_type = event.disaster_type.lower().strip()

        event_meta = {
            "event_id": event.event_id,
            "disaster_type": event.disaster_type,
            "description": getattr(event, "description", ""),
            "latitude": event.latitude,
            "longitude": event.longitude,
            "before_date": event.before_date,
            "after_date": event.after_date,
        }

        # 2. Raster Validation Stage
        val_res = validate_event_images(event)
        if not val_res.is_valid:
            err_str = "; ".join(str(e) for e in val_res.errors)
            return self._build_failed_contract(
                event_id=event_id,
                disaster_type=disaster_type,
                stage="Raster Validation",
                error_msg=err_str,
                event_metadata=event_meta,
            )

        # 3. Multispectral Preprocessing Stage
        try:
            before_proc, after_proc = self.preprocessor.preprocess_event(event)
        except Exception as e:
            return self._build_failed_contract(
                event_id=event_id,
                disaster_type=disaster_type,
                stage="Multispectral Preprocessing",
                error_msg=str(e),
                event_metadata=event_meta,
            )

        # 4. Disaster Detection & Change Detection Stage
        try:
            if disaster_type == "flood":
                det_res = self.flood_detector.detect(event)
                change_res = self.change_detector.detect_change(event)
            elif disaster_type == "wildfire":
                det_res = self.wildfire_detector.detect(event)
                change_res = self.change_detector.detect_change(event)
            else:
                return self._build_failed_contract(
                    event_id=event_id,
                    disaster_type=disaster_type,
                    stage="Disaster Detector Routing",
                    error_msg=f"Unsupported disaster type: '{disaster_type}'",
                    event_metadata=event_meta,
                )
        except Exception as e:
            return self._build_failed_contract(
                event_id=event_id,
                disaster_type=disaster_type,
                stage="Disaster Detection",
                error_msg=str(e),
                event_metadata=event_meta,
            )

        # 5. Mask Generation Stage
        try:
            mask_obj = self.mask_generator.from_change_result(change_res)
        except Exception as e:
            return self._build_failed_contract(
                event_id=event_id,
                disaster_type=disaster_type,
                stage="Mask Generation",
                error_msg=str(e),
                event_metadata=event_meta,
            )

        # 6. Affected Area Calculation Stage
        try:
            area_res = self.area_calculator.calculate_area(mask_obj, latitude=event.latitude)
        except Exception as e:
            return self._build_failed_contract(
                event_id=event_id,
                disaster_type=disaster_type,
                stage="Affected Area Calculation",
                error_msg=str(e),
                event_metadata=event_meta,
            )

        # 7. Severity Classification Stage
        try:
            if disaster_type == "flood":
                severity_res = self.severity_classifier.classify_flood_severity(
                    area_res, affected_ratio=change_res.changed_ratio
                )
            else:
                wildfire_det = det_res if isinstance(det_res, WildfireDetectionResult) else None
                breakdown = wildfire_det.severity_breakdown if wildfire_det else None
                severity_res = self.severity_classifier.classify_wildfire_severity(
                    area_res, severity_breakdown=breakdown
                )
        except Exception as e:
            return self._build_failed_contract(
                event_id=event_id,
                disaster_type=disaster_type,
                stage="Severity Classification",
                error_msg=str(e),
                event_metadata=event_meta,
            )

        # 8. Hotspot Extraction Stage
        try:
            hotspot_res = self.hotspot_extractor.extract_hotspots(
                mask_obj, event_center_lat=event.latitude, event_center_lon=event.longitude
            )
        except Exception as e:
            warnings.append(f"Hotspot extraction warning: {str(e)}")
            hotspot_res = HotspotExtractionResult(
                event_id=event_id,
                disaster_type=disaster_type,
                total_hotspots=0,
                hotspots=[],
                CRS=mask_obj.CRS,
                resolution_m=mask_obj.resolution_m,
                min_pixels_filter=10,
                provenance=change_res.provenance,
            )

        # Assemble Mask Reference
        mask_ref = {
            "dimensions": list(mask_obj.dimensions),
            "CRS": mask_obj.CRS,
            "resolution_m": mask_obj.resolution_m,
            "valid_pixel_count": mask_obj.valid_pixel_count,
            "affected_pixel_count": mask_obj.affected_pixel_count,
            "transform": list(mask_obj.transform) if mask_obj.transform else None,
            "category_labels": mask_obj.category_labels,
        }

        # Return validated DetectionResultContract
        return DetectionResultContract(
            event_id=event_id,
            disaster_type=event.disaster_type,
            status="success",
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_metadata=event_meta,
            detection_summary=change_res.to_dict(),
            affected_area=area_res.to_dict(),
            severity=severity_res.to_dict(),
            hotspots=hotspot_res.to_dict()["hotspots"],
            mask_reference=mask_ref,
            provenance=change_res.provenance,
            warnings=warnings,
            limitations=limitations,
        )

    def _build_failed_contract(
        self,
        event_id: str,
        disaster_type: str,
        stage: str,
        error_msg: str,
        event_metadata: Optional[Dict[str, Any]] = None,
    ) -> DetectionResultContract:
        """Constructs a structured failed DetectionResultContract."""
        return DetectionResultContract(
            event_id=event_id,
            disaster_type=disaster_type if disaster_type in {"flood", "wildfire"} else "flood",
            status="failed",
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_metadata=event_metadata or {},
            detection_summary={"failed_stage": stage},
            affected_area={},
            severity={},
            hotspots=[],
            mask_reference={},
            provenance={},
            warnings=[f"Pipeline failed at stage '{stage}': {error_msg}"],
            limitations=["Pipeline execution unfulfilled due to error."],
        )


def run_detection(
    event_or_id: Union[str, DisasterEvent],
    mode: str = "LIVE_ANALYZE",
    config_path: Optional[Union[str, Path]] = None,
) -> DetectionResultContract:
    """Public helper API for running the orchestrated detection pipeline."""
    pipeline = DetectionPipeline(config_path=config_path)
    return pipeline.run(event_or_id, mode=mode)
