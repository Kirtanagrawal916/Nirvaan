"""
NIRVAAN Analysis Package
Provides risk-zone generation, affected area calculations, population impact estimation,
severity scoring, and infrastructure impact analysis.
"""

from analysis.risk_zones import (
    buffer_polygon_vertices,
    generate_risk_zones,
    to_geojson_risk_zones,
)
from analysis.population import (
    create_synthetic_population_grid,
    estimate_affected_population,
)
from analysis.infrastructure import (
    haversine_distance,
    create_synthetic_infrastructure_layer,
    analyze_infrastructure_impact,
)
from analysis.severity import calculate_composite_impact_score

__all__ = [
    "buffer_polygon_vertices",
    "generate_risk_zones",
    "to_geojson_risk_zones",
    "create_synthetic_population_grid",
    "estimate_affected_population",
    "haversine_distance",
    "create_synthetic_infrastructure_layer",
    "analyze_infrastructure_impact",
    "calculate_composite_impact_score",
]
