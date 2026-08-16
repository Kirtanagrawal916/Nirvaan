"""
Unit tests for NIRVAAN Situation Assessment Schema (analysis/situation_assessment.py - TASK-021)
"""

import json
import unittest

from analysis.situation_assessment import (
    SituationAssessment,
    build_situation_assessment,
)
from detection.mode_controller import execute_mode_analysis


class TestSituationAssessment(unittest.TestCase):
    """Test suite for SituationAssessment schema validation, JSON serialization, and canonical contract building."""

    def test_build_situation_assessment_flood(self):
        """Verify building situation assessment from canonical flood contract."""
        contract = execute_mode_analysis("flood-emilia-romagna-2023", mode="INSTANT_DEMO")
        assessment = build_situation_assessment(contract)

        self.assertIsInstance(assessment, SituationAssessment)
        self.assertEqual(assessment.event_id, "flood-emilia-romagna-2023")
        self.assertEqual(assessment.disaster_type, "flood")
        self.assertEqual(assessment.severity_level, contract.severity["severity_level"])
        self.assertTrue(assessment.is_estimate)
        self.assertGreater(len(assessment.recommended_verification_actions), 0)

        # Verify JSON serialization
        d = assessment.to_dict()
        self.assertIn("affected_area_km2", d)

        json_str = assessment.to_json()
        parsed = json.loads(json_str)
        reconstructed = SituationAssessment.from_dict(parsed)
        self.assertEqual(reconstructed.event_id, "flood-emilia-romagna-2023")

    def test_build_situation_assessment_wildfire(self):
        """Verify building situation assessment from canonical wildfire contract."""
        contract = execute_mode_analysis("wildfire-rhodes-2023", mode="INSTANT_DEMO")
        assessment = build_situation_assessment(contract)

        self.assertIsInstance(assessment, SituationAssessment)
        self.assertEqual(assessment.event_id, "wildfire-rhodes-2023")
        self.assertEqual(assessment.disaster_type, "wildfire")
        self.assertEqual(assessment.severity_level, contract.severity["severity_level"])
        self.assertTrue(assessment.is_estimate)
        self.assertGreater(len(assessment.recommended_verification_actions), 0)

    def test_invalid_disaster_type_raises_value_error(self):
        """Verify invalid disaster type raises ValueError."""
        with self.assertRaises(ValueError):
            SituationAssessment(
                event_id="test-bad-disaster",
                disaster_type="hurricane_unsupported",
                evidence_confidence=0.8,
                severity_level="LOW",
                severity_score=10.0,
                affected_area_km2=1.0,
                affected_area_hectares=100.0,
                hotspot_count=0,
                top_hotspots=[],
                infrastructure_summary=[],
                evidence_source="Test",
                limitations=[],
                recommended_verification_actions=[],
            )

    def test_invalid_confidence_raises_value_error(self):
        """Verify confidence out of 0.0-1.0 range raises ValueError."""
        with self.assertRaises(ValueError):
            SituationAssessment(
                event_id="test-bad-conf",
                disaster_type="flood",
                evidence_confidence=1.5,  # Out of range
                severity_level="LOW",
                severity_score=10.0,
                affected_area_km2=1.0,
                affected_area_hectares=100.0,
                hotspot_count=0,
                top_hotspots=[],
                infrastructure_summary=[],
                evidence_source="Test",
                limitations=[],
                recommended_verification_actions=[],
            )

    def test_negative_affected_area_raises_value_error(self):
        """Verify negative affected area raises ValueError."""
        with self.assertRaises(ValueError):
            SituationAssessment(
                event_id="test-neg-area",
                disaster_type="flood",
                evidence_confidence=0.8,
                severity_level="LOW",
                severity_score=10.0,
                affected_area_km2=-5.0,  # Invalid negative area
                affected_area_hectares=-500.0,
                hotspot_count=0,
                top_hotspots=[],
                infrastructure_summary=[],
                evidence_source="Test",
                limitations=[],
                recommended_verification_actions=[],
            )


if __name__ == "__main__":
    unittest.main()
