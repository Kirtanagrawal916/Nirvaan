"""
Unit Tests for NIRVAAN Mapping & Geographic Coordinate Handling
"""

import math
import site
import sys
import unittest

# Ensure user site packages are included in sys.path
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

try:
    import folium
    HAS_FOLIUM = True
except ImportError:
    folium = None
    HAS_FOLIUM = False

from mapping.geojson import (
    DEFAULT_CRS,
    validate_coordinates,
    parse_event_coordinates,
    parse_hotspot_coordinates,
    calculate_bounds,
    create_point_feature,
    create_polygon_feature,
    create_feature_collection,
)
from mapping.map_builder import build_folium_map, get_severity_color
from ui.map_panel import render_map_panel


class TestCoordinateHandlingAndMapping(unittest.TestCase):

    def test_validate_coordinates_valid_and_boundaries(self):
        # Standard valid coordinates
        self.assertTrue(validate_coordinates(20.5937, 78.9629))
        self.assertTrue(validate_coordinates("15.5", "75.2"))

        # Exact boundary values
        self.assertTrue(validate_coordinates(90.0, 180.0))
        self.assertTrue(validate_coordinates(-90.0, -180.0))
        self.assertTrue(validate_coordinates(0.0, 180.0))
        self.assertTrue(validate_coordinates(90.0, 0.0))

    def test_validate_coordinates_invalid_and_out_of_bounds(self):
        # Out-of-bounds latitude
        self.assertFalse(validate_coordinates(90.0001, 78.0))
        self.assertFalse(validate_coordinates(-90.0001, 78.0))

        # Out-of-bounds longitude
        self.assertFalse(validate_coordinates(20.0, 180.0001))
        self.assertFalse(validate_coordinates(20.0, -180.0001))

        # Malformed, None, NaN, Inf
        self.assertFalse(validate_coordinates(None, 78.0))
        self.assertFalse(validate_coordinates(20.0, None))
        self.assertFalse(validate_coordinates(float("nan"), 78.0))
        self.assertFalse(validate_coordinates(20.0, float("inf")))
        self.assertFalse(validate_coordinates("invalid_lat", 78.0))

    def test_null_island_rejection(self):
        # Default behavior: reject (0.0, 0.0) as uninitialized/invented coordinate
        self.assertFalse(validate_coordinates(0.0, 0.0, allow_null_island=False))
        self.assertFalse(validate_coordinates("0", "0.0", allow_null_island=False))

        # When explicitly allowed
        self.assertTrue(validate_coordinates(0.0, 0.0, allow_null_island=True))

    def test_parse_event_coordinates(self):
        # Valid dict formats
        valid_1 = {"name": "Assam Flood", "lat": 26.2006, "lon": 92.9376}
        valid_2 = {"name": "Wildfire", "latitude": -33.8688, "longitude": 151.2093}
        self.assertEqual(parse_event_coordinates(valid_1), (26.2006, 92.9376))
        self.assertEqual(parse_event_coordinates(valid_2), (-33.8688, 151.2093))

        # Invalid / missing / malformed
        self.assertIsNone(parse_event_coordinates(None))
        self.assertIsNone(parse_event_coordinates({}))
        self.assertIsNone(parse_event_coordinates({"lat": 100.0, "lon": 50.0}))  # Invalid lat
        self.assertIsNone(parse_event_coordinates({"lat": 0.0, "lon": 0.0}))    # Null island

    def test_parse_hotspot_coordinates(self):
        raw_hotspots = [
            {"lat": 26.22, "lon": 92.91, "intensity": "Extreme"},
            {"latitude": 26.25, "longitude": 92.95, "intensity": "High"},
            {"lat": 999.0, "lon": 92.91, "intensity": "Invalid"},  # Rejected
            {"lat": 0.0, "lon": 0.0, "intensity": "Null Island"},   # Rejected
            "not a dict"                                           # Rejected
        ]
        parsed = parse_hotspot_coordinates(raw_hotspots)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["lat"], 26.22)
        self.assertEqual(parsed[0]["lon"], 92.91)
        self.assertEqual(parsed[1]["lat"], 26.25)
        self.assertEqual(parsed[1]["lon"], 92.95)

    def test_calculate_bounds(self):
        # Single point
        bounds = calculate_bounds([{"lat": 20.0, "lon": 78.0}])
        self.assertIsNotNone(bounds)
        self.assertEqual(len(bounds), 2)
        self.assertLess(bounds[0][0], bounds[1][0])
        self.assertLess(bounds[0][1], bounds[1][1])

        # Multiple points
        pts = [(10.0, 70.0), (30.0, 80.0), (20.0, 75.0)]
        bounds_multi = calculate_bounds(pts)
        self.assertEqual(bounds_multi, [[10.0, 70.0], [30.0, 80.0]])

        # Empty / Invalid
        self.assertIsNone(calculate_bounds(None))
        self.assertIsNone(calculate_bounds([]))
        self.assertIsNone(calculate_bounds([{"lat": "invalid", "lon": "invalid"}]))

    def test_geojson_serialization_and_crs(self):
        pt_feat = create_point_feature(20.0, 78.0, {"name": "Test Event"})
        self.assertIsNotNone(pt_feat)
        self.assertEqual(pt_feat["geometry"]["type"], "Point")
        # GeoJSON RFC 7946 strictly requires [longitude, latitude]
        self.assertEqual(pt_feat["geometry"]["coordinates"], [78.0, 20.0])

        poly_pts = [(10.0, 70.0), (10.0, 72.0), (12.0, 71.0)]
        poly_feat = create_polygon_feature(poly_pts, {"severity": "High"})
        self.assertIsNotNone(poly_feat)
        self.assertEqual(poly_feat["geometry"]["type"], "Polygon")
        self.assertEqual(len(poly_feat["geometry"]["coordinates"][0]), 4)  # Closed ring

        fc = create_feature_collection([pt_feat, poly_feat], include_crs=True)
        self.assertEqual(fc["type"], "FeatureCollection")
        self.assertEqual(len(fc["features"]), 2)
        self.assertEqual(fc["crs"], DEFAULT_CRS)
        self.assertEqual(fc["crs"]["properties"]["name"], "urn:ogc:def:crs:OGC:1.3:CRS84")

    def test_severity_colors(self):
        self.assertEqual(get_severity_color("High"), "#e74c3c")
        self.assertEqual(get_severity_color("low"), "#f1c40f")
        self.assertEqual(get_severity_color("Extreme"), "#8e44ad")
        self.assertEqual(get_severity_color(None), "#95a5a6")

    @unittest.skipUnless(HAS_FOLIUM, "folium not installed")
    def test_build_folium_map_valid_data(self):
        event_loc = {
            "name": "Assam Flood 2024",
            "type": "Flood",
            "lat": 26.2006,
            "lon": 92.9376,
        }
        polygons = [
            {
                "coordinates": [(26.1, 92.8), (26.3, 92.8), (26.2, 93.0)],
                "severity": "High",
                "area_km2": 45.2,
            }
        ]
        hotspots = [
            {"lat": 26.22, "lon": 92.91, "intensity": "Extreme"}
        ]

        folium_map = build_folium_map(
            event_location=event_loc,
            affected_polygons=polygons,
            hotspots=hotspots,
            severity_level="High",
        )

        self.assertIsInstance(folium_map, folium.Map)
        map_html = folium_map.get_root().render()
        self.assertIn("Assam Flood 2024", map_html)
        self.assertIn("Severity Index", map_html)

    @unittest.skipUnless(HAS_FOLIUM, "folium not installed")
    def test_build_folium_map_missing_metadata(self):
        folium_map = build_folium_map(
            event_location={},
            affected_polygons=[],
            hotspots=[],
            severity_level=None,
        )
        self.assertIsInstance(folium_map, folium.Map)
        map_html = folium_map.get_root().render()
        self.assertIn("No valid geospatial coordinates available", map_html)

    @unittest.skipUnless(HAS_FOLIUM, "folium not installed")
    def test_render_map_panel_fallback(self):
        res = render_map_panel(event_location={"lat": 15.0, "lon": 75.0})
        self.assertIsInstance(res, folium.Map)


if __name__ == "__main__":
    unittest.main()
