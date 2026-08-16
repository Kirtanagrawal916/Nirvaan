"""
Unit tests for NIRVAAN Affected Area Calculator (analysis/affected_area.py - TASK-012)
"""

import unittest
import numpy as np

from analysis.affected_area import AreaCalculator, calculate_affected_area
from analysis.mask_generator import DisasterMask, generate_disaster_mask


class TestAffectedAreaCalculator(unittest.TestCase):
    """Test suite for AreaCalculator math, unit conversions, CRS handling, and canonical event integration."""

    def setUp(self):
        self.calculator = AreaCalculator()

    def test_known_pixel_count_and_resolution_projected(self):
        """Verify 100 pixels at 10m resolution = 10,000 m² = 1.0 ha = 0.01 km²."""
        mask = np.ones((10, 10), dtype=np.uint8)  # 10x10 = 100 pixels
        mask_obj = DisasterMask(
            event_id="test-event-01",
            disaster_type="flood",
            mask=mask,
            dimensions=(10, 10),
            CRS="EPSG:32632",  # UTM Projected
            resolution_m=10.0,
            valid_pixel_count=100,
            affected_pixel_count=100,
        )

        res = self.calculator.calculate_area(mask_obj)
        self.assertEqual(res.affected_pixel_count, 100)
        self.assertEqual(res.pixel_area_m2, 100.0)
        self.assertEqual(res.affected_area_m2, 10000.0)
        self.assertEqual(res.affected_area_hectares, 1.0)
        self.assertEqual(res.affected_area_km2, 0.01)
        self.assertEqual(res.method, "PROJECTED_UTM_SQUARE_PIXEL")

    def test_zero_affected_pixels(self):
        """Verify 0 affected pixels produces 0 m², 0 ha, 0 km²."""
        mask = np.zeros((10, 10), dtype=np.uint8)
        mask_obj = DisasterMask(
            event_id="test-event-02",
            disaster_type="flood",
            mask=mask,
            dimensions=(10, 10),
            CRS="EPSG:32632",
            resolution_m=10.0,
            valid_pixel_count=100,
            affected_pixel_count=0,
        )

        res = self.calculator.calculate_area(mask_obj)
        self.assertEqual(res.affected_pixel_count, 0)
        self.assertEqual(res.affected_area_m2, 0.0)
        self.assertEqual(res.affected_area_hectares, 0.0)
        self.assertEqual(res.affected_area_km2, 0.0)

    def test_invalid_resolution_raises_value_error(self):
        """Verify resolution <= 0 raises ValueError."""
        mask = np.ones((5, 5), dtype=np.uint8)
        mask_obj = DisasterMask(
            event_id="test-bad-res",
            disaster_type="flood",
            mask=mask,
            dimensions=(5, 5),
            CRS="EPSG:32632",
            resolution_m=0.0,
            valid_pixel_count=25,
            affected_pixel_count=25,
        )

        with self.assertRaises(ValueError):
            self.calculator.calculate_area(mask_obj)

    def test_geographic_crs_handling(self):
        """Verify Geographic EPSG:4326 CRS uses latitude cosine scaling for degree resolutions."""
        mask = np.ones((10, 10), dtype=np.uint8)
        mask_obj = DisasterMask(
            event_id="test-geo-crs",
            disaster_type="wildfire",
            mask=mask,
            dimensions=(10, 10),
            CRS="EPSG:4326",  # Geographic
            resolution_m=0.0001,  # In degrees (~11 meters)
            valid_pixel_count=100,
            affected_pixel_count=100,
        )

        res = self.calculator.calculate_area(mask_obj, latitude=45.0)
        self.assertEqual(res.method, "GEODESIC_LATITUDE_COSINE_SCALED")
        self.assertGreater(res.affected_area_m2, 0.0)

    def test_canonical_flood_event_affected_area(self):
        """Verify area calculation integration on canonical flood event (flood-emilia-romagna-2023)."""
        res = calculate_affected_area("flood-emilia-romagna-2023")

        self.assertEqual(res.event_id, "flood-emilia-romagna-2023")
        self.assertEqual(res.disaster_type, "flood")
        self.assertEqual(res.resolution_m, 10.0)
        self.assertEqual(res.pixel_area_m2, 100.0)
        self.assertGreaterEqual(res.affected_area_m2, 0.0)
        self.assertEqual(res.affected_area_km2, res.affected_area_m2 / 1000000.0)

        summary = res.to_dict()
        self.assertIn("affected_area_km2", summary)
        self.assertIn("affected_area_hectares", summary)

    def test_canonical_wildfire_event_affected_area(self):
        """Verify area calculation integration on canonical wildfire event (wildfire-rhodes-2023)."""
        res = calculate_affected_area("wildfire-rhodes-2023")

        self.assertEqual(res.event_id, "wildfire-rhodes-2023")
        self.assertEqual(res.disaster_type, "wildfire")
        self.assertEqual(res.resolution_m, 10.0)
        self.assertEqual(res.pixel_area_m2, 100.0)
        self.assertGreaterEqual(res.affected_area_m2, 0.0)
        self.assertEqual(res.affected_area_km2, res.affected_area_m2 / 1000000.0)


if __name__ == "__main__":
    unittest.main()
