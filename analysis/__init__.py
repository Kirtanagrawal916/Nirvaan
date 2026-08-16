"""
NIRVAAN Analysis Package
Provides risk-zone generation, affected area calculations, population impact estimation, and severity algorithms.
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

__all__ = [
    "buffer_polygon_vertices",
    "generate_risk_zones",
    "to_geojson_risk_zones",
    "create_synthetic_population_grid",
    "estimate_affected_population",
]
