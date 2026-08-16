"""
NIRVAAN Disaster Severity Classification Module (TASK-013)

Provides deterministic, explainable severity classification for flood and wildfire
disaster events based on pipeline metrics and centralized prototype configuration.
"""

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

from analysis.affected_area import AffectedAreaResult, calculate_affected_area
from data.event_schema import DisasterEvent
from data.loader import load_event


@dataclass
class SeverityResult:
    """
    Structured severity classification result for NIRVAAN disaster analysis.
    """
    event_id: str
    disaster_type: str
    severity_level: str               # "LOW", "MODERATE", "HIGH", "CRITICAL"
    severity_score: float             # 0.0 to 100.0 numeric severity ranking
    severity_method: str
    input_metrics: Dict[str, Any]
    thresholds_used: Dict[str, Any]
    affected_area_km2: float
    provenance: Dict[str, Any] = field(default_factory=dict)
    limitations: str = (
        "Prototype scoring criteria for hackathon decision support; "
        "not an authoritative operational emergency standard."
    )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes severity classification output to a dictionary."""
        return {
            "event_id": self.event_id,
            "disaster_type": self.disaster_type,
            "severity_level": self.severity_level,
            "severity_score": round(self.severity_score, 2),
            "severity_method": self.severity_method,
            "input_metrics": self.input_metrics,
            "thresholds_used": self.thresholds_used,
            "affected_area_km2": round(self.affected_area_km2, 6),
            "provenance": self.provenance,
            "limitations": self.limitations,
        }


class SeverityClassifier:
    """
    Engine for classifying disaster severity levels and scores.
    """

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """Initialize SeverityClassifier with configuration."""
        self.config = self._load_config(config_path)

    def _load_config(self, config_path: Optional[Union[str, Path]]) -> Dict[str, Any]:
        """Loads configuration from JSON file."""
        if config_path:
            p = Path(config_path)
        else:
            p = Path(__file__).resolve().parent.parent / "config" / "detection_config.json"

        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)

        return {}

    def classify_flood_severity(
        self,
        area_result: AffectedAreaResult,
        affected_ratio: Optional[float] = None,
    ) -> SeverityResult:
        """
        Classifies flood disaster severity based on affected area ratio and ground extent.

        Bands (per implementations.md):
        0 - 20%: LOW
        20 - 50%: MODERATE
        50 - 75%: HIGH
        75%+: CRITICAL
        """
        ratio = affected_ratio if affected_ratio is not None else 0.0
        # If ratio not explicitly provided, estimate from affected area vs default grid
        if affected_ratio is None and area_result.affected_area_km2 > 0:
            # Prototype scaling: 10 km2 = ~25% moderate
            ratio = min(area_result.affected_area_km2 / 40.0, 1.0)

        pct = ratio * 100.0

        if pct < 20.0:
            level = "LOW"
            score = pct  # 0 to 20
        elif pct < 50.0:
            level = "MODERATE"
            score = pct  # 20 to 50
        elif pct < 75.0:
            level = "HIGH"
            score = pct  # 50 to 75
        else:
            level = "CRITICAL"
            score = min(pct, 100.0)  # 75 to 100

        thresholds = {
            "low": "< 20%",
            "moderate": "20% - 50%",
            "high": "50% - 75%",
            "critical": ">= 75%",
        }

        metrics = {
            "affected_pixel_count": area_result.affected_pixel_count,
            "affected_area_km2": area_result.affected_area_km2,
            "affected_ratio_percent": round(pct, 2),
        }

        return SeverityResult(
            event_id=area_result.event_id,
            disaster_type="flood",
            severity_level=level,
            severity_score=score,
            severity_method="FLOOD_AREA_RATIO_PROTOTYPE",
            input_metrics=metrics,
            thresholds_used=thresholds,
            affected_area_km2=area_result.affected_area_km2,
            provenance=area_result.provenance,
        )

    def classify_wildfire_severity(
        self,
        area_result: AffectedAreaResult,
        severity_breakdown: Optional[Dict[str, int]] = None,
    ) -> SeverityResult:
        """
        Classifies wildfire disaster severity based on dNBR burn severity breakdown and area.
        """
        breakdown = severity_breakdown or {}
        low_cnt = breakdown.get("low_severity", 0)
        mod_cnt = breakdown.get("moderate_severity", 0)
        high_cnt = breakdown.get("high_severity", 0)
        total_burned = low_cnt + mod_cnt + high_cnt

        if total_burned > 0:
            # Weighted severity index: (1*low + 2*mod + 3*high) / (3 * total)
            weighted_severity = (1.0 * low_cnt + 2.0 * mod_cnt + 3.0 * high_cnt) / (3.0 * total_burned)
            score = weighted_severity * 100.0
        else:
            score = 0.0

        if score < 25.0:
            level = "LOW"
        elif score < 55.0:
            level = "MODERATE"
        elif score < 80.0:
            level = "HIGH"
        else:
            level = "CRITICAL"

        thresholds = {
            "dnbr_classes": self.config.get("wildfire", {}).get("prototype_thresholds", {}).get("dnbr_severity_classes", {}),
            "score_bands": {
                "low": "< 25",
                "moderate": "25 - 55",
                "high": "55 - 80",
                "critical": ">= 80",
            },
        }

        metrics = {
            "affected_pixel_count": area_result.affected_pixel_count,
            "affected_area_km2": area_result.affected_area_km2,
            "severity_breakdown": breakdown,
            "weighted_burn_severity_index": round(score / 100.0, 4),
        }

        return SeverityResult(
            event_id=area_result.event_id,
            disaster_type="wildfire",
            severity_level=level,
            severity_score=score,
            severity_method="WILDFIRE_DNBR_WEIGHTED_INDEX_PROTOTYPE",
            input_metrics=metrics,
            thresholds_used=thresholds,
            affected_area_km2=area_result.affected_area_km2,
            provenance=area_result.provenance,
        )

    def classify_event(self, event_or_id: Union[str, DisasterEvent]) -> SeverityResult:
        """
        Executes end-to-end severity classification for a disaster event.

        :param event_or_id: Event ID string or DisasterEvent instance.
        :return: SeverityResult object.
        """
        if isinstance(event_or_id, str):
            event = load_event(event_or_id)
        else:
            event = event_or_id

        area_res = calculate_affected_area(event.event_id, config_path=None)

        if event.disaster_type.lower() == "flood":
            return self.classify_flood_severity(area_res)
        else:
            return self.classify_wildfire_severity(area_res)


def classify_severity(
    event_or_area: Any, config_path: Optional[Union[str, Path]] = None
) -> SeverityResult:
    """Public helper function API for classifying disaster severity."""
    classifier = SeverityClassifier(config_path=config_path)

    if isinstance(event_or_area, AffectedAreaResult):
        if event_or_area.disaster_type == "flood":
            return classifier.classify_flood_severity(event_or_area)
        else:
            return classifier.classify_wildfire_severity(event_or_area)
    else:
        return classifier.classify_event(event_or_area)
