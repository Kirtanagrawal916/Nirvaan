"""
Unit tests for NIRVAAN Disaster Mask Generator (analysis/mask_generator.py - TASK-011)
"""

import unittest
import numpy as np

from analysis.mask_generator import (
    DisasterMask,
    MaskGenerator,
    generate_disaster_mask,
    hex_to_rgba,
)
from detection.flood_detector import detect_flood
from detection.wildfire_detector import detect_wildfire


class TestMaskGenerator(unittest.TestCase):
    """Test suite for MaskGenerator mask conversion, spatial metadata preservation, and RGBA rendering."""

    def setUp(self):
        self.generator = MaskGenerator()

    def test_hex_to_rgba_conversion(self):
        """Verify hex_to_rgba converts '#0066FF' correctly to (0, 102, 255, 200)."""
        r, g, b, a = hex_to_rgba("#0066FF", alpha=200)
        self.assertEqual((r, g, b, a), (0, 102, 255, 200))

    def test_flood_mask_generation_and_metadata(self):
        """Verify mask generation from flood detection result."""
        flood_res = detect_flood("flood-emilia-romagna-2023")
        mask_obj = self.generator.from_flood_result(flood_res)

        self.assertIsInstance(mask_obj, DisasterMask)
        self.assertEqual(mask_obj.event_id, "flood-emilia-romagna-2023")
        self.assertEqual(mask_obj.disaster_type, "flood")
        self.assertEqual(mask_obj.dimensions, flood_res.dimensions)
        self.assertEqual(mask_obj.CRS, flood_res.CRS)
        self.assertEqual(mask_obj.resolution_m, flood_res.resolution_m)
        self.assertEqual(mask_obj.mask.shape, flood_res.dimensions)
        self.assertEqual(mask_obj.mask.dtype, np.uint8)

    def test_wildfire_mask_generation_and_metadata(self):
        """Verify mask generation from wildfire detection result."""
        wildfire_res = detect_wildfire("wildfire-rhodes-2023")
        mask_obj = self.generator.from_wildfire_result(wildfire_res)

        self.assertIsInstance(mask_obj, DisasterMask)
        self.assertEqual(mask_obj.event_id, "wildfire-rhodes-2023")
        self.assertEqual(mask_obj.disaster_type, "wildfire")
        self.assertEqual(mask_obj.dimensions, wildfire_res.dimensions)
        self.assertEqual(mask_obj.CRS, wildfire_res.CRS)
        self.assertEqual(mask_obj.resolution_m, wildfire_res.resolution_m)
        self.assertIn(1, mask_obj.category_labels)

    def test_render_mask_rgba(self):
        """Verify render_mask_rgba produces (H, W, 4) uint8 RGBA image array."""
        flood_res = detect_flood("flood-emilia-romagna-2023")
        mask_obj = self.generator.from_flood_result(flood_res)
        rgba = self.generator.render_mask_rgba(mask_obj)

        h, w = mask_obj.dimensions
        self.assertEqual(rgba.shape, (h, w, 4))
        self.assertEqual(rgba.dtype, np.uint8)

    def test_generate_disaster_mask_helper(self):
        """Verify public helper generate_disaster_mask works for event_id string."""
        mask_obj = generate_disaster_mask("flood-emilia-romagna-2023")
        self.assertEqual(mask_obj.event_id, "flood-emilia-romagna-2023")


if __name__ == "__main__":
    unittest.main()
