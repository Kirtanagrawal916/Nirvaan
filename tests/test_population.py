"""
Deterministic Unit Tests for NIRVAAN Population Impact Estimation
"""

import site
import sys
import unittest
import numpy as np

# Ensure user site packages are in sys.path
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

from analysis.population import (
    create_synthetic_population_grid,
    estimate_affected_population,
)
from analysis.risk_zones import generate_risk_zones


class TestPopulationEstimation(unittest.TestCase):

    def test_estimate_affected_population_valid_grid(self):
        transform = {
            "origin_lat": 26.0,
            "origin_lon": 92.0,
            "pixel_size_lat": -0.01,
            "pixel_size_lon": 0.01
        }
        # 10x10 grid with 100 people per pixel
        pop_data = create_synthetic_population_grid(10, 10, transform, density_per_pixel=100.0)

        # Polygon covering rows 1..3, cols 1..3 (4 pixel centers: (1.5, 1.5) grid area)
        square_ring = [
            (25.995, 92.005),
            (25.995, 92.025),
            (25.975, 92.025),
            (25.975, 92.005),
            (25.995, 92.005)
        ]

        result = estimate_affected_population([square_ring], population_data=pop_data)
        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["provenance_label"], "ESTIMATE")
        self.assertGreater(result["estimated_affected_population"], 0)
        self.assertEqual(len(result["zone_breakdown"]), 1)
        self.assertEqual(result["zone_breakdown"][0]["provenance_label"], "ESTIMATE")

    def test_estimate_affected_population_risk_zones(self):
        transform = {
            "origin_lat": 26.0,
            "origin_lon": 92.0,
            "pixel_size_lat": -0.01,
            "pixel_size_lon": 0.01
        }
        pop_data = create_synthetic_population_grid(10, 10, transform, density_per_pixel=50.0)

        square_ring = [(25.99, 92.01), (25.99, 92.03), (25.97, 92.03), (25.97, 92.01), (25.99, 92.01)]
        risk_zones = generate_risk_zones([square_ring])

        result = estimate_affected_population(risk_zones, population_data=pop_data)
        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["provenance_label"], "ESTIMATE")
        self.assertEqual(result["total_zones_analyzed"], 3)
        self.assertEqual(len(result["zone_breakdown"]), 3)

    def test_population_data_unavailable_rejection(self):
        square_ring = [(26.0, 92.0), (26.0, 92.2), (26.2, 92.2), (26.2, 92.0), (26.0, 92.0)]

        # None population data
        res_none = estimate_affected_population([square_ring], population_data=None)
        self.assertEqual(res_none["status"], "DATA_UNAVAILABLE")
        self.assertIsNone(res_none["estimated_affected_population"])
        self.assertEqual(res_none["provenance_label"], "ESTIMATE")

        # Empty dict population data
        res_empty = estimate_affected_population([square_ring], population_data={})
        self.assertEqual(res_empty["status"], "DATA_UNAVAILABLE")
        self.assertIsNone(res_empty["estimated_affected_population"])
        self.assertEqual(res_empty["provenance_label"], "ESTIMATE")

    def test_no_valid_polygons(self):
        transform = {"origin_lat": 26.0, "origin_lon": 92.0, "pixel_size_lat": -0.01, "pixel_size_lon": 0.01}
        pop_data = create_synthetic_population_grid(5, 5, transform)

        res_empty_poly = estimate_affected_population([], population_data=pop_data)
        self.assertEqual(res_empty_poly["status"], "NO_AFFECTED_POLYGONS")
        self.assertEqual(res_empty_poly["estimated_affected_population"], 0)
        self.assertEqual(res_empty_poly["provenance_label"], "ESTIMATE")


if __name__ == "__main__":
    unittest.main()
