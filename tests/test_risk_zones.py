"""
Deterministic Unit Tests for NIRVAAN Risk-Zone Generation
"""

import site
import sys
import unittest

# Ensure user site packages are in sys.path
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

from analysis.risk_zones import (
    buffer_polygon_vertices,
    generate_risk_zones,
    to_geojson_risk_zones,
)
from mapping.geojson import DEFAULT_CRS


class TestRiskZoneGeneration(unittest.TestCase):

    def test_buffer_polygon_vertices(self):
        # Square polygon: lat [10, 12], lon [20, 22]
        square_ring = [(10.0, 20.0), (10.0, 22.0), (12.0, 22.0), (12.0, 20.0), (10.0, 20.0)]
        buffered = buffer_polygon_vertices(square_ring, offset_dist=0.01)

        self.assertIsNotNone(buffered)
        self.assertEqual(len(buffered), len(square_ring))
        self.assertEqual(buffered[0], buffered[-1])  # Closed ring

        # Calculate bounding box to verify expansion
        lats_orig = [pt[0] for pt in square_ring]
        lons_orig = [pt[1] for pt in square_ring]
        lats_buf = [pt[0] for pt in buffered]
        lons_buf = [pt[1] for pt in buffered]

        self.assertGreater(max(lats_buf), max(lats_orig))
        self.assertLess(min(lats_buf), min(lats_orig))
        self.assertGreater(max(lons_buf), max(lons_orig))
        self.assertLess(min(lons_buf), min(lons_orig))

    def test_generate_risk_zones_valid(self):
        square_ring = [(26.0, 92.0), (26.0, 92.2), (26.2, 92.2), (26.2, 92.0), (26.0, 92.0)]
        input_polygons = [
            {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[(20.0, 10.0), (22.0, 10.0), (22.0, 12.0), (20.0, 12.0), (20.0, 10.0)]]}}
        ]

        # Use raw ring input
        zones = generate_risk_zones([square_ring])
        self.assertEqual(len(zones), 3)

        # Tier 1: Core (High)
        self.assertEqual(zones[0]["properties"]["severity"], "High")
        self.assertEqual(zones[0]["properties"]["zone_type"], "core")
        self.assertEqual(zones[0]["properties"]["buffer_deg"], 0.0)

        # Tier 2: Moderate Buffer
        self.assertEqual(zones[1]["properties"]["severity"], "Moderate")
        self.assertEqual(zones[1]["properties"]["zone_type"], "buffer_moderate")
        self.assertEqual(zones[1]["properties"]["buffer_deg"], 0.01)

        # Tier 3: Low Buffer
        self.assertEqual(zones[2]["properties"]["severity"], "Low")
        self.assertEqual(zones[2]["properties"]["zone_type"], "buffer_low")
        self.assertEqual(zones[2]["properties"]["buffer_deg"], 0.025)

    def test_generate_risk_zones_empty_and_invalid(self):
        # Empty input list
        self.assertEqual(generate_risk_zones([]), [])
        self.assertEqual(generate_risk_zones(None), [])

        # Invalid / degenerate ring
        invalid_ring = [(10.0, 20.0), (10.0, 22.0), (10.0, 20.0)]  # Collinear / zero area
        self.assertEqual(generate_risk_zones([invalid_ring]), [])

    def test_to_geojson_risk_zones(self):
        square_ring = [(26.0, 92.0), (26.0, 92.2), (26.2, 92.2), (26.2, 92.0), (26.0, 92.0)]
        zones = generate_risk_zones([square_ring])

        fc = to_geojson_risk_zones(zones, include_crs=True)
        self.assertEqual(fc["type"], "FeatureCollection")
        self.assertEqual(len(fc["features"]), 3)
        self.assertEqual(fc["crs"], DEFAULT_CRS)

        # Verify GeoJSON coordinate ordering [longitude, latitude]
        first_coords = fc["features"][0]["geometry"]["coordinates"][0]
        self.assertGreater(first_coords[0][0], 90.0)  # Longitude (~92.0)
        self.assertLess(first_coords[0][1], 30.0)     # Latitude (~26.0)


if __name__ == "__main__":
    unittest.main()
