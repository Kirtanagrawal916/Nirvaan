"""
Unit tests for NIRVAAN Change Detector (detection/change_detection.py - TASK-010)
"""

import unittest
import numpy as np

from data.loader import load_event
from detection.change_detection import ChangeDetector, detect_change


class TestChangeDetector(unittest.TestCase):
    """Test suite for ChangeDetector difference math, nodata/NaN handling, and event integration."""

    def setUp(self):
        self.detector = ChangeDetector()

    def test_compute_difference_accuracy(self):
        """Verify compute_difference computes (after - before) accurately."""
        before = np.array([[0.2, 0.4], [0.1, 0.5]], dtype=np.float32)
        after = np.array([[0.6, 0.4], [0.3, 0.2]], dtype=np.float32)

        diff, valid = self.detector.compute_difference(before, after)
        self.assertTrue(np.all(valid))
        self.assertAlmostEqual(float(diff[0, 0]), 0.4, places=4)
        self.assertAlmostEqual(float(diff[1, 1]), -0.3, places=4)

    def test_compute_difference_handles_nan_and_inf(self):
        """Verify compute_difference handles NaN and Inf values without crashing."""
        before = np.array([[0.2, np.nan], [np.inf, 0.5]], dtype=np.float32)
        after = np.array([[0.6, 0.4], [0.3, -np.inf]], dtype=np.float32)

        diff, valid = self.detector.compute_difference(before, after)
        self.assertTrue(valid[0, 0])
        self.assertFalse(valid[0, 1])
        self.assertFalse(valid[1, 0])
        self.assertFalse(valid[1, 1])
        self.assertEqual(float(diff[0, 1]), 0.0)

    def test_canonical_flood_change_detection(self):
        """Verify change detection integration on canonical flood event."""
        res = detect_change("flood-emilia-romagna-2023")

        self.assertEqual(res.event_id, "flood-emilia-romagna-2023")
        self.assertEqual(res.disaster_type, "flood")
        self.assertEqual(res.method, "NDWI_CHANGE_DETECTION")
        self.assertEqual(res.CRS, "EPSG:32632 (WGS 84 / UTM zone 32N)")
        self.assertEqual(res.resolution_m, 10.0)
        self.assertGreater(res.valid_pixel_count, 0)
        self.assertEqual(res.change_mask.shape, res.dimensions)
        self.assertEqual(res.difference_index.shape, res.dimensions)

    def test_canonical_wildfire_change_detection(self):
        """Verify change detection integration on canonical wildfire event."""
        res = detect_change("wildfire-rhodes-2023")

        self.assertEqual(res.event_id, "wildfire-rhodes-2023")
        self.assertEqual(res.disaster_type, "wildfire")
        self.assertEqual(res.method, "DNBR_CHANGE_DETECTION")
        self.assertEqual(res.CRS, "EPSG:32635 (WGS 84 / UTM zone 35N)")
        self.assertEqual(res.resolution_m, 10.0)
        self.assertGreater(res.valid_pixel_count, 0)
        self.assertEqual(res.change_mask.shape, res.dimensions)
        self.assertEqual(res.difference_index.shape, res.dimensions)


if __name__ == "__main__":
    unittest.main()
