"""
NIRVAAN Reports Package
Provides grounded AI situation report generation and deterministic offline report fallbacks.
"""

from reports.situation_report import (
    serialize_evidence_payload,
    generate_fallback_situation_report,
    generate_situation_report,
)

__all__ = [
    "serialize_evidence_payload",
    "generate_fallback_situation_report",
    "generate_situation_report",
]
