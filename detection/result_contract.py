"""
NIRVAAN Detection Result Contract Module (TASK-015)

Defines a stable, typed, fully-validated result contract combining outputs
from dataset loading, raster validation, multispectral preprocessing, disaster detection,
change detection, spatial mask generation, affected area calculation, severity classification,
and hotspot extraction.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from analysis.affected_area import AffectedAreaResult, calculate_affected_area
from analysis.hotspots import HotspotExtractionResult, extract_hotspots
from analysis.mask_generator import DisasterMask, generate_disaster_mask
from data.event_schema import DisasterEvent
from data.loader import load_event
from detection.change_detection import ChangeDetectionResult, detect_change
from detection.severity import SeverityResult, classify_severity


VALID_STATUSES = {"success", "partial", "failed"}
VALID_DISASTER_TYPES = {"flood", "wildfire"}


@dataclass
class DetectionResultContract:
    """
    Unified JSON-serializable Result Contract for NIRVAAN disaster detection runs.
    """
    event_id: str
    disaster_type: str
    status: str
    timestamp: str
    event_metadata: Dict[str, Any]
    detection_summary: Dict[str, Any]
    affected_area: Dict[str, Any]
    severity: Dict[str, Any]
    hotspots: List[Dict[str, Any]]
    mask_reference: Dict[str, Any]
    provenance: Dict[str, Any]
    warnings: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    contract_version: str = "1.0.0"

    def __post_init__(self):
        """Validates contract structure and values."""
        self.validate()

    def validate(self):
        """Strict validation of contract fields."""
        if not self.event_id or not isinstance(self.event_id, str):
            raise ValueError("Contract 'event_id' must be a non-empty string.")

        d_type = str(self.disaster_type).lower().strip()
        if d_type not in VALID_DISASTER_TYPES:
            raise ValueError(f"Invalid contract 'disaster_type': {self.disaster_type}. Must be one of {VALID_DISASTER_TYPES}")

        st = str(self.status).lower().strip()
        if st not in VALID_STATUSES:
            raise ValueError(f"Invalid contract 'status': {self.status}. Must be one of {VALID_STATUSES}")

        if not isinstance(self.event_metadata, dict):
            raise ValueError("Contract 'event_metadata' must be a dictionary.")

        if not isinstance(self.affected_area, dict):
            raise ValueError("Contract 'affected_area' must be a dictionary.")

        if not isinstance(self.severity, dict):
            raise ValueError("Contract 'severity' must be a dictionary.")

        if not isinstance(self.hotspots, list):
            raise ValueError("Contract 'hotspots' must be a list.")

        if not isinstance(self.mask_reference, dict):
            raise ValueError("Contract 'mask_reference' must be a dictionary.")

    def to_dict(self) -> Dict[str, Any]:
        """Serializes contract to a clean, JSON-compliant dictionary."""
        return {
            "contract_version": self.contract_version,
            "event_id": self.event_id,
            "disaster_type": self.disaster_type,
            "status": self.status,
            "timestamp": self.timestamp,
            "event_metadata": self.event_metadata,
            "detection_summary": self.detection_summary,
            "affected_area": self.affected_area,
            "severity": self.severity,
            "hotspots": self.hotspots,
            "mask_reference": self.mask_reference,
            "provenance": self.provenance,
            "warnings": self.warnings,
            "limitations": self.limitations,
        }

    def to_json(self, indent: int = 2) -> str:
        """Serializes contract to a formatted JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DetectionResultContract":
        """Constructs and validates a DetectionResultContract from a dictionary."""
        return cls(
            contract_version=data.get("contract_version", "1.0.0"),
            event_id=data.get("event_id", ""),
            disaster_type=data.get("disaster_type", ""),
            status=data.get("status", "failed"),
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            event_metadata=data.get("event_metadata", {}),
            detection_summary=data.get("detection_summary", {}),
            affected_area=data.get("affected_area", {}),
            severity=data.get("severity", {}),
            hotspots=data.get("hotspots", []),
            mask_reference=data.get("mask_reference", {}),
            provenance=data.get("provenance", {}),
            warnings=data.get("warnings", []),
            limitations=data.get("limitations", []),
        )


def build_detection_result_contract(
    event_or_id: Union[str, DisasterEvent],
    config_path: Optional[Union[str, Path]] = None,
) -> DetectionResultContract:
    """
    Executes complete NIRVAAN detection pipeline and builds a validated DetectionResultContract.

    :param event_or_id: Event ID string or DisasterEvent instance.
    :param config_path: Optional path to config/detection_config.json.
    :return: Validated DetectionResultContract object.
    """
    warnings: List[str] = []
    limitations: List[str] = [
        "Hackathon prototype thresholds; not an official emergency dispatch standard."
    ]

    try:
        if isinstance(event_or_id, str):
            event = load_event(event_or_id)
        else:
            event = event_or_id
    except Exception as e:
        # Construct failed result contract cleanly
        return DetectionResultContract(
            event_id=str(event_or_id) if isinstance(event_or_id, str) else "unknown-event",
            disaster_type="flood",
            status="failed",
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_metadata={},
            detection_summary={},
            affected_area={},
            severity={},
            hotspots=[],
            mask_reference={},
            provenance={},
            warnings=[f"Failed to load dataset: {str(e)}"],
            limitations=limitations,
        )

    # 1. Change detection
    change_res: ChangeDetectionResult = detect_change(event, config_path=config_path)

    # 2. Mask generation
    mask_obj: DisasterMask = generate_disaster_mask(change_res, config_path=config_path)

    # 3. Affected area calculation
    area_res: AffectedAreaResult = calculate_affected_area(mask_obj, latitude=event.latitude)

    # 4. Severity classification
    severity_res: SeverityResult = classify_severity(area_res, config_path=config_path)

    # 5. Hotspot extraction
    hotspot_res: HotspotExtractionResult = extract_hotspots(mask_obj, config_path=config_path)

    mask_ref = {
        "dimensions": list(mask_obj.dimensions),
        "CRS": mask_obj.CRS,
        "resolution_m": mask_obj.resolution_m,
        "valid_pixel_count": mask_obj.valid_pixel_count,
        "affected_pixel_count": mask_obj.affected_pixel_count,
        "transform": list(mask_obj.transform) if mask_obj.transform else None,
        "category_labels": mask_obj.category_labels,
    }

    event_meta = {
        "event_id": event.event_id,
        "disaster_type": event.disaster_type,
        "description": getattr(event, "description", ""),
        "latitude": event.latitude,
        "longitude": event.longitude,
        "before_date": event.before_date,
        "after_date": event.after_date,
    }

    return DetectionResultContract(
        event_id=event.event_id,
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
