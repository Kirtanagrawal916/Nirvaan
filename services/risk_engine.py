"""
NIRVAAN Explainable Risk Engine (services/risk_engine.py)

Calculates transparent, defensible composite risk scores (0–100) and classifications
based on hazard severity, spatial exposure, infrastructure vulnerability, model confidence,
and data freshness.

Formula:
Risk = min(100, (Hazard * 0.35 + PopulationExposure * 0.30 + InfrastructureExposure * 0.20 + EnvironmentalAnomaly * 0.15) * (Confidence / 100) * Freshness)
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging
import math
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger("nirvaan.risk_engine")


@dataclass
class RiskFactors:
    """Inputs to explainable risk evaluation."""
    disaster_type: str
    severity: str                           # 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL'
    confidence_score: float                 # 0.0 - 100.0
    affected_area_km2: float
    population_density: Optional[float] = None    # residents per km2, if available
    critical_infrastructure_count: Optional[int] = None
    environmental_anomaly_score: float = 20.0
    data_freshness_factor: float = 1.0


@dataclass
class RiskEvaluationResult:
    """Transparent, explainable risk score output."""
    composite_risk_score: float
    risk_category: str                      # 'LOW' | 'MODERATE' | 'ELEVATED' | 'HIGH' | 'CRITICAL'
    hazard_score: float
    population_exposure_score: float
    infrastructure_exposure_score: float
    environmental_anomaly_score: float
    confidence_adjustment: float
    data_freshness: float
    is_exposure_data_available: bool
    methodology_version: str = "Nirvaan-Risk-v1.0"
    evaluated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "composite_risk_score": round(self.composite_risk_score, 1),
            "risk_category": self.risk_category,
            "classification_note": "Nirvaan operational risk classification",
            "hazard_severity_score": round(self.hazard_score, 1),
            "population_exposure_score": round(self.population_exposure_score, 1) if self.is_exposure_data_available else "Exposure data unavailable",
            "infrastructure_exposure_score": round(self.infrastructure_exposure_score, 1) if self.is_exposure_data_available else "Exposure data unavailable",
            "environmental_anomaly_score": round(self.environmental_anomaly_score, 1),
            "confidence_adjustment": round(self.confidence_adjustment, 2),
            "data_freshness": round(self.data_freshness, 2),
            "methodology_version": self.methodology_version,
            "evaluated_at": self.evaluated_at
        }


class ExplainableRiskEngine:
    """
    Evaluates multi-hazard operational risk with full factor explainability.
    """

    SEVERITY_WEIGHTS = {
        "LOW": 25.0,
        "MODERATE": 50.0,
        "HIGH": 75.0,
        "CRITICAL": 95.0
    }

    @classmethod
    def classify_category(cls, score: float) -> str:
        if score >= 81.0:
            return "CRITICAL"
        if score >= 61.0:
            return "HIGH"
        if score >= 41.0:
            return "ELEVATED"
        if score >= 21.0:
            return "MODERATE"
        return "LOW"

    @classmethod
    def evaluate(cls, factors: RiskFactors) -> RiskEvaluationResult:
        """
        Executes explainable risk score calculation.
        """
        hazard_val = cls.SEVERITY_WEIGHTS.get(factors.severity.upper(), 40.0)

        # Spatial exposure calculations
        has_exposure = factors.population_density is not None or factors.affected_area_km2 > 0
        if factors.population_density is not None:
            # Scaled logarithmic exposure based on density and area
            est_pop = factors.population_density * factors.affected_area_km2
            pop_exposure = min(100.0, max(5.0, math.log10(max(10, est_pop)) * 20.0))
        elif factors.affected_area_km2 > 0:
            # Default density scaling based on hazard footprint
            pop_exposure = min(100.0, max(10.0, factors.affected_area_km2 * 5.0))
        else:
            pop_exposure = 10.0

        if factors.critical_infrastructure_count is not None:
            infra_exposure = min(100.0, factors.critical_infrastructure_count * 15.0)
        else:
            infra_exposure = min(100.0, max(10.0, factors.affected_area_km2 * 4.0))

        env_score = min(100.0, max(0.0, factors.environmental_anomaly_score))
        conf_adj = max(0.4, min(1.0, factors.confidence_score / 100.0))
        freshness = max(0.5, min(1.0, factors.data_freshness_factor))

        # Weighted multi-factor composite
        weighted_sum = (
            hazard_val * 0.35 +
            pop_exposure * 0.30 +
            infra_exposure * 0.20 +
            env_score * 0.15
        )

        composite_score = min(100.0, max(0.0, weighted_sum * conf_adj * freshness))
        category = cls.classify_category(composite_score)

        return RiskEvaluationResult(
            composite_risk_score=composite_score,
            risk_category=category,
            hazard_score=hazard_val,
            population_exposure_score=pop_exposure,
            infrastructure_exposure_score=infra_exposure,
            environmental_anomaly_score=env_score,
            confidence_adjustment=conf_adj,
            data_freshness=freshness,
            is_exposure_data_available=has_exposure
        )
