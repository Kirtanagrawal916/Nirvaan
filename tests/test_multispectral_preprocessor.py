"""
Unit tests for NIRVAAN Multispectral Preprocessor (preprocessing/preprocess.py - TASK-007)
"""

import tempfile
import unittest
from pathlib import Path

import numpy as np

from data.loader import load_event
from preprocessing.preprocess import MultispectralPreprocessor, ProcessedRaster


class TestMultispectralPreprocessor(unittest.TestCase):
    """Test suite for MultispectralPreprocessor rules, nodata/NaN handling, and metadata preservation."""

    def setUp(self):
        self.preprocessor = MultispectralPreprocessor()
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.tmp_dir.name) / "test_raster_dir"
        self.test_dir.mkdir()

        # Create dummy band placeholder files
        (self.test_dir / "B03.tif").touch()
        (self.test_dir / "B08.tif").touch()

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_sanitize_array_handles_nan_and_inf(self):
        """Verify sanitize_array cleanly removes NaN and Inf values while building valid_mask."""
        raw_arr = np.array([[0.5, np.nan], [np.inf, -np.inf]], dtype=np.float32)
        sanitized, valid_mask = self.preprocessor.sanitize_array(raw_arr)

        self.assertFalse(np.any(np.isnan(sanitized)))
        self.assertFalse(np.any(np.isinf(sanitized)))
        self.assertTrue(valid_mask[0, 0])
        self.assertFalse(valid_mask[0, 1])
        self.assertFalse(valid_mask[1, 0])
        self.assertFalse(valid_mask[1, 1])

    def test_nodata_handling(self):
        """Verify nodata values are masked out correctly."""
        raw_arr = np.array([[10.0, -9999.0], [50.0, 100.0]], dtype=np.float32)
        sanitized, valid_mask = self.preprocessor.sanitize_array(raw_arr, nodata_val=-9999.0)

        self.assertTrue(valid_mask[0, 0])
        self.assertFalse(valid_mask[0, 1])
        self.assertEqual(sanitized[0, 1], 0.0)

    def test_preprocess_raster_metadata_preservation(self):
        """Verify CRS, transform, dimensions, resolution, and bounds are preserved."""
        processed = self.preprocessor.preprocess_raster(
            self.test_dir,
            required_bands=["B03", "B08"],
            default_crs="EPSG:32632",
            default_resolution=10.0,
        )

        self.assertEqual(processed.CRS, "EPSG:32632")
        self.assertEqual(processed.resolution_m, 10.0)
        self.assertEqual(processed.dimensions, (512, 512))
        self.assertIsNotNone(processed.transform)
        self.assertIsNotNone(processed.bounds)
        self.assertIn("B03", processed.bands)
        self.assertIn("B08", processed.bands)

    def test_preprocess_event_canonical_flood(self):
        """Verify preprocess_event processes canonical flood event before/after rasters."""
        flood_event = load_event("flood-emilia-romagna-2023")
        before_p, after_p = self.preprocessor.preprocess_event(flood_event)

        self.assertEqual(before_p.CRS, "EPSG:32632 (WGS 84 / UTM zone 32N)")
        self.assertEqual(after_p.CRS, "EPSG:32632 (WGS 84 / UTM zone 32N)")
        self.assertEqual(before_p.resolution_m, 10.0)
        self.assertEqual(after_p.resolution_m, 10.0)
        self.assertEqual(before_p.dimensions, after_p.dimensions)

    def test_get_band_missing_raises_keyerror(self):
        """Verify get_band raises KeyError for missing band name."""
        processed = self.preprocessor.preprocess_raster(self.test_dir, required_bands=["B03"])
        with self.assertRaises(KeyError):
            processed.get_band("B99")


if __name__ == "__main__":
    unittest.main()
