"""
NIRVAAN Base Disaster Detector Interface (detection/detector_base.py)

Defines the abstract interface and data contracts for all disaster detectors.
Supports pluggable multi-disaster detection pipelines (Flood, Wildfire, Severe Weather)
ensuring uniform validation, preprocessing, inference, confidence scoring, geometry generation,
and explainable risk factor extraction.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union


@dataclass
class DetectorInput:
    """Standardized input payload for disaster detection runs."""
    latitude: float
    longitude: float
    location_name: str
    disaster_type: str
    time_window_days: int = 90
    max_cloud_cover: float = 60.0
    custom_params: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None


@dataclass
class DetectorOutput:
    """Standardized output payload from disaster detection runs."""
    status: str                                    # 'success' | 'no_hazard' | 'failed'
    event_id: str
    disaster_type: str
    location_name: str
    latitude: float
    longitude: float
    confidence_score: float                        # Model confidence (0 - 100)
    severity: str                                  # 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL'
    affected_area_km2: float
    geometry_geojson: Dict[str, Any]               # GeoJSON FeatureCollection
    satellite_info: Dict[str, Any]                 # STAC scene metadata & provenance
    model_metadata: Dict[str, Any]                 # Model version, duration, parameters
    risk_breakdown: Dict[str, Any]                 # Contributing risk factors
    provenance: Dict[str, Any]                     # Attribution, source type, timestamps
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converts detection output to dictionary for API & database persistence."""
        return {
            "status": self.status,
            "event_id": self.event_id,
            "disaster_type": self.disaster_type,
            "location_name": self.location_name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "confidence_score": round(self.confidence_score, 1),
            "severity": self.severity,
            "affected_area_km2": round(self.affected_area_km2, 2),
            "geometry_geojson": self.geometry_geojson,
            "satellite_info": self.satellite_info,
            "model_metadata": self.model_metadata,
            "risk_breakdown": self.risk_breakdown,
            "provenance": self.provenance,
            "error_message": self.error_message,
        }


class BaseDisasterDetector(ABC):
    """
    Abstract Base Class that every Nirvaan disaster detector must implement.
    """

    @property
    @abstractmethod
    def disaster_type(self) -> str:
        """Returns disaster identifier string (e.g. 'flood', 'wildfire', 'severe_weather')."""
        pass

    @property
    @abstractmethod
    def model_version(self) -> str:
        """Returns detector model and version identifier."""
        pass

    @abstractmethod
    def validate_input(self, inp: DetectorInput) -> Tuple[bool, Optional[str]]:
        """Validates input coordinates and parameters."""
        pass

    @abstractmethod
    def acquire_data(self, inp: DetectorInput) -> Dict[str, Any]:
        """Queries STAC satellite catalogs or authoritative external APIs."""
        pass

    @abstractmethod
    def preprocess(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocesses raw raster bands, metadata, or telemetry."""
        pass

    @abstractmethod
    def infer(self, preprocessed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Executes spectral thresholding or neural inference."""
        pass

    @abstractmethod
    def postprocess(self, inference_result: Dict[str, Any], inp: DetectorInput) -> DetectorOutput:
        """Calculates confidence, risk factors, generates GeoJSON, and packages result."""
        pass

    def run(self, inp: DetectorInput) -> DetectorOutput:
        """
        Executes full detection pipeline lifecycle.
        """
        valid, err = self.validate_input(inp)
        if not valid:
            return DetectorOutput(
                status="failed",
                event_id=f"{self.disaster_type}-err-{datetime.now(timezone.utc).strftime('%H%M%S')}",
                disaster_type=self.disaster_type,
                location_name=inp.location_name,
                latitude=inp.latitude,
                longitude=inp.longitude,
                confidence_score=0.0,
                severity="NONE",
                affected_area_km2=0.0,
                geometry_geojson={"type": "FeatureCollection", "features": []},
                satellite_info={},
                model_metadata={"model_name": self.model_version, "error": err},
                risk_breakdown={"composite_risk_score": 0.0, "risk_category": "LOW"},
                provenance={"data_provenance": "NO_LIVE_DATA"},
                error_message=err or "Invalid detection input parameters."
            )

        raw_data = self.acquire_data(inp)
        preprocessed = self.preprocess(raw_data)
        inference_res = self.infer(preprocessed)
        return self.postprocess(inference_res, inp)
