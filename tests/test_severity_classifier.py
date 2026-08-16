"""
Unit tests for NIRVAAN Severity Classifier (detection/severity.py - TASK-013)
"""

import unittest

from analysis.affected_area import AffectedAreaResult, calculate_affected_area
from detection.severity import SeverityClassifier, SeverityResult, classify_severity


class TestSeverityClassifier(unittest.TestCase):
    """Test suite for SeverityClassifier flood & wildfire logic, score calculation, and boundaries."""

    def setUp(self):
        self.classifier = SeverityClassifier()

    def test_flood_severity_low_case(self):
        """Verify ratio < 20% classifies as LOW."""
        area = AffectedAreaResult(
            event_id="test-flood-low",
            disaster_type="flood",
            affected_pixel_count=10,
            pixel_area_m2=100.0,
            affected_area_m2=1000.0,
            affected_area_hectares=0.1,
            affected_area_km2=0.001,
            CRS="EPSG:32632",
            resolution_m=10.0,
            method="PROJECTED_UTM_SQUARE_PIXEL",
        )

        res = self.classifier.classify_flood_severity(area, affected_ratio=0.10)
        self.assertEqual(res.severity_level, "LOW")
        self.assertLess(res.severity_score, 20.0)

    def test_flood_severity_moderate_case(self):
        """Verify ratio 20%-50% classifies as MODERATE."""
        area = AffectedAreaResult(
            event_id="test-flood-mod",
            disaster_type="flood",
            affected_pixel_count=30,
            pixel_area_m2=100.0,
            affected_area_m2=3000.0,
            affected_area_hectares=0.3,
            affected_area_km2=0.003,
            CRS="EPSG:32632",
            resolution_m=10.0,
            method="PROJECTED_UTM_SQUARE_PIXEL",
        )

        res = self.classifier.classify_flood_severity(area, affected_ratio=0.30)
        self.assertEqual(res.severity_level, "MODERATE")
        self.assertGreaterEqual(res.severity_score, 20.0)
        self.assertLess(res.severity_score, 60.0)

    def test_flood_severity_high_and_critical_boundaries(self):
        """Verify boundary behavior for HIGH (50-75%) and CRITICAL (>= 75%)."""
        area = AffectedAreaResult(
            event_id="test-flood-boundary",
            disaster_type="flood",
            affected_pixel_count=80,
            pixel_area_m2=100.0,
            affected_area_m2=8000.0,
            affected_area_hectares=0.8,
            affected_area_km2=0.008,
            CRS="EPSG:32632",
            resolution_m=10.0,
            method="PROJECTED_UTM_SQUARE_PIXEL",
        )

        res_high = self.classifier.classify_flood_severity(area, affected_ratio=0.60)
        self.assertEqual(res_high.severity_level, "HIGH")

        res_crit = self.classifier.classify_flood_severity(area, affected_ratio=0.80)
        self.assertEqual(res_crit.severity_level, "CRITICAL")

    def test_wildfire_severity_breakdown(self):
        """Verify wildfire dNBR breakdown classification."""
        area = AffectedAreaResult(
            event_id="test-wildfire-severe",
            disaster_type="wildfire",
            affected_pixel_count=100,
            pixel_area_m2=100.0,
            affected_area_m2=10000.0,
            affected_area_hectares=1.0,
            affected_area_km2=0.01,
            CRS="EPSG:32635",
            resolution_m=10.0,
            method="PROJECTED_UTM_SQUARE_PIXEL",
        )

        breakdown_high = {"low_severity": 10, "moderate_severity": 20, "high_severity": 70}
        res = self.classifier.classify_wildfire_severity(area, severity_breakdown=breakdown_high)

        self.assertIn(res.severity_level, {"HIGH", "CRITICAL"})
        self.assertGreater(res.severity_score, 70.0)

    def test_canonical_flood_severity_classification(self):
        """Verify severity classification on canonical flood event (flood-emilia-romagna-2023)."""
        res = classify_severity("flood-emilia-romagna-2023")

        self.assertEqual(res.event_id, "flood-emilia-romagna-2023")
        self.assertEqual(res.disaster_type, "flood")
        self.assertIn(res.severity_level, {"LOW", "MODERATE", "HIGH", "CRITICAL"})
        self.assertIsNotNone(res.limitations)

    def test_canonical_wildfire_severity_classification(self):
        """Verify severity classification on canonical wildfire event (wildfire-rhodes-2023)."""
        res = classify_severity("wildfire-rhodes-2023")

        self.assertEqual(res.event_id, "wildfire-rhodes-2023")
        self.assertEqual(res.disaster_type, "wildfire")
        self.assertIn(res.severity_level, {"LOW", "MODERATE", "HIGH", "CRITICAL"})
        self.assertIsNotNone(res.limitations)


if __name__ == "__main__":
    unittest.main()
