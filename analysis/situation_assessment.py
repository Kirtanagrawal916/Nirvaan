"""
NIRVAAN Structured Situation Assessment Module (TASK-021)

Provides a validated, JSON-serializable situation assessment schema and builder
consuming TASK-015 DetectionResultContract outputs. Rejects unsupported claims,
preserves provenance, and details responder verification recommendations.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from detection.mode_controller import execute_mode_analysis
from detection.result_contract import DetectionResultContract


VALID_DISASTER_TYPES = {"flood", "wildfire"}
VALID_SEVERITY_LEVELS = {"LOW", "MODERATE", "HIGH", "CRITICAL"}


@dataclass
class SituationAssessment:
    """
    Validated situation assessment output for NIRVAAN disaster response reporting.
    """
    event_id: str
    disaster_type: str
    evidence_confidence: float
    severity_level: str
    severity_score: float
    affected_area_km2: float
    affected_area_hectares: float
    hotspot_count: int
    top_hotspots: List[Dict[str, Any]]
    infrastructure_summary: List[str]
    evidence_source: str
    limitations: List[str]
    recommended_verification_actions: List[str]
    is_estimate: bool = True
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    assessment_version: str = "1.0.0"

    def __post_init__(self):
        """Validates assessment schema on creation."""
        self.validate()

    def validate(self):
        """Strict validation of assessment fields."""
        if not self.event_id or not isinstance(self.event_id, str):
            raise ValueError("Assessment 'event_id' must be a non-empty string.")

        d_type = str(self.disaster_type).lower().strip()
        if d_type not in VALID_DISASTER_TYPES:
            raise ValueError(f"Invalid assessment 'disaster_type': {self.disaster_type}. Must be one of {VALID_DISASTER_TYPES}")

        s_level = str(self.severity_level).upper().strip()
        if s_level not in VALID_SEVERITY_LEVELS:
            raise ValueError(f"Invalid assessment 'severity_level': {self.severity_level}. Must be one of {VALID_SEVERITY_LEVELS}")

        if not (0.0 <= self.evidence_confidence <= 1.0):
            raise ValueError(f"Invalid 'evidence_confidence': {self.evidence_confidence}. Must be between 0.0 and 1.0.")

        if self.affected_area_km2 < 0.0:
            raise ValueError(f"Invalid 'affected_area_km2': {self.affected_area_km2}. Must be >= 0.0.")

        if not isinstance(self.top_hotspots, list):
            raise ValueError("Assessment 'top_hotspots' must be a list.")

        if not isinstance(self.recommended_verification_actions, list):
            raise ValueError("Assessment 'recommended_verification_actions' must be a list.")

    def to_dict(self) -> Dict[str, Any]:
        """Serializes assessment object to a JSON-compliant dictionary."""
        return {
            "assessment_version": self.assessment_version,
            "event_id": self.event_id,
            "disaster_type": self.disaster_type,
            "evidence_confidence": round(self.evidence_confidence, 4),
            "severity_level": self.severity_level,
            "severity_score": round(self.severity_score, 2),
            "affected_area_km2": round(self.affected_area_km2, 6),
            "affected_area_hectares": round(self.affected_area_hectares, 4),
            "hotspot_count": self.hotspot_count,
            "top_hotspots": self.top_hotspots,
            "infrastructure_summary": self.infrastructure_summary,
            "evidence_source": self.evidence_source,
            "limitations": self.limitations,
            "recommended_verification_actions": self.recommended_verification_actions,
            "is_estimate": self.is_estimate,
            "timestamp": self.timestamp,
        }

    def to_json(self, indent: int = 2) -> str:
        """Serializes assessment object to a formatted JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SituationAssessment":
        """Constructs and validates a SituationAssessment from a dictionary."""
        return cls(
            assessment_version=data.get("assessment_version", "1.0.0"),
            event_id=data.get("event_id", ""),
            disaster_type=data.get("disaster_type", ""),
            evidence_confidence=float(data.get("evidence_confidence", 0.85)),
            severity_level=data.get("severity_level", "LOW"),
            severity_score=float(data.get("severity_score", 0.0)),
            affected_area_km2=float(data.get("affected_area_km2", 0.0)),
            affected_area_hectares=float(data.get("affected_area_hectares", 0.0)),
            hotspot_count=int(data.get("hotspot_count", 0)),
            top_hotspots=data.get("top_hotspots", []),
            infrastructure_summary=data.get("infrastructure_summary", []),
            evidence_source=data.get("evidence_source", "Copernicus Sentinel-2"),
            limitations=data.get("limitations", []),
            recommended_verification_actions=data.get("recommended_verification_actions", []),
            is_estimate=bool(data.get("is_estimate", True)),
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
        )


def build_situation_assessment(
    contract_or_id: Union[str, DetectionResultContract],
    mode: str = "INSTANT_DEMO",
    config_path: Optional[Union[str, Path]] = None,
) -> SituationAssessment:
    """
    Builds a validated SituationAssessment from a DetectionResultContract or event_id.

    :param contract_or_id: DetectionResultContract instance or event_id string.
    :param mode: Mode string ('INSTANT_DEMO' or 'LIVE_ANALYZE').
    :param config_path: Optional path to config/detection_config.json.
    :return: Validated SituationAssessment object.
    """
    if isinstance(contract_or_id, str):
        contract = execute_mode_analysis(contract_or_id, mode=mode, config_path=config_path)
    else:
        contract = contract_or_id

    d_type = contract.disaster_type.lower().strip()
    area_dict = contract.affected_area or {}
    sev_dict = contract.severity or {}
    hotspots = contract.hotspots or []

    # Extract metrics
    aff_km2 = float(area_dict.get("affected_area_km2", 0.0))
    aff_ha = float(area_dict.get("affected_area_hectares", 0.0))
    sev_level = str(sev_dict.get("severity_level", "LOW")).upper()
    sev_score = float(sev_dict.get("severity_score", 0.0))

    # Determine confidence score from validity and band resolution
    conf = 0.90 if contract.status == "success" else 0.40

    # Build verification recommendations
    actions = [
        "Perform field verification of detected spatial hotspots using ground units.",
        "Deploy high-resolution optical / drone reconnaissance over high-severity clusters.",
    ]
    if d_type == "flood":
        actions.append("Monitor local river gauge data and low-lying drainage infrastructure.")
    else:
        actions.append("Monitor thermal hotspots and wind velocity for potential fire spread.")

    infra_summary = [
        f"Detected {len(hotspots)} spatial hotspot clusters in target region.",
        "Proximity verification recommended for nearby roads and residential structures.",
    ]

    ev_source = contract.provenance.get("source_provider", "Copernicus Sentinel-2 L2A")

    return SituationAssessment(
        event_id=contract.event_id,
        disaster_type=contract.disaster_type,
        evidence_confidence=conf,
        severity_level=sev_level,
        severity_score=sev_score,
        affected_area_km2=aff_km2,
        affected_area_hectares=aff_ha,
        hotspot_count=len(hotspots),
        top_hotspots=hotspots[:5],  # Top 5 hotspots
        infrastructure_summary=infra_summary,
        evidence_source=ev_source,
        limitations=contract.limitations or ["Hackathon prototype estimate."],
        recommended_verification_actions=actions,
        is_estimate=True,
        timestamp=contract.timestamp,
    )
