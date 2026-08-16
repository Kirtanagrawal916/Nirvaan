"""
Unit tests for NIRVAAN Dataset Loader (data/loader.py)
"""

import json
import tempfile
import unittest
from pathlib import Path

from data.event_schema import UnsupportedDisasterTypeError
from data.loader import (
    DatasetCatalogError,
    DatasetLoader,
    EventNotFoundError,
    MissingFileError,
    load_event,
)


class TestDatasetLoader(unittest.TestCase):
    """Test suite for DatasetLoader functionality and error handling."""

    def setUp(self):
        self.loader = DatasetLoader(verify_files=True)

    def test_canonical_flood_event_loads(self):
        """Verify canonical flood event (flood-emilia-romagna-2023) loads cleanly."""
        event = self.loader.load_event("flood-emilia-romagna-2023")
        self.assertEqual(event.event_id, "flood-emilia-romagna-2023")
        self.assertEqual(event.disaster_type, "flood")
        self.assertEqual(event.CRS, "EPSG:32632 (WGS 84 / UTM zone 32N)")
        self.assertEqual(event.resolution_m, 10.0)
        self.assertEqual(event.before_date, "2023-05-04")
        self.assertEqual(event.after_date, "2023-05-19")
        self.assertTrue(Path(event.before_image).exists())
        self.assertTrue(Path(event.after_image).exists())

    def test_canonical_wildfire_event_loads(self):
        """Verify canonical wildfire event (wildfire-rhodes-2023) loads cleanly."""
        event = self.loader.load_event("wildfire-rhodes-2023")
        self.assertEqual(event.event_id, "wildfire-rhodes-2023")
        self.assertEqual(event.disaster_type, "wildfire")
        self.assertEqual(event.CRS, "EPSG:32635 (WGS 84 / UTM zone 35N)")
        self.assertEqual(event.resolution_m, 10.0)
        self.assertEqual(event.before_date, "2023-07-13")
        self.assertEqual(event.after_date, "2023-07-28")
        self.assertTrue(Path(event.before_image).exists())
        self.assertTrue(Path(event.after_image).exists())

    def test_unknown_event_id_fails(self):
        """Verify requesting non-existent event_id raises EventNotFoundError."""
        with self.assertRaises(EventNotFoundError):
            self.loader.load_event("non-existent-event-999")

    def test_missing_catalog_file_fails(self):
        """Verify specifying non-existent catalog path raises DatasetCatalogError."""
        bad_loader = DatasetLoader(catalog_path="data/non_existent_catalog.json")
        with self.assertRaises(DatasetCatalogError):
            bad_loader.load_event("flood-emilia-romagna-2023")

    def test_unsupported_disaster_type_in_catalog_fails(self):
        """Verify catalog entry with unsupported disaster type fails."""
        bad_catalog_data = {
            "canonical_events": [
                {
                    "event_id": "bad-tsunami-01",
                    "disaster_type": "tsunami",
                    "location_name": "Coast",
                    "before_date": "2023-01-01",
                    "after_date": "2023-01-02",
                    "source": "Test",
                    "coordinate_reference_system": "EPSG:4326",
                    "resolution_m": 10.0,
                    "available_bands": ["B01"],
                    "local_paths": {
                        "before_dir": "data/canonical/flood/before",
                        "after_dir": "data/canonical/flood/after",
                    },
                }
            ]
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
            json.dump(bad_catalog_data, tmp)
            tmp_path = tmp.name

        loader = DatasetLoader(catalog_path=tmp_path, verify_files=False)
        with self.assertRaises(UnsupportedDisasterTypeError):
            loader.load_event("bad-tsunami-01")

    def test_missing_local_file_fails_verification(self):
        """Verify missing local dataset paths raise MissingFileError when verify_files=True."""
        bad_catalog_data = {
            "canonical_events": [
                {
                    "event_id": "missing-path-event",
                    "disaster_type": "flood",
                    "location_name": "Test Location",
                    "before_date": "2023-05-04",
                    "after_date": "2023-05-19",
                    "source": "Test Source",
                    "coordinate_reference_system": "EPSG:32632",
                    "resolution_m": 10.0,
                    "available_bands": ["B03", "B08"],
                    "local_paths": {
                        "before_dir": "data/non_existent_folder_xyz/before",
                        "after_dir": "data/non_existent_folder_xyz/after",
                    },
                }
            ]
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
            json.dump(bad_catalog_data, tmp)
            tmp_path = tmp.name

        loader = DatasetLoader(catalog_path=tmp_path, verify_files=True)
        with self.assertRaises(MissingFileError):
            loader.load_event("missing-path-event")

    def test_global_helper_load_event(self):
        """Verify public API load_event() helper functions correctly."""
        event = load_event("flood-emilia-romagna-2023")
        self.assertEqual(event.event_id, "flood-emilia-romagna-2023")


if __name__ == "__main__":
    unittest.main()
