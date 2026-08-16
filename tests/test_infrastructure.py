"""
Deterministic Unit Tests for NIRVAAN Infrastructure Impact Analysis
"""

import site
import sys
import unittest

# Ensure user site packages are in sys.path
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

from analysis.infrastructure import (
    haversine_distance,
    create_synthetic_infrastructure_layer,
    analyze_infrastructure_impact,
)


class TestInfrastructureAnalysis(unittest.TestCase):

    def test_haversine_distance_accuracy(self):
        # Known distance between Assam points (~2.47 km)
        dist = haversine_distance(26.2006, 92.9376, 26.2100, 92.9150)
        self.assertGreater(dist, 2.0)
        self.assertLess(dist, 3.0)

        # Same point distance is 0
        self.assertEqual(haversine_distance(26.0, 92.0, 26.0, 92.0), 0.0)

    def test_analyze_infrastructure_impact_synthetic(self):
        infra_layer = create_synthetic_infrastructure_layer()
        hotspot_pts = [{"lat": 26.2006, "lon": 92.9376}]

        result = analyze_infrastructure_impact(
            polygons_or_hotspots=hotspot_pts,
            infrastructure_data=infra_layer,
            max_threshold_km=5.0
        )

        self.assertEqual(result["status"], "SUCCESS")
        self.assertTrue(result["field_verification_recommended"])
        self.assertGreater(result["impacted_facilities_count"], 0)

        # Check advisory statement formatting
        advisories = result["advisory_statements"]
        self.assertGreater(len(advisories), 0)
        for text in advisories:
            self.assertIn("field verification recommended", text)

    def test_analyze_infrastructure_impact_threshold_filtering(self):
        infra_layer = create_synthetic_infrastructure_layer()
        # Distant hotspot (~1800 km away)
        distant_hotspot = [{"lat": 10.0, "lon": 70.0}]

        result = analyze_infrastructure_impact(
            polygons_or_hotspots=distant_hotspot,
            infrastructure_data=infra_layer,
            max_threshold_km=5.0
        )

        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["impacted_facilities_count"], 0)
        self.assertEqual(len(result["advisory_statements"]), 0)

    def test_infrastructure_data_unavailable_skipping(self):
        hotspot_pts = [{"lat": 26.2006, "lon": 92.9376}]

        # None dataset
        res_none = analyze_infrastructure_impact(hotspot_pts, infrastructure_data=None)
        self.assertEqual(res_none["status"], "DATA_UNAVAILABLE")
        self.assertEqual(res_none["impacted_infrastructure"], [])
        self.assertTrue(res_none["field_verification_recommended"])

        # Empty dict dataset
        res_empty = analyze_infrastructure_impact(hotspot_pts, infrastructure_data={})
        self.assertEqual(res_empty["status"], "DATA_UNAVAILABLE")
        self.assertEqual(res_empty["impacted_infrastructure"], [])


if __name__ == "__main__":
    unittest.main()
