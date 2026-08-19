"""
Integration & Health Verification Tests for NIRVAAN FastAPI Application
"""

import site
import sys
import unittest

user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

try:
    from fastapi.testclient import TestClient
    from api.main import app
    HAS_FASTAPI_TESTCLIENT = True
except ImportError:
    HAS_FASTAPI_TESTCLIENT = False


class TestFastAPIApplication(unittest.TestCase):

    def setUp(self):
        if not HAS_FASTAPI_TESTCLIENT:
            self.skipTest("fastapi or starlette TestClient not installed in current environment")
        self.client = TestClient(app)

    def test_health_check_endpoint(self):
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_cors_headers_present(self):
        response = self.client.get("/api/v1/health", headers={"Origin": "http://localhost:3000"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access-control-allow-origin", response.headers)

    def test_latest_disaster_endpoint(self):
        response = self.client.get("/api/disaster/latest")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("type", data)
        self.assertIn("location", data)
        self.assertIn("confidence", data)
        self.assertIn("severity", data)
        self.assertIn("affectedArea", data)

    def test_disaster_history_endpoint(self):
        response = self.client.get("/api/disasters")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        item = data[0]
        self.assertIn("id", item)
        self.assertIn("type", item)
        self.assertIn("location", item)

    def test_latest_satellite_endpoint(self):
        response = self.client.get("/api/satellite/latest")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("beforeImage", data)
        self.assertIn("afterImage", data)

    def test_static_asset_before_image_accessible(self):
        response = self.client.get("/assets/before.jpg")
        self.assertEqual(response.status_code, 200)
        self.assertIn("image/", response.headers.get("content-type", ""))

    def test_static_asset_after_image_accessible(self):
        response = self.client.get("/assets/after.jpg")
        self.assertEqual(response.status_code, 200)
        self.assertIn("image/", response.headers.get("content-type", ""))

    def test_missing_asset_returns_404(self):
        response = self.client.get("/assets/nonexistent.jpg")
        self.assertEqual(response.status_code, 404)

    def test_path_traversal_rejected(self):
        response = self.client.get("/assets/../config/detection_config.json")
        self.assertIn(response.status_code, [400, 404])


if __name__ == "__main__":
    unittest.main()
