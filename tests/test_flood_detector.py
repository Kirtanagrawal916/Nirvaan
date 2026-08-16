"""
Unit tests for NIRVAAN NDWI Flood Detector (detection/flood_detector.py - TASK-008)
"""

import unittest
import numpy as np

from data.loader import load_event
from detection.flood_detector import FloodDetector, detect_flood
from preprocessing.preprocess import ProcessedRaster


class TestFloodDetector(unittest.TestCase):
    """Test suite for FloodDetector NDWI calculations, zero denominator protection, and canonical flood integration."""

    def setUp(self):
        self.detector = FloodDetector(threshold_override=0.0)

    def test_ndwi_calculation_accuracy(self):
        """Verify NDWI calculation (Green - NIR) / (Green + NIR)."""
        # Create synthetic raster: Green=0.4, NIR=0.1 -> NDWI = (0.4-0.1)/(0.4+0.1) = 0.3/0.5 = 0.6
        green = np.full((10, 10), 0.4, dtype=np.float32)
        nir = np.full((10, 10), 0.1, dtype=np.float32)

        raster = ProcessedRaster(
            bands={"B03": green, "B08": nir},
            dimensions=(10, 10),
            CRS="EPSG:32632",
            resolution_m=10.0,
            valid_mask=np.ones((10, 10), dtype=bool),
        )

        ndwi, valid = self.detector.calculate_ndwi(raster)
        self.assertTrue(np.all(valid))
        self.assertAlmostEqual(float(ndwi[0, 0]), 0.6, places=4)

    def test_zero_denominator_handling(self):
        """Verify zero denominator (Green + NIR == 0) produces 0.0 NDWI without NaN/Inf errors."""
        green = np.zeros((10, 10), dtype=np.float32)
        nir = np.zeros((10, 10), dtype=np.float32)

        raster = ProcessedRaster(
            bands={"B03": green, "B08": nir},
            dimensions=(10, 10),
            CRS="EPSG:32632",
            resolution_m=10.0,
            valid_mask=np.ones((10, 10), dtype=bool),
        )

        ndwi, valid = self.detector.calculate_ndwi(raster)
        self.assertFalse(np.any(np.isnan(ndwi)))
        self.assertFalse(np.any(np.isinf(ndwi)))
        self.assertEqual(float(ndwi[0, 0]), 0.0)

    def test_nodata_masking(self):
        """Verify nodata pixels are excluded from valid mask and calculation."""
        green = np.full((5, 5), 0.5, dtype=np.float32)
        nir = np.full((5, 5), 0.2, dtype=np.float32)
        valid_m = np.ones((5, 5), dtype=bool)
        valid_m[0, 0] = False  # Nodata pixel

        raster = ProcessedRaster(
            bands={"B03": green, "B08": nir},
            dimensions=(5, 5),
            CRS="EPSG:32632",
            resolution_m=10.0,
            valid_mask=valid_m,
        )

        ndwi, valid = self.detector.calculate_ndwi(raster)
        self.assertFalse(valid[0, 0])
        self.assertEqual(float(ndwi[0, 0]), 0.0)

    def test_canonical_flood_event_detection(self):
        """Verify end-to-end detection on canonical flood event (flood-emilia-romagna-2023)."""
        res = detect_flood("flood-emilia-romagna-2023")

        self.assertEqual(res.event_id, "flood-emilia-romagna-2023")
        self.assertEqual(res.disaster_type, "flood")
        self.assertEqual(res.method, "NDWI_DIFFERENCE")
        self.assertEqual(res.index_name, "NDWI")
        self.assertEqual(res.threshold_used, 0.0)
        self.assertEqual(res.CRS, "EPSG:32632 (WGS 84 / UTM zone 32N)")
        self.assertEqual(res.resolution_m, 10.0)
        self.assertEqual(res.flood_mask.shape, res.dimensions)
        self.assertGreater(res.valid_pixel_count, 0)
        self.assertIsNotNone(res.provenance)
        self.assertIn("source_provider", res.provenance)

        # Check serialization output
        summary = res.to_dict()
        self.assertEqual(summary["event_id"], "flood-emilia-romagna-2023")
        self.assertIn("affected_pixel_count", summary)


if __name__ == "__main__":
    unittest.main()
