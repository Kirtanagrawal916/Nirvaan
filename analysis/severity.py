"""
Prototype Severity & Composite Impact Scoring Engine for NIRVAAN

Calculates a deterministic composite impact score (0–100) and severity band classification
combining spectral evidence, affected population estimates, critical infrastructure proximity, and hotspots.
Labels all outputs as PROTOTYPE with transparent contributing factors.
"""

import math
from typing import Any, Dict, List, Optional, Tuple, Union

DEFAULT_WEIGHTS = {
    "spectral": 0.30,
    "population": 0.30,
    "infrastructure": 0.25,
    "hotspots": 0.15,
}

DEFAULT_THRESHOLDS = {
    "Low": (0.0, 25.0),
    "Moderate": (25.0, 50.0),
    "High": (50.0, 75.0),
    "Extreme": (75.0, 100.0),
}


def _compute_spectral_subscore(spectral_input: Any) -> Tuple[float, str]:
    """Compute 0-100 spectral subscore from severity string or numerical index."""
    if spectral_input is None:
        return 0.0, "None"

    if isinstance(spectral_input, (int, float)):
        val = float(spectral_input)
        return min(max(val, 0.0), 100.0), f"{val:.1f}"

    clean = str(spectral_input).strip().lower()
    mapping = {
        "extreme": 100.0,
        "high": 75.0,
        "moderate": 50.0,
        "medium": 50.0,
        "low": 25.0,
    }
    score = mapping.get(clean, 0.0)
    return score, str(spectral_input)


def _compute_population_subscore(pop_input: Any) -> Tuple[float, str]:
    """Compute 0-100 population subscore log-scaled up to 10,000 people."""
    if pop_input is None:
        return 0.0, "Unavailable"

    pop_val = 0.0
    if isinstance(pop_input, (int, float)):
        pop_val = float(pop_input)
    elif isinstance(pop_input, dict):
        est = pop_input.get("estimated_affected_population")
        if est is not None and isinstance(est, (int, float)):
            pop_val = float(est)
        else:
            return 0.0, "Unavailable"

    if pop_val <= 0:
        return 0.0, "0 people"

    # Logarithmic scaling: 10 people -> ~25%, 100 people -> ~50%, 1000 people -> ~75%, 10000+ -> 100%
    log_pop = math.log10(max(pop_val, 1.0))
    score = min((log_pop / 4.0) * 100.0, 100.0)
    return round(score, 1), f"{int(pop_val):,} people"


def _compute_infrastructure_subscore(infra_input: Any) -> Tuple[float, str]:
    """Compute 0-100 infrastructure proximity subscore."""
    if infra_input is None:
        return 0.0, "Unavailable"

    facilities = []
    if isinstance(infra_input, dict):
        facilities = infra_input.get("impacted_infrastructure", [])
    elif isinstance(infra_input, list):
        facilities = infra_input

    if not facilities:
        return 0.0, "0 facilities nearby"

    score = 0.0
    for fac in facilities:
        if isinstance(fac, dict):
            dist_km = fac.get("distance_km", 5.0)
            cat = str(fac.get("category", "")).lower()
            
            # Higher score for closer distance and high-criticality categories
            cat_weight = 1.5 if cat in ["hospital", "bridge", "power"] else 1.0
            dist_factor = max(1.0 - (dist_km / 5.0), 0.1)
            score += 25.0 * dist_factor * cat_weight

    score = min(score, 100.0)
    return round(score, 1), f"{len(facilities)} facilities within threshold"


def _compute_hotspot_subscore(hotspots_input: Any) -> Tuple[float, str]:
    """Compute 0-100 hotspot concentration subscore."""
    if hotspots_input is None:
        return 0.0, "0 hotspots"

    count = 0
    if isinstance(hotspots_input, (int, float)):
        count = int(hotspots_input)
    elif isinstance(hotspots_input, list):
        count = len(hotspots_input)
    elif isinstance(hotspots_input, dict):
        count = len(hotspots_input.get("features", []))

    if count <= 0:
        return 0.0, "0 hotspots"

    # 1 hotspot -> 20, 5 hotspots -> 60, 10+ hotspots -> 100
    score = min(count * 10.0 + 10.0, 100.0)
    return round(score, 1), f"{count} hotspots"


def calculate_composite_impact_score(
    spectral_severity: Optional[Any] = None,
    population_estimate: Optional[Any] = None,
    infrastructure_impact: Optional[Any] = None,
    hotspots: Optional[Any] = None,
    weights: Optional[Dict[str, float]] = None,
    thresholds: Optional[Dict[str, Tuple[float, float]]] = None
) -> Dict[str, Any]:
    """
    Calculate deterministic composite impact_score (0-100) and impact_band.
    
    Exposes transparent contributing factors breakdown.
    Labels output as PROTOTYPE.
    """
    w = weights or DEFAULT_WEIGHTS

    # Ensure weights sum to 1.0
    w_spectral = w.get("spectral", 0.30)
    w_population = w.get("population", 0.30)
    w_infrastructure = w.get("infrastructure", 0.25)
    w_hotspots = w.get("hotspots", 0.15)
    total_w = w_spectral + w_population + w_infrastructure + w_hotspots

    if total_w > 0:
        w_spectral /= total_w
        w_population /= total_w
        w_infrastructure /= total_w
        w_hotspots /= total_w

    # Sub-scores
    score_spec, raw_spec = _compute_spectral_subscore(spectral_severity)
    score_pop, raw_pop = _compute_population_subscore(population_estimate)
    score_infra, raw_infra = _compute_infrastructure_subscore(infrastructure_impact)
    score_hot, raw_hot = _compute_hotspot_subscore(hotspots)

    # Weighted Composite Score
    composite_score = (
        score_spec * w_spectral +
        score_pop * w_population +
        score_infra * w_infrastructure +
        score_hot * w_hotspots
    )
    composite_score = round(min(max(composite_score, 0.0), 100.0), 1)

    # Categorize into impact_band
    if composite_score >= 75.0:
        impact_band = "Extreme"
    elif composite_score >= 50.0:
        impact_band = "High"
    elif composite_score >= 25.0:
        impact_band = "Moderate"
    else:
        impact_band = "Low"

    contributing_factors = {
        "spectral_evidence": {
            "subscore": score_spec,
            "weight": round(w_spectral, 2),
            "points_contributed": round(score_spec * w_spectral, 1),
            "input_summary": raw_spec
        },
        "population_exposure": {
            "subscore": score_pop,
            "weight": round(w_population, 2),
            "points_contributed": round(score_pop * w_population, 1),
            "input_summary": raw_pop
        },
        "infrastructure_proximity": {
            "subscore": score_infra,
            "weight": round(w_infrastructure, 2),
            "points_contributed": round(score_infra * w_infrastructure, 1),
            "input_summary": raw_infra
        },
        "hotspot_concentration": {
            "subscore": score_hot,
            "weight": round(w_hotspots, 2),
            "points_contributed": round(score_hot * w_hotspots, 1),
            "input_summary": raw_hot
        }
    }

    return {
        "status": "PROTOTYPE",
        "impact_score": composite_score,
        "impact_band": impact_band,
        "severity_band": impact_band,
        "contributing_factors": contributing_factors,
        "provenance_label": "PROTOTYPE",
        "is_prototype": True,
        "disclaimer": "Prototype composite score — not an operational emergency standard. Field verification recommended."
    }


# Re-export detection severity layer symbols for package compatibility
try:
    from detection.severity import SeverityClassifier, SeverityResult, classify_severity
except ImportError:
    pass

