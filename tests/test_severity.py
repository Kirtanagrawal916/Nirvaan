"""
Deterministic Unit Tests for NIRVAAN Prototype Severity & Composite Impact Scoring Engine
"""

import site
import sys
import unittest

# Ensure user site packages are in sys.path
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

from analysis.severity import calculate_composite_impact_score


class TestCompositeImpactScoring(unittest.TestCase):

    def test_calculate_composite_impact_score_maximum_boundary(self):
        infra_facilities = [
            {"category": "hospital", "distance_km": 0.2},
            {"category": "bridge", "distance_km": 0.5},
            {"category": "power", "distance_km": 0.8},
            {"category": "school", "distance_km": 1.0}
        ]
        result = calculate_composite_impact_score(
            spectral_severity="Extreme",
            population_estimate=15000,
            infrastructure_impact={"impacted_infrastructure": infra_facilities},
            hotspots=10
        )

        self.assertEqual(result["status"], "PROTOTYPE")
        self.assertEqual(result["provenance_label"], "PROTOTYPE")
        self.assertTrue(result["is_prototype"])
        self.assertEqual(result["impact_score"], 100.0)
        self.assertEqual(result["impact_band"], "Extreme")

    def test_calculate_composite_impact_score_minimum_boundary(self):
        result = calculate_composite_impact_score(
            spectral_severity=None,
            population_estimate=None,
            infrastructure_impact=None,
            hotspots=None
        )

        self.assertEqual(result["status"], "PROTOTYPE")
        self.assertEqual(result["provenance_label"], "PROTOTYPE")
        self.assertEqual(result["impact_score"], 0.0)
        self.assertEqual(result["impact_band"], "Low")

    def test_intermediate_scenario_and_transparency(self):
        infra_facilities = [{"category": "hospital", "distance_km": 1.5}]
        result = calculate_composite_impact_score(
            spectral_severity="Moderate",
            population_estimate=500,
            infrastructure_impact={"impacted_infrastructure": infra_facilities},
            hotspots=3
        )

        self.assertEqual(result["status"], "PROTOTYPE")
        self.assertGreater(result["impact_score"], 20.0)
        self.assertLess(result["impact_score"], 80.0)

        # Transparent contributing factors check
        factors = result["contributing_factors"]
        self.assertIn("spectral_evidence", factors)
        self.assertIn("population_exposure", factors)
        self.assertIn("infrastructure_proximity", factors)
        self.assertIn("hotspot_concentration", factors)

        self.assertAlmostEqual(factors["spectral_evidence"]["subscore"], 50.0)
        self.assertGreater(factors["spectral_evidence"]["points_contributed"], 0)

    def test_custom_weights_and_thresholds(self):
        # 100% Spectral Weight Test
        custom_weights = {"spectral": 1.0, "population": 0.0, "infrastructure": 0.0, "hotspots": 0.0}
        result = calculate_composite_impact_score(
            spectral_severity="High",  # 75.0 subscore
            population_estimate=0,
            weights=custom_weights
        )

        self.assertEqual(result["impact_score"], 75.0)
        self.assertEqual(result["impact_band"], "Extreme")  # 75-100 threshold


if __name__ == "__main__":
    unittest.main()
