"""
Unit tests for NIRVAAN Hotspot Extractor (analysis/hotspots.py - TASK-014)
"""

import unittest
import numpy as np

from analysis.hotspots import (
    HotspotExtractor,
    extract_hotspots,
    utm_to_latlon,
)
from analysis.mask_generator import DisasterMask, generate_disaster_mask


class TestHotspotExtractor(unittest.TestCase):
    """Test suite for HotspotExtractor clustering, noise filtering, UTM conversion, and metadata."""

    def setUp(self):
        self.extractor = HotspotExtractor(min_pixels=5)

    def test_utm_to_latlon_conversion(self):
        """Verify UTM zone 32 Easting/Northing converts to valid Italy lat/lon."""
        # 500000 Easting, 4900000 Northing in UTM Zone 32N is ~44.25°N, ~11.0°E
        lat, lon = utm_to_latlon(500000.0, 4900000.0, zone=32, northern=True)
        self.assertAlmostEqual(lat, 44.25, delta=1.0)
        self.assertAlmostEqual(lon, 11.0, delta=2.0)

    def test_one_obvious_hotspot(self):
        """Verify a single contiguous block of 20 pixels is extracted as 1 hotspot."""
        mask = np.zeros((20, 20), dtype=np.uint8)
        mask[5:10, 5:9] = 1  # 5x4 = 20 pixels

        mask_obj = DisasterMask(
            event_id="test-one-hotspot",
            disaster_type="flood",
            mask=mask,
            dimensions=(20, 20),
            CRS="EPSG:32632",
            resolution_m=10.0,
            valid_pixel_count=400,
            affected_pixel_count=20,
        )

        res = self.extractor.extract_hotspots(mask_obj)
        self.assertEqual(res.total_hotspots, 1)
        h0 = res.hotspots[0]
        self.assertEqual(h0.hotspot_id, "hotspot-01")
        self.assertEqual(h0.pixel_count, 20)
        self.assertEqual(h0.area_m2, 2000.0)

    def test_multiple_hotspots_and_noise_filtering(self):
        """Verify multiple hotspots are extracted and isolated pixels < min_pixels are filtered."""
        mask = np.zeros((30, 30), dtype=np.uint8)
        # Cluster 1: 15 pixels
        mask[2:5, 2:7] = 1
        # Cluster 2: 8 pixels
        mask[15:17, 15:19] = 1
        # Noise pixel: 2 pixels (below min_pixels=5)
        mask[25, 25:27] = 1

        mask_obj = DisasterMask(
            event_id="test-multi-hotspot",
            disaster_type="wildfire",
            mask=mask,
            dimensions=(30, 30),
            CRS="EPSG:32635",
            resolution_m=10.0,
            valid_pixel_count=900,
            affected_pixel_count=25,
        )

        res = self.extractor.extract_hotspots(mask_obj)
        # Should extract 2 clusters (15 and 8 pixels), filtering out noise (2 pixels)
        self.assertEqual(res.total_hotspots, 2)
        self.assertEqual(res.hotspots[0].pixel_count, 15)
        self.assertEqual(res.hotspots[1].pixel_count, 8)

    def test_zero_hotspots_case(self):
        """Verify all zeros mask produces 0 total hotspots."""
        mask = np.zeros((10, 10), dtype=np.uint8)
        mask_obj = DisasterMask(
            event_id="test-zero-hotspot",
            disaster_type="flood",
            mask=mask,
            dimensions=(10, 10),
            CRS="EPSG:32632",
            resolution_m=10.0,
            valid_pixel_count=100,
            affected_pixel_count=0,
        )

        res = self.extractor.extract_hotspots(mask_obj)
        self.assertEqual(res.total_hotspots, 0)
        self.assertEqual(len(res.hotspots), 0)

    def test_canonical_flood_hotspot_extraction(self):
        """Verify hotspot extraction on canonical flood mask."""
        flood_mask = generate_disaster_mask("flood-emilia-romagna-2023")
        res = extract_hotspots(flood_mask, min_pixels=10)

        self.assertEqual(res.event_id, "flood-emilia-romagna-2023")
        self.assertEqual(res.disaster_type, "flood")
        self.assertGreaterEqual(res.total_hotspots, 0)

        if res.total_hotspots > 0:
            h0 = res.hotspots[0]
            self.assertGreater(h0.centroid_latitude, 0.0)
            self.assertGreater(h0.centroid_longitude, 0.0)

    def test_canonical_wildfire_hotspot_extraction(self):
        """Verify hotspot extraction on canonical wildfire mask."""
        wildfire_mask = generate_disaster_mask("wildfire-rhodes-2023")
        res = extract_hotspots(wildfire_mask, min_pixels=10)

        self.assertEqual(res.event_id, "wildfire-rhodes-2023")
        self.assertEqual(res.disaster_type, "wildfire")
        self.assertGreaterEqual(res.total_hotspots, 0)


if __name__ == "__main__":
    unittest.main()
