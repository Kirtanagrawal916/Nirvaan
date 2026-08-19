"""
Unit & Integration Tests for NIRVAAN One-Click SITREP Flow

Tests /api/v1/report endpoint, report serialization, structured report_json fields,
canonical event enrichment, data provenance disclosure, and error contracts.
"""

import unittest
from typing import Any, Dict

from api.server import handle_report_endpoint
from reports.situation_report import (
    generate_situation_report,
    build_structured_report_json,
    enrich_payload_from_canonical_event
)


class TestSitrepFlow(unittest.TestCase):

    def test_canonical_flood_report_generation(self):
        """Test report generation for flood-emilia-romagna-2023 canonical event."""
        payload = {"event_id": "flood-emilia-romagna-2023"}
        response = handle_report_endpoint(payload)
        self.assertEqual(response["status_code"], 200)

        data = response["data"]
        self.assertEqual(data["status"], "SUCCESS")
        self.assertIn("data_provenance", data)
        self.assertIn("report_markdown", data)
        self.assertIn("report_json", data)

        rjson = data["report_json"]
        self.assertEqual(rjson["event_id"], "flood-emilia-romagna-2023")
        self.assertIn("Flood", rjson["disaster_type"])
        self.assertIn("severity", rjson)
        self.assertIn("affected_area", rjson)
        self.assertIn("population_exposure", rjson)
        self.assertIn("infrastructure_impact", rjson)
        self.assertIn("recommendations", rjson)
        self.assertIsInstance(rjson["recommendations"], list)
        self.assertGreater(len(rjson["recommendations"]), 0)

    def test_canonical_wildfire_report_generation(self):
        """Test report generation for wildfire-rhodes-2023 canonical event."""
        payload = {"event_id": "wildfire-rhodes-2023"}
        response = handle_report_endpoint(payload)
        self.assertEqual(response["status_code"], 200)

        data = response["data"]
        self.assertEqual(data["status"], "SUCCESS")
        self.assertIn("data_provenance", data)
        self.assertIn("report_markdown", data)

        rjson = data["report_json"]
        self.assertEqual(rjson["event_id"], "wildfire-rhodes-2023")
        self.assertIn("Wildfire", rjson["disaster_type"])
        self.assertIn("severity", rjson)
        self.assertIn("recommendations", rjson)

    def test_custom_event_payload_sitrep(self):
        """Test report generation for custom event payload."""
        custom_payload = {
            "event": {
                "event_id": "EVT_CUSTOM_99",
                "event_name": "Test Quake Event",
                "disaster_type": "Earthquake",
                "location_name": "Test City",
                "latitude": 37.7,
                "longitude": -122.4,
                "data_provenance": "REAL_SATELLITE_DATA"
            },
            "spectral_data": {
                "sensor": "Sentinel-1 SAR",
                "before_date": "2024-01-01",
                "after_date": "2024-01-05"
            },
            "severity_result": {
                "impact_score": 78.5,
                "impact_band": "High"
            },
            "population_impact": {
                "status": "SUCCESS",
                "estimated_affected_population": 45000
            },
            "data_provenance": "REAL_SATELLITE_DATA"
        }
        res = handle_report_endpoint(custom_payload)
        self.assertEqual(res["status_code"], 200)
        data = res["data"]
        self.assertEqual(data["data_provenance"], "REAL_SATELLITE_DATA")

        rjson = data["report_json"]
        self.assertEqual(rjson["event_id"], "EVT_CUSTOM_99")
        self.assertEqual(rjson["severity"]["impact_score"], 78.5)
        self.assertEqual(rjson["population_exposure"]["estimated_affected_population"], 45000)

    def test_invalid_payload_error_handling(self):
        """Test 400 BAD_REQUEST response when payload is non-dict."""
        res = handle_report_endpoint(None)
        self.assertEqual(res["status_code"], 400)
        data = res["data"]
        self.assertEqual(data["status"], "error")
        self.assertEqual(data["code"], "BAD_REQUEST")

    def test_data_provenance_preserved_in_report(self):
        """Confirm data_provenance is surfaced in report response."""
        result = generate_situation_report({"event_id": "flood-emilia-romagna-2023"})
        self.assertIn("data_provenance", result)
        self.assertIn(result["data_provenance"], ["REAL_SATELLITE_DATA", "SYNTHETIC_FALLBACK"])
        self.assertEqual(result["report_json"]["data_provenance"], result["data_provenance"])


if __name__ == "__main__":
    unittest.main()
