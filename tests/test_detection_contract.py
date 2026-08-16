"""
Unit tests for NIRVAAN Detection Result Contract (detection/result_contract.py - TASK-015)
"""

import json
import unittest

from detection.result_contract import (
    DetectionResultContract,
    build_detection_result_contract,
)


class TestDetectionResultContract(unittest.TestCase):
    """Test suite for DetectionResultContract validation, serialization, error states, and canonical integration."""

    def test_valid_complete_contract_serialization(self):
        """Verify contract serialization to dict and JSON."""
        contract = DetectionResultContract(
            event_id="test-event-01",
            disaster_type="flood",
            status="success",
            timestamp="2026-08-16T12:00:00Z",
            event_metadata={"name": "Test Flood"},
            detection_summary={"method": "NDWI"},
            affected_area={"affected_area_km2": 1.5},
            severity={"severity_level": "MODERATE"},
            hotspots=[{"hotspot_id": "hotspot-01"}],
            mask_reference={"dimensions": [100, 100]},
            provenance={"source": "Copernicus"},
        )

        d = contract.to_dict()
        self.assertEqual(d["event_id"], "test-event-01")
        self.assertEqual(d["status"], "success")

        json_str = contract.to_json()
        parsed = json.loads(json_str)
        self.assertEqual(parsed["disaster_type"], "flood")

        reconstructed = DetectionResultContract.from_dict(parsed)
        self.assertEqual(reconstructed.event_id, "test-event-01")

    def test_invalid_disaster_type_raises_value_error(self):
        """Verify invalid disaster type raises ValueError."""
        with self.assertRaises(ValueError):
            DetectionResultContract(
                event_id="test-bad-disaster",
                disaster_type="earthquake_unsupported",
                status="success",
                timestamp="2026-08-16T12:00:00Z",
                event_metadata={},
                detection_summary={},
                affected_area={},
                severity={},
                hotspots=[],
                mask_reference={},
                provenance={},
            )

    def test_invalid_status_raises_value_error(self):
        """Verify invalid status raises ValueError."""
        with self.assertRaises(ValueError):
            DetectionResultContract(
                event_id="test-bad-status",
                disaster_type="flood",
                status="super_successful_unsupported",
                timestamp="2026-08-16T12:00:00Z",
                event_metadata={},
                detection_summary={},
                affected_area={},
                severity={},
                hotspots=[],
                mask_reference={},
                provenance={},
            )

    def test_failed_contract_creation(self):
        """Verify build_detection_result_contract creates clean failed contract for unknown event."""
        contract = build_detection_result_contract("nonexistent-dummy-event-999")
        self.assertEqual(contract.status, "failed")
        self.assertGreater(len(contract.warnings), 0)

    def test_canonical_flood_contract_validation(self):
        """Verify end-to-end pipeline execution on canonical flood event (flood-emilia-romagna-2023)."""
        contract = build_detection_result_contract("flood-emilia-romagna-2023")

        self.assertEqual(contract.event_id, "flood-emilia-romagna-2023")
        self.assertEqual(contract.disaster_type, "flood")
        self.assertEqual(contract.status, "success")
        self.assertIn("affected_area_km2", contract.affected_area)
        self.assertIn("severity_level", contract.severity)
        self.assertIn("provenance", contract.to_dict())

        # Test serializability
        json_output = contract.to_json()
        self.assertIn("flood-emilia-romagna-2023", json_output)

    def test_canonical_wildfire_contract_validation(self):
        """Verify end-to-end pipeline execution on canonical wildfire event (wildfire-rhodes-2023)."""
        contract = build_detection_result_contract("wildfire-rhodes-2023")

        self.assertEqual(contract.event_id, "wildfire-rhodes-2023")
        self.assertEqual(contract.disaster_type, "wildfire")
        self.assertEqual(contract.status, "success")
        self.assertIn("affected_area_km2", contract.affected_area)
        self.assertIn("severity_level", contract.severity)
        self.assertIn("provenance", contract.to_dict())

        # Test serializability
        json_output = contract.to_json()
        self.assertIn("wildfire-rhodes-2023", json_output)


if __name__ == "__main__":
    unittest.main()
