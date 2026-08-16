"""
Unit tests for NIRVAAN Detection Pipeline (detection/pipeline.py - TASK-016)
"""

import unittest

from detection.pipeline import DetectionPipeline, run_detection
from detection.result_contract import DetectionResultContract


class TestDetectionPipeline(unittest.TestCase):
    """Test suite for DetectionPipeline orchestration, stage error handling, and canonical event execution."""

    def setUp(self):
        self.pipeline = DetectionPipeline()

    def test_complete_flood_pipeline_execution(self):
        """Verify complete pipeline execution on canonical flood event (flood-emilia-romagna-2023)."""
        res = self.pipeline.run("flood-emilia-romagna-2023")

        self.assertIsInstance(res, DetectionResultContract)
        self.assertEqual(res.event_id, "flood-emilia-romagna-2023")
        self.assertEqual(res.disaster_type, "flood")
        self.assertEqual(res.status, "success")

        # Verify all downstream stages populated cleanly
        self.assertIn("affected_area_km2", res.affected_area)
        self.assertIn("severity_level", res.severity)
        self.assertIsInstance(res.hotspots, list)
        self.assertIn("dimensions", res.mask_reference)
        self.assertIsNotNone(res.provenance)

    def test_complete_wildfire_pipeline_execution(self):
        """Verify complete pipeline execution on canonical wildfire event (wildfire-rhodes-2023)."""
        res = self.pipeline.run("wildfire-rhodes-2023")

        self.assertIsInstance(res, DetectionResultContract)
        self.assertEqual(res.event_id, "wildfire-rhodes-2023")
        self.assertEqual(res.disaster_type, "wildfire")
        self.assertEqual(res.status, "success")

        # Verify downstream stages
        self.assertIn("affected_area_km2", res.affected_area)
        self.assertIn("severity_level", res.severity)
        self.assertIsInstance(res.hotspots, list)
        self.assertIn("dimensions", res.mask_reference)
        self.assertIsNotNone(res.provenance)

    def test_invalid_event_id_returns_failed_contract(self):
        """Verify invalid event ID returns a structured failed contract without crashing."""
        res = self.pipeline.run("invalid-dummy-event-999")

        self.assertIsInstance(res, DetectionResultContract)
        self.assertEqual(res.event_id, "invalid-dummy-event-999")
        self.assertEqual(res.status, "failed")
        self.assertGreater(len(res.warnings), 0)

    def test_public_run_detection_helper(self):
        """Verify public helper run_detection executes cleanly."""
        res = run_detection("flood-emilia-romagna-2023")
        self.assertEqual(res.status, "success")


if __name__ == "__main__":
    unittest.main()
