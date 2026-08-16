"""
End-to-End Validation Test Suite for NIRVAAN Disaster Detection Pipeline (TASK-018)
"""

import time
import unittest

from demo.precomputed_results import load_demo_result
from detection.pipeline import DetectionPipeline, run_detection
from detection.result_contract import DetectionResultContract


class TestEndToEndPipeline(unittest.TestCase):
    """
    Comprehensive end-to-end validation test suite verifying live processing,
    instant demo mode, determinism, performance, and schema compatibility.
    """

    def setUp(self):
        self.pipeline = DetectionPipeline()

    def test_e2e_flood_live_pipeline(self):
        """Verify complete live flood pipeline execution from raw rasters to contract."""
        start_time = time.time()
        res = run_detection("flood-emilia-romagna-2023", mode="LIVE_ANALYZE")
        duration = time.time() - start_time

        self.assertIsInstance(res, DetectionResultContract)
        self.assertEqual(res.event_id, "flood-emilia-romagna-2023")
        self.assertEqual(res.disaster_type, "flood")
        self.assertEqual(res.status, "success")
        self.assertIn("affected_area_km2", res.affected_area)
        self.assertIn("severity_level", res.severity)
        self.assertIsInstance(res.hotspots, list)
        self.assertIn("source_provider", res.provenance)
        self.assertLess(duration, 5.0, "Live flood pipeline execution exceeded 5.0 second threshold")

    def test_e2e_wildfire_live_pipeline(self):
        """Verify complete live wildfire pipeline execution from raw rasters to contract."""
        start_time = time.time()
        res = run_detection("wildfire-rhodes-2023", mode="LIVE_ANALYZE")
        duration = time.time() - start_time

        self.assertIsInstance(res, DetectionResultContract)
        self.assertEqual(res.event_id, "wildfire-rhodes-2023")
        self.assertEqual(res.disaster_type, "wildfire")
        self.assertEqual(res.status, "success")
        self.assertIn("affected_area_km2", res.affected_area)
        self.assertIn("severity_level", res.severity)
        self.assertIsInstance(res.hotspots, list)
        self.assertIn("source_provider", res.provenance)
        self.assertLess(duration, 30.0, "Live wildfire pipeline execution exceeded 30.0 second threshold")

    def test_e2e_determinism(self):
        """Verify identical repeated executions produce deterministic metrics and hotspots."""
        run1 = run_detection("flood-emilia-romagna-2023")
        run2 = run_detection("flood-emilia-romagna-2023")

        self.assertEqual(run1.affected_area["affected_pixel_count"], run2.affected_area["affected_pixel_count"])
        self.assertEqual(run1.affected_area["affected_area_m2"], run2.affected_area["affected_area_m2"])
        self.assertEqual(run1.severity["severity_level"], run2.severity["severity_level"])
        self.assertEqual(len(run1.hotspots), len(run2.hotspots))

    def test_live_vs_demo_contract_compatibility(self):
        """Verify Live and Instant Demo results conform to identical TASK-015 contract schema."""
        live_res = run_detection("flood-emilia-romagna-2023", mode="LIVE_ANALYZE")
        demo_res = load_demo_result("flood-emilia-romagna-2023")

        self.assertEqual(live_res.event_id, demo_res.event_id)
        self.assertEqual(live_res.disaster_type, demo_res.disaster_type)
        self.assertEqual(live_res.status, demo_res.status)
        self.assertEqual(
            live_res.affected_area["affected_pixel_count"],
            demo_res.affected_area["affected_pixel_count"],
        )
        self.assertEqual(
            live_res.severity["severity_level"],
            demo_res.severity["severity_level"],
        )

    def test_invalid_and_error_cases(self):
        """Verify pipeline handles invalid inputs and error cases cleanly."""
        res_invalid = run_detection("nonexistent-invalid-event")
        self.assertEqual(res_invalid.status, "failed")
        self.assertGreater(len(res_invalid.warnings), 0)


if __name__ == "__main__":
    unittest.main()
