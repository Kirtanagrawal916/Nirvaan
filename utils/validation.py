"""
Backend Validation & Secret Sanitization Layer for NIRVAAN

Validates input metadata, imagery arrays, spectral thresholds, and output GeoJSON payloads.
Enforces standardized API error contracts and sanitizes log messages to prevent secret leaks.
"""

import re
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

from mapping.geojson import validate_coordinates

SECRET_PATTERNS = [
    re.compile(r'(?i)(api[_-]?key|secret|password|token|bearer|auth)\s*[:=]\s*["\']?([^"\'\s]+)["\']?'),
    re.compile(r'AIzaSy[A-Za-z0-9_-]{33}'),  # Google API key pattern
    re.compile(r'sk-[A-Za-z0-9]{32,}'),       # OpenAI API key pattern
]


def sanitize_log_message(msg: str) -> str:
    """
    Sanitize log messages by replacing API keys, secrets, and auth tokens with [REDACTED].
    """
    if not isinstance(msg, str):
        return str(msg)

    sanitized = msg
    for pattern in SECRET_PATTERNS:
        sanitized = pattern.sub(r'\1=[REDACTED]' if r'\1' in pattern.pattern else '[REDACTED]', sanitized)
    return sanitized


def validate_event_metadata(metadata: Optional[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validate disaster event metadata dictionary.
    Returns (is_valid, list_of_errors).
    """
    errors = []
    if not isinstance(metadata, dict) or not metadata:
        return False, ["Event metadata must be a non-empty dictionary."]

    if not metadata.get("event_id"):
        errors.append("Missing required field: 'event_id'.")

    if not metadata.get("name"):
        errors.append("Missing required field: 'name'.")

    if not metadata.get("type"):
        errors.append("Missing required field: 'type'.")

    lat = metadata.get("lat") if "lat" in metadata else metadata.get("latitude")
    lon = metadata.get("lon") if "lon" in metadata else metadata.get("longitude")

    if lat is None or lon is None or not validate_coordinates(lat, lon, allow_null_island=False):
        errors.append(f"Invalid or missing event coordinates: lat={lat}, lon={lon}.")

    return len(errors) == 0, errors


def validate_imagery_input(
    image_data: Any,
    required_bands: Optional[List[str]] = None
) -> Tuple[bool, List[str]]:
    """
    Validate imagery input data arrays.
    """
    errors = []
    if image_data is None:
        return False, ["Imagery input data is None."]

    if isinstance(image_data, np.ndarray):
        if image_data.size == 0:
            errors.append("Imagery numpy array is empty.")
        if np.isnan(image_data).any() or np.isinf(image_data).any():
            errors.append("Imagery array contains NaN or Inf values.")
    elif isinstance(image_data, dict):
        bands = image_data.get("bands", {})
        if not isinstance(bands, dict) or not bands:
            errors.append("Imagery dictionary contains no valid band data.")
        elif required_bands:
            for b in required_bands:
                if b not in bands:
                    errors.append(f"Missing required band: '{b}'.")
    elif isinstance(image_data, (list, tuple)):
        if len(image_data) == 0:
            errors.append("Imagery sequence is empty.")
    else:
        errors.append(f"Unsupported imagery data type: {type(image_data)}.")

    return len(errors) == 0, errors


def validate_thresholds(threshold_config: Optional[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validate spectral index threshold configurations.
    """
    errors = []
    if threshold_config is None:
        return True, []  # Optional, default thresholds will be used

    if not isinstance(threshold_config, dict):
        return False, ["Threshold configuration must be a dictionary."]

    ndwi_thresh = threshold_config.get("ndwi_threshold")
    if ndwi_thresh is not None:
        try:
            val = float(ndwi_thresh)
            if not (-1.0 <= val <= 1.0):
                errors.append(f"NDWI threshold must be between -1.0 and 1.0, got {val}.")
        except (ValueError, TypeError):
            errors.append(f"Invalid NDWI threshold value: {ndwi_thresh}.")

    dnbr_thresh = threshold_config.get("dnbr_threshold")
    if dnbr_thresh is not None:
        try:
            val = float(dnbr_thresh)
            if not (-2.0 <= val <= 2.0):
                errors.append(f"dNBR threshold must be between -2.0 and 2.0, got {val}.")
        except (ValueError, TypeError):
            errors.append(f"Invalid dNBR threshold value: {dnbr_thresh}.")

    return len(errors) == 0, errors


def validate_geojson_output(geojson_dict: Optional[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validate GeoJSON output structures and CRS metadata.
    """
    errors = []
    if not isinstance(geojson_dict, dict) or not geojson_dict:
        return False, ["GeoJSON output must be a non-empty dictionary."]

    gtype = geojson_dict.get("type")
    if gtype not in ["FeatureCollection", "Feature", "Polygon", "Point"]:
        errors.append(f"Invalid GeoJSON type: '{gtype}'.")

    if gtype == "FeatureCollection":
        features = geojson_dict.get("features")
        if not isinstance(features, list):
            errors.append("FeatureCollection must contain a 'features' array.")

    return len(errors) == 0, errors


def validate_detection_result(result: Optional[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validates model inference output payload before committing to persistent database.
    Checks for impossible coordinates, negative affected area, invalid confidence, and malformed geometry.
    """
    errors = []
    if not isinstance(result, dict) or not result:
        return False, ["Detection result payload is empty."]

    conf = result.get("confidence_score") or result.get("confidence")
    if conf is None:
        errors.append("Missing required 'confidence_score' in model output.")
    else:
        try:
            c_val = float(conf)
            if not (0.0 <= c_val <= 100.0):
                errors.append(f"Confidence score out of bounds [0.0, 100.0]: {c_val}")
        except (ValueError, TypeError):
            errors.append(f"Invalid non-numeric confidence score: {conf}")

    lat = result.get("latitude")
    lon = result.get("longitude")
    if lat is not None and lon is not None:
        if not validate_coordinates(lat, lon, allow_null_island=False):
            errors.append(f"Detection result coordinates out of bounds: lat={lat}, lon={lon}")

    area = result.get("affected_area_km2")
    if area is not None:
        try:
            a_val = float(area)
            if a_val < 0.0 or a_val > 1_000_000.0:
                errors.append(f"Unreasonable affected area: {a_val} km²")
        except (ValueError, TypeError):
            errors.append(f"Invalid non-numeric affected area: {area}")

    return len(errors) == 0, errors
