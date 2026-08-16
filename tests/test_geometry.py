"""
Deterministic Unit Tests for NIRVAAN Mask Processing and Disaster Polygon Extraction
"""

import site
import sys
import unittest
import numpy as np

# Ensure user site packages are in sys.path
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

from detection.mask import (
    clean_binary_mask,
    extract_contours_from_mask,
    transform_pixel_to_geo,
    validate_polygon_ring,
    mask_to_polygons,
)


class TestGeometryExtraction(unittest.TestCase):

    def test_clean_binary_mask_noise_removal(self):
        # 10x10 grid with one 3x3 region (9 pixels) and one 2-pixel isolated noise blob
        mask = np.zeros((10, 10), dtype=bool)
        mask[1:4, 1:4] = True  # 9 pixels region
        mask[8, 8:10] = True   # 2 pixels noise

        cleaned = clean_binary_mask(mask, min_pixels=5)
        self.assertTrue(np.any(cleaned[1:4, 1:4]))
        self.assertFalse(np.any(cleaned[8, 8:10]))
        self.assertEqual(np.sum(cleaned), 9)

    def test_empty_mask_handling(self):
        # All zero mask
        empty_mask = np.zeros((20, 20), dtype=bool)
        transform = {"origin_lat": 26.0, "origin_lon": 92.0, "pixel_size_lat": -0.001, "pixel_size_lon": 0.001}
        
        polygons = mask_to_polygons(empty_mask, transform, min_pixels=5)
        self.assertEqual(polygons, [])

        # None / Invalid type mask
        self.assertEqual(mask_to_polygons([], transform), [])

    def test_transform_pixel_to_geo(self):
        transform_dict = {
            "origin_lat": 26.0,
            "origin_lon": 92.0,
            "pixel_size_lat": -0.01,
            "pixel_size_lon": 0.01
        }
        lat, lon = transform_pixel_to_geo(10, 20, transform_dict)
        self.assertAlmostEqual(lat, 25.9)
        self.assertAlmostEqual(lon, 92.2)

        transform_tuple = (26.0, 92.0, -0.01, 0.01)
        lat2, lon2 = transform_pixel_to_geo(5, 5, transform_tuple)
        self.assertAlmostEqual(lat2, 25.95)
        self.assertAlmostEqual(lon2, 92.05)

    def test_validate_polygon_ring(self):
        # Valid square ring
        valid_ring = [(10.0, 20.0), (10.0, 22.0), (12.0, 22.0), (12.0, 20.0), (10.0, 20.0)]
        self.assertTrue(validate_polygon_ring(valid_ring))

        # Open ring (not closed)
        open_ring = [(10.0, 20.0), (10.0, 22.0), (12.0, 22.0), (12.0, 20.0)]
        self.assertFalse(validate_polygon_ring(open_ring))

        # Collinear / zero-area ring
        zero_area_ring = [(10.0, 20.0), (10.0, 22.0), (10.0, 20.0)]
        self.assertFalse(validate_polygon_ring(zero_area_ring))

        # Self-intersecting figure-8 ring
        figure_8_ring = [(0.0, 0.0), (2.0, 2.0), (0.0, 2.0), (2.0, 0.0), (0.0, 0.0)]
        self.assertFalse(validate_polygon_ring(figure_8_ring))

    def test_mask_to_polygons_valid_extraction(self):
        mask = np.zeros((15, 15), dtype=bool)
        mask[2:7, 2:7] = True  # 5x5 region (25 pixels)

        transform = {
            "origin_lat": 26.5,
            "origin_lon": 92.5,
            "pixel_size_lat": -0.001,
            "pixel_size_lon": 0.001
        }

        polygons = mask_to_polygons(mask, transform, min_pixels=5, properties={"event_id": "EVT_001", "severity": "High"})
        self.assertEqual(len(polygons), 1)

        feat = polygons[0]
        self.assertEqual(feat["type"], "Feature")
        self.assertEqual(feat["geometry"]["type"], "Polygon")
        self.assertEqual(feat["properties"]["event_id"], "EVT_001")
        self.assertEqual(feat["properties"]["severity"], "High")
        self.assertEqual(feat["properties"]["region_id"], 1)

        # Verify GeoJSON coordinate ordering [lon, lat]
        coords = feat["geometry"]["coordinates"][0]
        self.assertGreater(coords[0][0], 90.0)  # Longitude (~92.5)
        self.assertLess(coords[0][1], 30.0)     # Latitude (~26.5)


if __name__ == "__main__":
    unittest.main()
