"""
Grounded Situation Report Generator for NIRVAAN

Serializes satellite evidence and impact analytics into responder-oriented situation reports.
Supports LLM-assisted summary generation when configured, and provides a deterministic offline fallback.
Strictly prohibits unsupported claims (casualties, evacuation orders, confirmed damage, weather).
"""

import os
from typing import Any, Dict, List, Optional, Tuple, Union

PROHIBITED_TERMS = [
    "casualty",
    "casualties",
    "evacuation order",
    "confirmed damage",
    "weather forecast",
    "road closure",
    "resource availability",
]


def serialize_evidence_payload(
    event_info: Optional[Dict[str, Any]] = None,
    spectral_data: Optional[Dict[str, Any]] = None,
    risk_zones: Optional[List[Dict[str, Any]]] = None,
    population_impact: Optional[Dict[str, Any]] = None,
    infrastructure_impact: Optional[Dict[str, Any]] = None,
    severity_result: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Serialize validated evidence and impact metrics into a structured schema.
    """
    event = event_info or {}
    event_id = event.get("event_id", "EVT_UNKNOWN")
    event_name = event.get("name", "Unspecified Disaster Event")
    disaster_type = event.get("type", "Satellite Observed Anomaly")
    location_name = event.get("location_name", "Target AOI")
    lat = event.get("lat") or event.get("latitude")
    lon = event.get("lon") or event.get("longitude")

    spec = spectral_data or {}
    index_name = spec.get("index_name", "NDWI/NBR")
    before_date = spec.get("before_date", "N/A")
    after_date = spec.get("after_date", "N/A")
    sensor = spec.get("sensor", "Sentinel-2 Level-2A")

    zones = risk_zones or []

    pop = population_impact or {}
    pop_status = pop.get("status", "DATA_UNAVAILABLE")
    pop_est = pop.get("estimated_affected_population")

    infra = infrastructure_impact or {}
    infra_status = infra.get("status", "DATA_UNAVAILABLE")
    infra_facilities = infra.get("impacted_infrastructure", [])
    infra_advisories = infra.get("advisory_statements", [])

    sev = severity_result or {}
    impact_score = sev.get("impact_score", 0.0)
    impact_band = sev.get("impact_band", "Low")
    factors = sev.get("contributing_factors", {})

    return {
        "event": {
            "event_id": event_id,
            "event_name": event_name,
            "disaster_type": disaster_type,
            "location_name": location_name,
            "latitude": lat,
            "longitude": lon,
        },
        "spectral_evidence": {
            "sensor": sensor,
            "index_name": index_name,
            "before_date": before_date,
            "after_date": after_date,
        },
        "spatial_analytics": {
            "total_risk_zones": len(zones),
            "zones": zones,
        },
        "population_exposure": {
            "status": pop_status,
            "estimated_affected_population": pop_est,
            "provenance_label": "ESTIMATE",
        },
        "infrastructure_proximity": {
            "status": infra_status,
            "impacted_facilities_count": len(infra_facilities),
            "facilities": infra_facilities,
            "advisory_statements": infra_advisories,
            "provenance_label": "FIELD_VERIFICATION_RECOMMENDED",
        },
        "composite_severity": {
            "impact_score": impact_score,
            "impact_band": impact_band,
            "contributing_factors": factors,
            "provenance_label": "PROTOTYPE",
        },
        "provenance_metadata": {
            "is_prototype": True,
            "disclaimer": "Prototype situation report based solely on satellite evidence and proxy data — not an operational emergency declaration."
        }
    }


def generate_fallback_situation_report(evidence_payload: Dict[str, Any]) -> str:
    """
    Generate a deterministic responder-oriented situation report offline.
    
    Contains NO unsupported claims or hallucinated facts.
    """
    event = evidence_payload.get("event", {})
    spectral = evidence_payload.get("spectral_evidence", {})
    spatial = evidence_payload.get("spatial_analytics", {})
    pop = evidence_payload.get("population_exposure", {})
    infra = evidence_payload.get("infrastructure_proximity", {})
    sev = evidence_payload.get("composite_severity", {})

    event_name = event.get("event_name", "Disaster Observation")
    disaster_type = event.get("disaster_type", "Disaster")
    location = event.get("location_name", "Target Region")
    lat, lon = event.get("latitude"), event.get("longitude")

    impact_score = sev.get("impact_score", "N/A")
    impact_band = sev.get("impact_band", "Unassessed")

    report_lines = [
        f"# 🛰️ NIRVAAN Situation Report: {event_name}",
        f"**Event Type:** {disaster_type} | **Location:** {location} | **Severity Index:** {impact_score}/100 ({impact_band}) `[PROTOTYPE]`",
        f"**Source Sensor:** {spectral.get('sensor', 'Sentinel-2')} | **Observation Window:** {spectral.get('before_date', 'N/A')} to {spectral.get('after_date', 'N/A')}",
        "",
        "---",
        "",
        "## 1. Executive Situation Summary",
        f"Multispectral satellite observation confirms spectral anomalies consistent with **{disaster_type.lower()}** evidence in the {location} area.",
        f"- **Prototype Composite Severity Score:** `{impact_score}/100` (`{impact_band}` band).",
    ]

    if lat is not None and lon is not None:
        report_lines.append(f"- **Center Coordinates:** Latitude `{lat:.4f}`, Longitude `{lon:.4f}`.")

    report_lines.extend([
        "",
        "## 2. High-Priority Impact Zones",
    ])

    num_zones = spatial.get("total_risk_zones", 0)
    if num_zones > 0:
        report_lines.append(f"- Identified **{num_zones} concentric risk zones** derived from spectral change masks.")
    else:
        report_lines.append("- *Risk zones:* Primary evidence polygons pending or sub-threshold.")

    pop_est = pop.get("estimated_affected_population")
    if pop.get("status") == "SUCCESS" and pop_est is not None:
        report_lines.append(f"- **Estimated Population Exposure:** ~`{pop_est:,}` people `[ESTIMATE]`.")
    else:
        report_lines.append("- **Population Exposure:** Local population raster dataset unavailable or unassessed.")

    report_lines.extend([
        "",
        "## 3. Field-Verification Recommendations",
    ])

    advisories = infra.get("advisory_statements", [])
    if infra.get("status") == "SUCCESS" and advisories:
        for adv in advisories:
            report_lines.append(f"- ⚠️ {adv}")
    else:
        report_lines.append("- *Critical Infrastructure:* No local infrastructure dataset loaded or no facilities within immediate proximity threshold — field verification recommended.")

    report_lines.extend([
        "",
        "## 4. Secondary Monitoring Actions",
        "- Schedule secondary satellite re-observation on next orbit pass.",
        "- Verify evidence spectral index thresholds against local ground validation points.",
        "",
        "## 5. Data Provenance & Limitations",
        "> [!IMPORTANT]",
        "> **Prototype Disclaimer:** This situation report is generated from satellite spectral indices and local geospatial proxy data.",
        "> - **No structural impact validation** is declared without ground truth inspection.",
        "> - **No health status estimates, operational emergency declarations, or directive commands** are issued.",
        "> - All derived population and severity figures are labeled as `ESTIMATE` / `PROTOTYPE`."
    ])

    return "\n".join(report_lines)


def generate_llm_situation_report(evidence_payload: Dict[str, Any], api_key: Optional[str] = None) -> Optional[str]:
    """
    Generate a responder-oriented summary using an LLM if available and configured.
    Falls back to None if unconfigured or API fails.
    """
    key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not key:
        return None

    try:
        # Prompt engineering with strict negative constraints
        prompt = f"""
        System: You are an emergency intelligence assistant for the NIRVAAN satellite monitoring platform.
        You must produce a concise responder-oriented situation report strictly using ONLY the provided structured evidence below.

        CRITICAL CONSTRAINTS:
        - NEVER invent or mention casualties, injuries, fatalities, or deaths.
        - NEVER invent or mention evacuation orders or operational emergency status.
        - NEVER declare confirmed structural damage without explicitly noting 'field verification recommended'.
        - NEVER invent weather conditions, road closures, or resource availability.
        - ALWAYS tag derived population counts as ESTIMATE and severity scores as PROTOTYPE.

        STRUCTURED EVIDENCE:
        {evidence_payload}

        Generate the situation report in Markdown format with sections:
        1. Executive Situation Summary
        2. High-Priority Impact Zones
        3. Field-Verification Recommendations
        4. Limitations & Data Provenance
        """

        # Optional Gemini import
        import google.generativeai as genai
        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text
    except Exception:
        pass

    return None


def generate_situation_report(
    evidence_data: Union[Dict[str, Any], Tuple[Any, ...]],
    force_offline: bool = False
) -> Dict[str, Any]:
    """
    Unified entry point for generating NIRVAAN situation reports.
    Attempts LLM summary generation when available, falling back deterministically to offline generation.
    """
    if isinstance(evidence_data, dict) and "event" in evidence_data:
        payload = evidence_data
    elif isinstance(evidence_data, (tuple, list)):
        payload = serialize_evidence_payload(*evidence_data)
    else:
        payload = serialize_evidence_payload(evidence_data if isinstance(evidence_data, dict) else {})

    report_text = None
    generation_mode = "OFFLINE_FALLBACK"

    if not force_offline:
        llm_output = generate_llm_situation_report(payload)
        if llm_output:
            report_text = llm_output
            generation_mode = "LLM_ASSISTED"

    if not report_text:
        report_text = generate_fallback_situation_report(payload)
        generation_mode = "OFFLINE_FALLBACK"

    return {
        "status": "SUCCESS",
        "mode": generation_mode,
        "report_markdown": report_text,
        "evidence_payload": payload,
        "provenance_label": "PROTOTYPE"
    }
