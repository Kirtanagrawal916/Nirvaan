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


if __name__ == "__main__":
    unittest.main()
