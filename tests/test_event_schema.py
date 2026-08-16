"""
Unit tests for NIRVAAN Disaster Event Schema (data/event_schema.py)
"""

import unittest
from pathlib import Path

from data.event_schema import (
    DisasterEvent,
    EventValidationError,
    UnsupportedDisasterTypeError,
)


class TestDisasterEventSchema(unittest.TestCase):
    """Test suite for DisasterEvent schema creation and validation rules."""

    def setUp(self):
        self.valid_flood_dict = {
            "event_id": "test-flood-01",
            "disaster_type": "flood",
            "location_name": "Test Location, Italy",
            "latitude": 44.4178,
            "longitude": 12.2035,
            "before_image": "data/canonical/flood/before",
            "after_image": "data/canonical/flood/after",
            "before_date": "2023-05-04",
            "after_date": "2023-05-19",
            "source": "Copernicus Data Space Ecosystem",
            "CRS": "EPSG:32632",
            "resolution_m": 10.0,
            "available_bands": ["B02", "B03", "B04", "B08"],
            "product_id": "S2B_TEST_PRODUCT_ID",
            "source_url": "https://dataspace.copernicus.eu/",
        }

        self.valid_wildfire_dict = {
            "event_id": "test-wildfire-01",
            "disaster_type": "wildfire",
            "location_name": "Rhodes Island, Greece",
            "latitude": 36.1700,
            "longitude": 27.9400,
            "before_image": "data/canonical/wildfire/before",
            "after_image": "data/canonical/wildfire/after",
            "before_date": "2023-07-13",
            "after_date": "2023-07-28",
            "source": "Copernicus EMS",
            "CRS": "EPSG:32635",
            "resolution_m": 10.0,
            "available_bands": ["B04", "B08", "B11", "B12"],
            "product_id": "S2B_WILDFIRE_TEST_ID",
        }

    def test_valid_flood_schema_instantiation(self):
        """Verify valid flood event instantiates and validates cleanly."""
        event = DisasterEvent.from_dict(self.valid_flood_dict)
        self.assertEqual(event.event_id, "test-flood-01")
        self.assertEqual(event.disaster_type, "flood")
        self.assertEqual(event.latitude, 44.4178)
        self.assertEqual(event.longitude, 12.2035)
        self.assertEqual(event.CRS, "EPSG:32632")
        self.assertEqual(event.resolution_m, 10.0)
        self.assertIn("B08", event.available_bands)

    def test_valid_wildfire_schema_instantiation(self):
        """Verify valid wildfire event instantiates and validates cleanly."""
        event = DisasterEvent.from_dict(self.valid_wildfire_dict)
        self.assertEqual(event.event_id, "test-wildfire-01")
        self.assertEqual(event.disaster_type, "wildfire")
        self.assertEqual(event.CRS, "EPSG:32635")
        self.assertIn("B12", event.available_bands)

    def test_unsupported_disaster_type_fails(self):
        """Verify unsupported disaster type raises UnsupportedDisasterTypeError."""
        bad_dict = dict(self.valid_flood_dict)
        bad_dict["disaster_type"] = "earthquake"
        with self.assertRaises(UnsupportedDisasterTypeError):
            DisasterEvent.from_dict(bad_dict)

    def test_invalid_latitude_range_fails(self):
        """Verify out-of-range latitude fails validation."""
        bad_dict = dict(self.valid_flood_dict)
        bad_dict["latitude"] = 105.0
        with self.assertRaises(EventValidationError):
            DisasterEvent.from_dict(bad_dict)

    def test_invalid_date_format_fails(self):
        """Verify bad date string format fails validation."""
        bad_dict = dict(self.valid_flood_dict)
        bad_dict["before_date"] = "04-05-2023"  # DD-MM-YYYY instead of YYYY-MM-DD
        with self.assertRaises(EventValidationError):
            DisasterEvent.from_dict(bad_dict)

    def test_missing_required_field_fails(self):
        """Verify missing CRS or resolution fails validation."""
        bad_dict = dict(self.valid_flood_dict)
        bad_dict["CRS"] = ""
        with self.assertRaises(EventValidationError):
            DisasterEvent.from_dict(bad_dict)

    def test_provenance_fields_preserved(self):
        """Verify provenance fields (source, product_id, source_url) are retained."""
        event = DisasterEvent.from_dict(self.valid_flood_dict)
        dict_output = event.to_dict()
        self.assertEqual(dict_output["source"], "Copernicus Data Space Ecosystem")
        self.assertEqual(dict_output["product_id"], "S2B_TEST_PRODUCT_ID")
        self.assertEqual(dict_output["source_url"], "https://dataspace.copernicus.eu/")


if __name__ == "__main__":
    unittest.main()
