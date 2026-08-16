"""
NIRVAAN Reports Package
Provides grounded AI situation report generation, response recommendations, and deterministic offline report fallbacks.
"""

from reports.situation_report import (
    serialize_evidence_payload,
    generate_fallback_situation_report,
    generate_situation_report,
)
from reports.recommendations import (
    generate_response_recommendations,
)

__all__ = [
    "serialize_evidence_payload",
    "generate_fallback_situation_report",
    "generate_situation_report",
    "generate_response_recommendations",
]
