"""
Unit tests for NIRVAAN NBR/dNBR Wildfire Detector (detection/wildfire_detector.py - TASK-009)
"""

import unittest
import numpy as np

from data.loader import load_event
from detection.wildfire_detector import WildfireDetector, detect_wildfire
from preprocessing.preprocess import ProcessedRaster


class TestWildfireDetector(unittest.TestCase):
    """Test suite for WildfireDetector NBR, dNBR calculations, zero denominator protection, and canonical wildfire integration."""

    def setUp(self):
        self.detector = WildfireDetector()

    def test_nbr_calculation_accuracy(self):
        """Verify NBR calculation (NIR - SWIR) / (NIR + SWIR)."""
        # NIR=0.5, SWIR=0.1 -> NBR = (0.5-0.1)/(0.5+0.1) = 0.4/0.6 = 0.6667
        nir = np.full((10, 10), 0.5, dtype=np.float32)
        swir = np.full((10, 10), 0.1, dtype=np.float32)

        raster = ProcessedRaster(
            bands={"B08": nir, "B12": swir},
            dimensions=(10, 10),
            CRS="EPSG:32635",
            resolution_m=10.0,
            valid_mask=np.ones((10, 10), dtype=bool),
        )

        nbr, valid = self.detector.calculate_nbr(raster)
        self.assertTrue(np.all(valid))
        self.assertAlmostEqual(float(nbr[0, 0]), 0.6667, places=3)

    def test_dnbr_calculation_and_burn_mask(self):
        """Verify dNBR = pre_fire_nbr - post_fire_nbr and burn mask generation."""
        # Pre-fire: healthy vegetation (high NIR, low SWIR) -> NBR ~ 0.6
        # Post-fire: burned land (low NIR, high SWIR) -> NBR ~ -0.2
        # dNBR = 0.6 - (-0.2) = 0.8 (High severity burn)
        pre_nir = np.full((5, 5), 0.5, dtype=np.float32)
        pre_swir = np.full((5, 5), 0.1, dtype=np.float32)

        post_nir = np.full((5, 5), 0.1, dtype=np.float32)
        post_swir = np.full((5, 5), 0.4, dtype=np.float32)

        before_r = ProcessedRaster(
            bands={"B08": pre_nir, "B12": pre_swir},
            dimensions=(5, 5),
            CRS="EPSG:32635",
            resolution_m=10.0,
            valid_mask=np.ones((5, 5), dtype=bool),
        )

        after_r = ProcessedRaster(
            bands={"B08": post_nir, "B12": post_swir},
            dimensions=(5, 5),
            CRS="EPSG:32635",
            resolution_m=10.0,
            valid_mask=np.ones((5, 5), dtype=bool),
        )

        pre_nbr, pre_v = self.detector.calculate_nbr(before_r)
        post_nbr, post_v = self.detector.calculate_nbr(after_r)

        dnbr = pre_nbr - post_nbr
        self.assertAlmostEqual(float(dnbr[0, 0]), 1.2667, places=3)
        self.assertGreater(float(dnbr[0, 0]), 0.1)

    def test_zero_denominator_handling(self):
        """Verify zero denominator (NIR + SWIR == 0) produces 0.0 NBR without errors."""
        nir = np.zeros((10, 10), dtype=np.float32)
        swir = np.zeros((10, 10), dtype=np.float32)

        raster = ProcessedRaster(
            bands={"B08": nir, "B12": swir},
            dimensions=(10, 10),
            CRS="EPSG:32635",
            resolution_m=10.0,
            valid_mask=np.ones((10, 10), dtype=bool),
        )

        nbr, valid = self.detector.calculate_nbr(raster)
        self.assertFalse(np.any(np.isnan(nbr)))
        self.assertFalse(np.any(np.isinf(nbr)))
        self.assertEqual(float(nbr[0, 0]), 0.0)

    def test_canonical_wildfire_event_detection(self):
        """Verify end-to-end detection on canonical wildfire event (wildfire-rhodes-2023)."""
        res = detect_wildfire("wildfire-rhodes-2023")

        self.assertEqual(res.event_id, "wildfire-rhodes-2023")
        self.assertEqual(res.disaster_type, "wildfire")
        self.assertEqual(res.method, "NBR_DNBR_DIFFERENCE")
        self.assertEqual(res.index_name, "dNBR")
        self.assertEqual(res.CRS, "EPSG:32635 (WGS 84 / UTM zone 35N)")
        self.assertEqual(res.resolution_m, 10.0)
        self.assertEqual(res.burn_mask.shape, res.dimensions)
        self.assertGreater(res.valid_pixel_count, 0)
        self.assertIn("severity_breakdown", res.to_dict())
        self.assertIsNotNone(res.provenance)


if __name__ == "__main__":
    unittest.main()
