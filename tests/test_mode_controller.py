"""
Unit tests for NIRVAAN Analysis Mode Controller (detection/mode_controller.py - TASK-020)
"""

import unittest

from detection.mode_controller import (
    AnalysisModeController,
    execute_mode_analysis,
)
from detection.result_contract import DetectionResultContract


class TestAnalysisModeController(unittest.TestCase):
    """Test suite for AnalysisModeController Instant Demo Mode and Live Analyze Mode execution."""

    def setUp(self):
        self.controller = AnalysisModeController()

    def test_instant_demo_mode_flood(self):
        """Verify Instant Demo Mode loads precomputed flood result cleanly with mode tag."""
        contract = self.controller.run_analysis("flood-emilia-romagna-2023", mode="INSTANT_DEMO")

        self.assertIsInstance(contract, DetectionResultContract)
        self.assertEqual(contract.event_id, "flood-emilia-romagna-2023")
        self.assertEqual(contract.status, "success")
        self.assertEqual(contract.event_metadata.get("analysis_mode"), "INSTANT_DEMO")

    def test_instant_demo_mode_wildfire(self):
        """Verify Instant Demo Mode loads precomputed wildfire result cleanly with mode tag."""
        contract = self.controller.run_analysis("wildfire-rhodes-2023", mode="INSTANT_DEMO")

        self.assertIsInstance(contract, DetectionResultContract)
        self.assertEqual(contract.event_id, "wildfire-rhodes-2023")
        self.assertEqual(contract.status, "success")
        self.assertEqual(contract.event_metadata.get("analysis_mode"), "INSTANT_DEMO")

    def test_live_analyze_mode_flood(self):
        """Verify Live Analyze Mode executes live pipeline for flood event with mode tag."""
        contract = self.controller.run_analysis("flood-emilia-romagna-2023", mode="LIVE_ANALYZE")

        self.assertIsInstance(contract, DetectionResultContract)
        self.assertEqual(contract.event_id, "flood-emilia-romagna-2023")
        self.assertEqual(contract.status, "success")
        self.assertEqual(contract.event_metadata.get("analysis_mode"), "LIVE_ANALYZE")

    def test_invalid_mode_raises_value_error(self):
        """Verify invalid mode raises ValueError."""
        with self.assertRaises(ValueError):
            self.controller.run_analysis("flood-emilia-romagna-2023", mode="UNSUPPORTED_MODE")

    def test_missing_demo_artifact_returns_failed_contract(self):
        """Verify missing demo artifact returns structured failed contract."""
        contract = self.controller.run_analysis("missing-dummy-event-999", mode="INSTANT_DEMO")
        self.assertEqual(contract.status, "failed")
        self.assertIn("analysis_mode", contract.event_metadata)

    def test_public_execute_mode_analysis_helper(self):
        """Verify public helper execute_mode_analysis works."""
        contract = execute_mode_analysis("flood-emilia-romagna-2023", mode="INSTANT_DEMO")
        self.assertEqual(contract.status, "success")

    def test_live_analysis_timeout_raises_error(self):
        """Verify live analysis with 0.00001s timeout raises AnalysisTimeoutError."""
        from detection.mode_controller import AnalysisTimeoutError
        controller = AnalysisModeController(timeout_sec=0.00001)
        with self.assertRaises(AnalysisTimeoutError):
            controller.run_analysis("flood-emilia-romagna-2023", mode="LIVE_ANALYZE")


if __name__ == "__main__":
    unittest.main()
