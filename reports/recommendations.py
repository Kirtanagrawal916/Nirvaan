"""
Responder Recommendations Module for NIRVAAN

Derives concise, prioritized responder recommendations from composite severity scores,
population exposure estimates, and infrastructure proximity metrics.
Strictly prohibits unsupported operational directives (no evacuation orders, no confirmed damage, no mandatory resource dispatch).
"""

from typing import Any, Dict, List, Optional, Tuple, Union

PROHIBITED_OPERATIONAL_TERMS = [
    "evacuation order",
    "evacuate immediately",
    "confirmed damage",
    "structural collapse",
    "mandatory dispatch",
    "resource deployment",
    "casualty count",
]


def generate_response_recommendations(
    severity_result: Optional[Dict[str, Any]] = None,
    population_impact: Optional[Dict[str, Any]] = None,
    infrastructure_impact: Optional[Dict[str, Any]] = None,
    risk_zones: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Derive structured, prioritized responder recommendations from analytical evidence.
    
    Priority Tiers:
    - P0_CRITICAL_VERIFICATION: High severity areas, nearby critical healthcare/access infrastructure.
    - P1_HIGH_ADVISORY: Significant population exposure or Moderate risk zone expansion.
    - P2_MONITORING: Satellite re-observation & baseline ground calibration.
    """
    sev = severity_result or {}
    impact_score = sev.get("impact_score", 0.0)
    impact_band = sev.get("impact_band", "Low")

    pop = population_impact or {}
    pop_est = pop.get("estimated_affected_population")

    infra = infrastructure_impact or {}
    infra_facilities = infra.get("impacted_infrastructure", [])
    infra_advisories = infra.get("advisory_statements", [])

    zones = risk_zones or []

    recommendations = []
    formatted_suggestions = []

    # 1. P0 Critical Verification Items
    if impact_band in ["High", "Extreme"] or (isinstance(impact_score, (int, float)) and impact_score >= 50.0):
        text = f"Prioritize ground verification in core affected zone (Severity Index: {impact_score}/100 - {impact_band} band) — field verification recommended."
        recommendations.append({
            "priority": "P0_CRITICAL_VERIFICATION",
            "category": "spatial_verification",
            "suggestion": text,
            "provenance_label": "PROTOTYPE"
        })
        formatted_suggestions.append(f"[P0] {text}")

    # Check high-criticality infrastructure (hospitals, bridges) within 1.5 km
    critical_infra = [f for f in infra_facilities if f.get("category") in ["hospital", "bridge", "power"] and f.get("distance_km", 99.0) <= 1.5]
    if critical_infra:
        for fac in critical_infra:
            fname = fac.get("name", "Critical Facility")
            fcat = str(fac.get("category", "facility")).capitalize()
            fdist = fac.get("distance_km", 0.0)
            text = f"Conduct physical accessibility inspection at {fcat} ('{fname}', {fdist:.1f} km from hotspot) — field verification recommended."
            recommendations.append({
                "priority": "P0_CRITICAL_VERIFICATION",
                "category": "infrastructure_inspection",
                "suggestion": text,
                "provenance_label": "PROTOTYPE"
            })
            formatted_suggestions.append(f"[P0] {text}")

    # 2. P1 High Advisory Items
    if pop_est is not None and pop_est > 0:
        text = f"Cross-examine estimated population exposure (~{pop_est:,} people `[ESTIMATE]`) against local district census records."
        recommendations.append({
            "priority": "P1_HIGH_ADVISORY",
            "category": "population_exposure",
            "suggestion": text,
            "provenance_label": "PROTOTYPE"
        })
        formatted_suggestions.append(f"[P1] {text}")

    if len(zones) > 1:
        text = f"Monitor buffer expansion across {len(zones)} concentric risk zones for perimeter boundary movement."
        recommendations.append({
            "priority": "P1_HIGH_ADVISORY",
            "category": "zone_monitoring",
            "suggestion": text,
            "provenance_label": "PROTOTYPE"
        })
        formatted_suggestions.append(f"[P1] {text}")

    # 3. P2 Monitoring Items (Baseline fallback recommendations)
    text_p2_sat = "Schedule secondary multispectral satellite re-observation on next orbit pass."
    recommendations.append({
        "priority": "P2_MONITORING",
        "category": "satellite_reobservation",
        "suggestion": text_p2_sat,
        "provenance_label": "PROTOTYPE"
    })
    formatted_suggestions.append(f"[P2] {text_p2_sat}")

    text_p2_cal = "Verify evidence spectral index change thresholds against local GPS calibration points."
    recommendations.append({
        "priority": "P2_MONITORING",
        "category": "calibration",
        "suggestion": text_p2_cal,
        "provenance_label": "PROTOTYPE"
    })
    formatted_suggestions.append(f"[P2] {text_p2_cal}")

    return {
        "status": "PROTOTYPE",
        "recommendations_count": len(recommendations),
        "recommendations": recommendations,
        "formatted_suggestions": formatted_suggestions,
        "provenance_label": "PROTOTYPE",
        "is_prototype": True,
        "disclaimer": "Prototype responder recommendations — analytical advisories only. Field verification required before operational deployment."
    }
