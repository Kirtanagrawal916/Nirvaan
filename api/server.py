"""
REST/JSON API Service Endpoint Router & Handlers for NIRVAAN

Exposes validated detection, spatial analytics, severity scoring, and reporting endpoints.
Enforces schema validation, secret sanitization, and safe error responses.
"""

from datetime import datetime, timezone
import json
from typing import Any, Dict, List, Optional, Tuple, Union

from utils.validation import (
    sanitize_log_message,
    validate_event_metadata,
    validate_thresholds,
    validate_geojson_output,
)
from utils.provenance import (
    create_provenance_record,
    attach_provenance,
)
from detection.mask import mask_to_polygons
from analysis.confidence import calculate_evidence_confidence
from analysis.risk_zones import generate_risk_zones, to_geojson_risk_zones
from analysis.population import estimate_affected_population
from analysis.infrastructure import analyze_infrastructure_impact
from analysis.severity import calculate_composite_impact_score
from reports.situation_report import generate_situation_report


def _create_json_response(status_code: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format standard API JSON response wrapper.
    """
    return {
        "status_code": status_code,
        "content_type": "application/json",
        "data": data
    }


def handle_health_check() -> Dict[str, Any]:
    """GET /api/v1/health endpoint handler."""
    return _create_json_response(200, {
        "status": "HEALTHY",
        "service": "NIRVAAN Satellite Disaster Monitoring API",
        "version": "1.0.0-prototype",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model_provenance": {
            "spectral_indices": ["NDWI", "dNBR"],
            "locked_stack": "Folium + Streamlit + Python Geospatial",
            "provenance_label": "VERIFIED"
        }
    })


def handle_detect_endpoint(payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """POST /api/v1/detect endpoint handler."""
    if not isinstance(payload, dict):
        return _create_json_response(400, {
            "error": "BAD_REQUEST",
            "message": sanitize_log_message("Payload must be a valid JSON object.")
        })

    # Validate event metadata
    event_info = payload.get("event", {})
    is_valid_meta, meta_errors = validate_event_metadata(event_info)
    if not is_valid_meta:
        return _create_json_response(422, {
            "error": "UNPROCESSABLE_ENTITY",
            "message": "Invalid event metadata.",
            "details": [sanitize_log_message(e) for e in meta_errors]
        })

    # Validate threshold configuration
    thresholds = payload.get("thresholds", {})
    is_valid_thresh, thresh_errors = validate_thresholds(thresholds)
    if not is_valid_thresh:
        return _create_json_response(422, {
            "error": "UNPROCESSABLE_ENTITY",
            "message": "Invalid threshold configuration.",
            "details": [sanitize_log_message(e) for e in thresh_errors]
        })

    # Extract mask/polygon detection data
    mask_grid = payload.get("mask")
    transform = payload.get("transform", {
        "origin_lat": event_info.get("lat", 26.0),
        "origin_lon": event_info.get("lon", 92.0),
        "pixel_size_lat": -0.001,
        "pixel_size_lon": 0.001
    })

    if mask_grid is not None:
        detected_polygons = mask_to_polygons(
            mask_grid,
            transform=transform,
            min_pixels=payload.get("min_pixels", 5),
            properties={"event_id": event_info.get("event_id"), "disaster_type": event_info.get("type")}
        )
        confidence_result = calculate_evidence_confidence(mask_grid)
    else:
        # Default empty detection fallback
        detected_polygons = []
        confidence_result = calculate_evidence_confidence(None)

    # Construct Provenance Record
    prov_record = create_provenance_record(
        dataset_id=payload.get("dataset_id", "CANONICAL_SENTINEL2_001"),
        source_url=payload.get("source_url", "https://scihub.copernicus.eu/s2"),
        before_date=payload.get("before_date", "2024-05-10"),
        after_date=payload.get("after_date", "2024-05-20"),
        bands_used=payload.get("bands_used", ["B03", "B08", "B12"]),
        thresholds=thresholds or {"ndwi": 0.3, "dnbr": 0.2}
    )

    response_data = {
        "status": "SUCCESS",
        "event_id": event_info.get("event_id"),
        "detection_polygons_count": len(detected_polygons),
        "geojson": {
            "type": "FeatureCollection",
            "features": detected_polygons
        },
        "confidence": confidence_result,
        "provenance": prov_record
    }

    return _create_json_response(200, response_data)


def handle_analyze_endpoint(payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """POST /api/v1/analyze endpoint handler."""
    if not isinstance(payload, dict):
        return _create_json_response(400, {
            "error": "BAD_REQUEST",
            "message": sanitize_log_message("Payload must be a valid JSON object.")
        })

    polygons = payload.get("polygons", [])
    pop_data = payload.get("population_data")
    infra_data = payload.get("infrastructure_data")
    hotspots = payload.get("hotspots", [])
    spectral_sev = payload.get("spectral_severity", "High")

    # Generate spatial risk zones
    risk_zones = generate_risk_zones(polygons)

    # Estimate population impact
    pop_impact = estimate_affected_population(risk_zones if risk_zones else polygons, population_data=pop_data)

    # Analyze infrastructure proximity
    infra_impact = analyze_infrastructure_impact(
        polygons_or_hotspots=hotspots if hotspots else polygons,
        infrastructure_data=infra_data
    )

    # Calculate composite impact score
    severity_result = calculate_composite_impact_score(
        spectral_severity=spectral_sev,
        population_estimate=pop_impact.get("estimated_affected_population"),
        infrastructure_impact=infra_impact,
        hotspots=hotspots
    )

    response_data = {
        "status": "SUCCESS",
        "risk_zones_geojson": to_geojson_risk_zones(risk_zones),
        "population_exposure": pop_impact,
        "infrastructure_proximity": infra_impact,
        "composite_severity": severity_result,
        "provenance_label": "PROTOTYPE"
    }

    return _create_json_response(200, response_data)


def handle_report_endpoint(payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """POST /api/v1/report endpoint handler."""
    if not isinstance(payload, dict):
        return _create_json_response(400, {
            "error": "BAD_REQUEST",
            "message": sanitize_log_message("Payload must be a valid JSON object.")
        })

    force_offline = payload.get("force_offline", True)
    report_result = generate_situation_report(payload, force_offline=force_offline)

    return _create_json_response(200, report_result)


def handle_api_request(endpoint: str, method: str = "POST", payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Main API Request Dispatcher.
    Applies endpoint routing, validation, sanitization, and exception safety.
    """
    clean_endpoint = str(endpoint).strip().rstrip("/")
    clean_method = str(method).strip().upper()

    try:
        if clean_endpoint == "/api/v1/health" and clean_method == "GET":
            return handle_health_check()
        elif clean_endpoint == "/api/v1/detect" and clean_method == "POST":
            return handle_detect_endpoint(payload)
        elif clean_endpoint == "/api/v1/analyze" and clean_method == "POST":
            return handle_analyze_endpoint(payload)
        elif clean_endpoint == "/api/v1/report" and clean_method == "POST":
            return handle_report_endpoint(payload)
        else:
            return _create_json_response(404, {
                "error": "NOT_FOUND",
                "message": f"Endpoint '{clean_endpoint}' [{clean_method}] not found."
            })
    except Exception as exc:
        safe_msg = sanitize_log_message(str(exc))
        return _create_json_response(500, {
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred during API processing.",
            "details": safe_msg
        })
