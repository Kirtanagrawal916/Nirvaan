"""
Deterministic Unit Tests for NIRVAAN Backend Validation and Secret Sanitization
"""

import site
import sys
import unittest
import numpy as np

# Ensure user site packages are in sys.path
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

from utils.validation import (
    sanitize_log_message,
    validate_event_metadata,
    validate_imagery_input,
    validate_thresholds,
    validate_geojson_output,
)


class TestValidationAndSanitization(unittest.TestCase):

    def test_secret_sanitization(self):
        # API Key sanitization test
        raw_msg = "Connecting to API with api_key='AIzaSy1234567890abcdefghijklmnopqrstuv' and token='sk-abcdef12345678901234567890123456'"
        sanitized = sanitize_log_message(raw_msg)

        self.assertNotIn("AIzaSy1234567890abcdefghijklmnopqrstuv", sanitized)
        self.assertNotIn("sk-abcdef12345678901234567890123456", sanitized)
        self.assertIn("[REDACTED]", sanitized)

    def test_validate_event_metadata_valid(self):
        valid_meta = {
            "event_id": "EVT_ASSAM_2024",
            "name": "Assam Flood 2024",
            "type": "Flood",
            "lat": 26.2006,
            "lon": 92.9376
        }
        is_valid, errors = validate_event_metadata(valid_meta)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_event_metadata_invalid(self):
        # Missing event_id and out-of-bounds coordinates
        invalid_meta = {
            "name": "Invalid Event",
            "type": "Wildfire",
            "lat": 120.0,
            "lon": 92.9376
        }
        is_valid, errors = validate_event_metadata(invalid_meta)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

    def test_validate_imagery_input(self):
        # Valid numpy array
        valid_arr = np.zeros((10, 10), dtype=float)
        is_valid, errors = validate_imagery_input(valid_arr)
        self.assertTrue(is_valid)

        # Invalid array containing NaN
        invalid_arr = np.full((5, 5), fill_value=np.nan)
        is_valid_nan, errors_nan = validate_imagery_input(invalid_arr)
        self.assertFalse(is_valid_nan)
        self.assertIn("NaN or Inf", errors_nan[0])

    def test_validate_thresholds(self):
        # Valid thresholds
        is_valid, errors = validate_thresholds({"ndwi_threshold": 0.3, "dnbr_threshold": 0.2})
        self.assertTrue(is_valid)

        # Out-of-bounds thresholds
        is_valid_invalid, errors_invalid = validate_thresholds({"ndwi_threshold": 5.0})
        self.assertFalse(is_valid_invalid)

    def test_validate_geojson_output(self):
        valid_geojson = {
            "type": "FeatureCollection",
            "features": [{"type": "Feature", "geometry": {"type": "Point", "coordinates": [92.0, 26.0]}, "properties": {}}]
        }
        is_valid, errors = validate_geojson_output(valid_geojson)
        self.assertTrue(is_valid)

        # Invalid GeoJSON type
        is_valid_type, errors_type = validate_geojson_output({"type": "InvalidType"})
        self.assertFalse(is_valid_type)


if __name__ == "__main__":
    unittest.main()
