"""
Dataset Evidence & Provenance Tracking Module for NIRVAAN

Records, validates, and propagates source dataset lineage, acquisition dates,
spectral bands used, and processing thresholds across all detection, spatial analytics, and reporting outputs.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union


def create_provenance_record(
    dataset_id: str,
    source_url: str,
    before_date: str,
    after_date: str,
    bands_used: List[str],
    thresholds: Dict[str, float],
    sensor: str = "Sentinel-2 Level-2A",
    processing_timestamp: Optional[str] = None
) -> Dict[str, Any]:
    """
    Construct a standardized NIRVAAN dataset provenance record.
    """
    ts = processing_timestamp or datetime.now(timezone.utc).isoformat()
    return {
        "dataset_id": str(dataset_id),
        "source_url": str(source_url),
        "sensor": str(sensor),
        "acquisition_dates": {
            "before_date": str(before_date),
            "after_date": str(after_date),
        },
        "bands_used": [str(b) for b in bands_used],
        "spectral_thresholds": dict(thresholds or {}),
        "processing_timestamp": ts,
        "provenance_label": "VERIFIED_SOURCE_LINEAGE"
    }


def validate_provenance_completeness(provenance: Optional[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validate completeness of a provenance record.
    Returns (is_complete, list_of_errors).
    """
    errors = []
    if not isinstance(provenance, dict) or not provenance:
        return False, ["Provenance record is missing or empty."]

    required_keys = ["dataset_id", "source_url", "sensor", "acquisition_dates", "bands_used", "spectral_thresholds"]
    for req in required_keys:
        if req not in provenance:
            errors.append(f"Missing required provenance field: '{req}'.")

    dates = provenance.get("acquisition_dates", {})
    if isinstance(dates, dict):
        if not dates.get("before_date"):
            errors.append("Missing provenance before_date.")
        if not dates.get("after_date"):
            errors.append("Missing provenance after_date.")

    bands = provenance.get("bands_used", [])
    if not isinstance(bands, list) or len(bands) == 0:
        errors.append("Provenance bands_used must be a non-empty list.")

    return len(errors) == 0, errors


def attach_provenance(output_payload: Dict[str, Any], provenance_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Attach provenance lineage record into an output dictionary.
    """
    if isinstance(output_payload, dict):
        output_payload["provenance"] = dict(provenance_record or {})
    return output_payload
