"""
Integration Tests for NIRVAAN REST/JSON API Service Endpoints
"""

import site
import sys
import unittest

# Ensure user site packages are in sys.path
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

from api.server import handle_api_request


class TestAPIServiceEndpoints(unittest.TestCase):

    def test_health_endpoint(self):
        res = handle_api_request("/api/v1/health", method="GET")
        self.assertEqual(res["status_code"], 200)
        self.assertEqual(res["data"]["status"], "HEALTHY")
        self.assertIn("version", res["data"])

    def test_readiness_endpoint(self):
        res = handle_api_request("/api/v1/ready", method="GET")
        self.assertEqual(res["status_code"], 200)
        self.assertEqual(res["data"]["status"], "READY")
        self.assertIn("checks", res["data"])

    def test_disaster_latest_endpoint(self):
        res = handle_api_request("/api/disaster/latest", method="GET")
        self.assertEqual(res["status_code"], 200)
        self.assertIn("type", res["data"])
        self.assertIn("location", res["data"])
        self.assertIn("severity", res["data"])
        self.assertIn("affectedArea", res["data"])
        self.assertEqual(res["data"]["type"], "Flood")
        self.assertIn("Emilia-Romagna", res["data"]["location"])

    def test_disasters_history_endpoint(self):
        res = handle_api_request("/api/disasters", method="GET")
        self.assertEqual(res["status_code"], 200)
        self.assertIsInstance(res["data"], list)
        self.assertGreaterEqual(len(res["data"]), 2)
        types = [d["type"] for d in res["data"]]
        self.assertIn("Flood", types)
        self.assertIn("Wildfire", types)

    def test_satellite_latest_endpoint(self):
        res = handle_api_request("/api/satellite/latest", method="GET")
        self.assertEqual(res["status_code"], 200)
        self.assertIn("beforeImage", res["data"])
        self.assertIn("afterImage", res["data"])
        self.assertIn("event_id", res["data"])

    def test_detect_endpoint_valid_request(self):
        payload = {
            "event": {
                "event_id": "EVT_001",
                "name": "Assam Flood",
                "type": "Flood",
                "lat": 26.2,
                "lon": 92.9
            },
            "thresholds": {"ndwi_threshold": 0.3},
            "dataset_id": "DS_001"
        }
        res = handle_api_request("/api/v1/detect", method="POST", payload=payload)
        self.assertEqual(res["status_code"], 200)
        self.assertEqual(res["data"]["status"], "SUCCESS")
        self.assertEqual(res["data"]["event_id"], "EVT_001")
        self.assertIn("geojson", res["data"])
        self.assertIn("provenance", res["data"])

    def test_detect_endpoint_invalid_metadata(self):
        payload = {
            "event": {"name": "Missing ID and Coords"},
            "thresholds": {"ndwi_threshold": 0.3}
        }
        res = handle_api_request("/api/v1/detect", method="POST", payload=payload)
        self.assertEqual(res["status_code"], 422)
        self.assertEqual(res["data"]["error"], "UNPROCESSABLE_ENTITY")

    def test_analyze_endpoint_valid_request(self):
        payload = {
            "polygons": [[(26.0, 92.0), (26.0, 92.2), (26.2, 92.2), (26.2, 92.0), (26.0, 92.0)]],
            "spectral_severity": "High"
        }
        res = handle_api_request("/api/v1/analyze", method="POST", payload=payload)
        self.assertEqual(res["status_code"], 200)
        self.assertEqual(res["data"]["status"], "SUCCESS")
        self.assertIn("composite_severity", res["data"])
        self.assertEqual(res["data"]["composite_severity"]["status"], "PROTOTYPE")

    def test_report_endpoint(self):
        payload = {
            "event": {"name": "Assam Flood", "type": "Flood"},
            "force_offline": True
        }
        res = handle_api_request("/api/v1/report", method="POST", payload=payload)
        self.assertEqual(res["status_code"], 200)
        self.assertEqual(res["data"]["status"], "SUCCESS")
        self.assertEqual(res["data"]["mode"], "OFFLINE_FALLBACK")
        self.assertIn("report_markdown", res["data"])

    def test_404_not_found(self):
        res = handle_api_request("/api/v1/nonexistent", method="GET")
        self.assertEqual(res["status_code"], 404)
        self.assertEqual(res["data"]["error"], "NOT_FOUND")


if __name__ == "__main__":
    unittest.main()
