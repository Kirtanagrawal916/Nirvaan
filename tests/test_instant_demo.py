"""
Unit tests for NIRVAAN Instant Demo Mode (demo/precomputed_results.py - TASK-017)
"""

import tempfile
import unittest
from pathlib import Path

from demo.precomputed_results import generate_precomputed_artifacts, load_demo_result
from detection.result_contract import DetectionResultContract


class TestInstantDemoMode(unittest.TestCase):
    """Test suite for Instant Demo precomputed artifact loading, validation, and error handling."""

    def test_load_demo_result_flood(self):
        """Verify load_demo_result loads valid flood demo result."""
        contract = load_demo_result("flood-emilia-romagna-2023")

        self.assertIsInstance(contract, DetectionResultContract)
        self.assertEqual(contract.event_id, "flood-emilia-romagna-2023")
        self.assertEqual(contract.disaster_type, "flood")
        self.assertEqual(contract.status, "success")
        self.assertIn("affected_area_km2", contract.affected_area)
        self.assertIsNotNone(contract.provenance)

    def test_load_demo_result_wildfire(self):
        """Verify load_demo_result loads valid wildfire demo result."""
        contract = load_demo_result("wildfire-rhodes-2023")

        self.assertIsInstance(contract, DetectionResultContract)
        self.assertEqual(contract.event_id, "wildfire-rhodes-2023")
        self.assertEqual(contract.disaster_type, "wildfire")
        self.assertEqual(contract.status, "success")
        self.assertIn("affected_area_km2", contract.affected_area)
        self.assertIsNotNone(contract.provenance)

    def test_missing_demo_result_raises_error(self):
        """Verify missing demo result in a non-existent directory raises FileNotFoundError."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with self.assertRaises(FileNotFoundError):
                load_demo_result("nonexistent-event-999", precomputed_dir=tmp_dir)

    def test_corrupt_demo_result_raises_value_error(self):
        """Verify corrupt demo result raises ValueError."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            bad_file = tmp_path / "bad-event.json"
            with open(bad_file, "w", encoding="utf-8") as f:
                f.write("{ invalid json syntax ...")

            with self.assertRaises(ValueError):
                load_demo_result("bad-event", precomputed_dir=tmp_path)


if __name__ == "__main__":
    unittest.main()
