"""
Unit tests for NIRVAAN Analysis State Manager (analysis/state_manager.py - TASK-019)
"""

import unittest

from analysis.state_manager import (
    AnalysisState,
    get_cached_detection_result,
    get_or_create_analysis_state,
)
from detection.result_contract import DetectionResultContract


class TestAnalysisStateManager(unittest.TestCase):
    """Test suite for AnalysisState state preservation, event switching, caching, and mode behavior."""

    def setUp(self):
        self.state = AnalysisState()

    def test_default_state_initialization(self):
        """Verify default state values."""
        self.assertEqual(self.state.selected_event_id, "flood-emilia-romagna-2023")
        self.assertEqual(self.state.selected_mode, "INSTANT_DEMO")
        self.assertIsNone(self.state.current_result)
        self.assertEqual(self.state.ui_stage, "DETECT")
        self.assertFalse(self.state.is_analyzing)

    def test_set_event_resets_event_specific_state(self):
        """Verify switching events resets result and stage while keeping mode."""
        self.state.ui_stage = "MAP"
        self.state.error_message = "Previous error"
        self.state.set_mode("LIVE_ANALYZE")

        self.state.set_event("wildfire-rhodes-2023")

        self.assertEqual(self.state.selected_event_id, "wildfire-rhodes-2023")
        self.assertEqual(self.state.selected_mode, "LIVE_ANALYZE")  # Preserved
        self.assertEqual(self.state.ui_stage, "DETECT")            # Reset
        self.assertIsNone(self.state.error_message)               # Reset

    def test_set_mode_validation(self):
        """Verify set_mode accepts INSTANT_DEMO / LIVE_ANALYZE and rejects invalid mode."""
        self.state.set_mode("live_analyze")
        self.assertEqual(self.state.selected_mode, "LIVE_ANALYZE")

        with self.assertRaises(ValueError):
            self.state.set_mode("unsupported_mode_999")

    def test_get_or_create_analysis_state_with_dict(self):
        """Verify get_or_create_analysis_state initializes state inside dictionary."""
        mock_session = {}
        st1 = get_or_create_analysis_state(mock_session)
        self.assertIsInstance(st1, AnalysisState)
        self.assertIn("nirvaan_analysis_state", mock_session)

        # Second call returns same object
        st2 = get_or_create_analysis_state(mock_session)
        self.assertIs(st1, st2)

    def test_get_cached_detection_result_instant_demo(self):
        """Verify get_cached_detection_result returns valid precomputed contract in INSTANT_DEMO mode."""
        contract = get_cached_detection_result("flood-emilia-romagna-2023", mode="INSTANT_DEMO")

        self.assertIsInstance(contract, DetectionResultContract)
        self.assertEqual(contract.event_id, "flood-emilia-romagna-2023")
        self.assertEqual(contract.status, "success")


if __name__ == "__main__":
    unittest.main()
