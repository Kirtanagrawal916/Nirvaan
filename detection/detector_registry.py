"""
NIRVAAN Disaster Detector Registry (detection/detector_registry.py)

Maintains pluggable registrations for all supported disaster detectors.
Exposes metadata on supported disaster types, models, update cadences, and limitations.
"""

import logging
from typing import Any, Dict, List, Optional, Type

from detection.detector_base import BaseDisasterDetector
from detection.detectors import ModularFloodDetector, ModularWildfireDetector, SevereWeatherDetector
from db.repository import DatabaseRepository

logger = logging.getLogger("nirvaan.detector_registry")


class DetectorRegistry:
    """
    Central registry for multi-disaster detector implementations.
    """

    _detectors: Dict[str, Type[BaseDisasterDetector]] = {
        "flood": ModularFloodDetector,
        "wildfire": ModularWildfireDetector,
        "severe_weather": SevereWeatherDetector,
        "cyclone": SevereWeatherDetector,
    }

    _metadata: Dict[str, Dict[str, Any]] = {
        "flood": {
            "disaster_type": "flood",
            "display_name": "Inundation & Riverine Flood",
            "description": "Normalized Difference Water Index (NDWI) thresholding on Sentinel-2 Level-2A surface reflectance coupled with hydrological river discharge telemetry.",
            "supported_data_sources": ["Copernicus Sentinel-2 L2A (B03 Green, B08 NIR)", "Open-Meteo Flood Discharge API"],
            "detection_method": "Multi-spectral NDWI difference segmentation",
            "severity_methodology": "Spatial surface area expansion (>20 km² High, >50 km² Critical) and river discharge volume",
            "confidence_interpretation": "Calculated from sensor radiometric fidelity, cloud cover attenuation, and gauge correlation",
            "update_frequency": "12–24h satellite revisit cadence",
            "limitations": "Heavy persistent cloud cover requires SAR radar fusion for optical penetration.",
            "operational_status": "PRODUCTION_VERIFIED"
        },
        "wildfire": {
            "disaster_type": "wildfire",
            "display_name": "Wildfire & Thermal Anomaly",
            "description": "Normalized Burn Ratio (NBR) using Sentinel-2 NIR (B08) and Short-Wave Infrared (B12) paired with active thermal hotspots.",
            "supported_data_sources": ["Copernicus Sentinel-2 L2A (B08 NIR, B12 SWIR-2)", "Open Thermal Anomaly Radiance"],
            "detection_method": "NBR / dNBR Burn Severity Index",
            "severity_methodology": "Burn scar surface magnitude (>10 km² High) and infrared radiance intensity",
            "confidence_interpretation": "Derived from SWIR-2 spectral contrast and cloud occlusion penalties",
            "update_frequency": "Daily orbital passes",
            "limitations": "Heavy smoke plumes may attenuate optical bands; verified with SWIR band penetration.",
            "operational_status": "PRODUCTION_VERIFIED"
        },
        "severe_weather": {
            "disaster_type": "severe_weather",
            "display_name": "Severe Weather & Storm Surge",
            "description": "Authoritative numerical weather prediction assimilation tracking severe barometric drops, gale-force wind fields, and storm surges.",
            "supported_data_sources": ["ECMWF / Open-Meteo Severe Weather Global Model", "Geostationary Meteorological Satellites"],
            "detection_method": "Authoritative multi-model meteorological assimilation",
            "severity_methodology": "Sustained wind velocities (>75 km/h High, >100 km/h Critical) and central barometric pressure (<985 hPa High)",
            "confidence_interpretation": "Numerical weather prediction ensemble confidence",
            "update_frequency": "3–6h forecast cycle update",
            "limitations": "Source attribution is external authoritative meteorological data, not internal Nirvaan optical ML.",
            "operational_status": "PRODUCTION_VERIFIED"
        }
    }

    @classmethod
    def register(cls, disaster_type: str, detector_cls: Type[BaseDisasterDetector], metadata: Optional[Dict[str, Any]] = None) -> None:
        """Registers a new disaster detector class."""
        norm_type = disaster_type.lower().strip()
        cls._detectors[norm_type] = detector_cls
        if metadata:
            cls._metadata[norm_type] = metadata
        logger.info("Registered disaster detector for type '%s'", norm_type)

    @classmethod
    def get_detector(cls, disaster_type: str, repo: Optional[DatabaseRepository] = None) -> BaseDisasterDetector:
        """Instantiates and returns the detector for the requested disaster type."""
        norm_type = disaster_type.lower().strip()
        detector_cls = cls._detectors.get(norm_type)
        if not detector_cls:
            raise ValueError(f"Unsupported disaster type '{disaster_type}'. Supported types: {list(cls._detectors.keys())}")
        return detector_cls(repo=repo)

    @classmethod
    def is_supported(cls, disaster_type: str) -> bool:
        """Checks if a disaster type is supported."""
        return disaster_type.lower().strip() in cls._detectors

    @classmethod
    def list_supported_types(cls) -> List[Dict[str, Any]]:
        """Returns metadata for all supported disaster types."""
        return list(cls._metadata.values())
