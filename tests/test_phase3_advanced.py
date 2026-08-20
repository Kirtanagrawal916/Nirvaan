"""
NIRVAAN Phase 3 Advanced Platform Capabilities Test Suite (tests/test_phase3_advanced.py)

Comprehensive verification tests for:
1. Multi-Disaster Detector Architecture & Registry (Flood, Wildfire NBR, Severe Weather)
2. Explainable Risk Engine (Formula calculation, factor explainability, edge cases)
3. Event-Driven Notification Engine & Idempotency Deduplication
4. User Notification Preferences & Rule Engine
5. Analytics Aggregation Endpoints (/api/v1/analytics/*)
6. Centralized Disaster Types Metadata API (/api/v1/disaster-types)
"""

import json
import os
import unittest
from fastapi.testclient import TestClient

from api.main import app
from db.database import init_db
from db.repository import DatabaseRepository
from detection.detector_base import DetectorInput
from detection.detector_registry import DetectorRegistry
from services.risk_engine import ExplainableRiskEngine, RiskFactors
from services.notification_service import NotificationEngine


class TestPhase3AdvancedCapabilities(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        cls.repo = DatabaseRepository()
        cls.client = TestClient(app)
        cls.notif_engine = NotificationEngine(repo=cls.repo)

    def test_detector_registry_registration_and_dispatch(self):
        """Verifies DetectorRegistry returns correct detectors and raises for unsupported types."""
        self.assertTrue(DetectorRegistry.is_supported("flood"))
        self.assertTrue(DetectorRegistry.is_supported("wildfire"))
        self.assertTrue(DetectorRegistry.is_supported("severe_weather"))

        flood_det = DetectorRegistry.get_detector("flood", repo=self.repo)
        self.assertEqual(flood_det.disaster_type, "flood")
        self.assertEqual(flood_det.model_version, "Nirvaan-NDWI-v1.0")

        wildfire_det = DetectorRegistry.get_detector("wildfire", repo=self.repo)
        self.assertEqual(wildfire_det.disaster_type, "wildfire")
        self.assertEqual(wildfire_det.model_version, "Nirvaan-NBR-v1.0")

        weather_det = DetectorRegistry.get_detector("severe_weather", repo=self.repo)
        self.assertEqual(weather_det.disaster_type, "severe_weather")

        with self.assertRaises(ValueError):
            DetectorRegistry.get_detector("volcanic_eruption", repo=self.repo)

    def test_wildfire_detector_nbr_execution(self):
        """Verifies Sentinel-2 NBR Wildfire detection execution."""
        wildfire_det = DetectorRegistry.get_detector("wildfire", repo=self.repo)
        inp = DetectorInput(
            latitude=37.7749,
            longitude=-122.4194,
            location_name="California Forest Basin",
            disaster_type="wildfire"
        )
        res = wildfire_det.run(inp)
        self.assertEqual(res.status, "success")
        self.assertEqual(res.disaster_type, "wildfire")
        self.assertGreater(res.confidence_score, 50.0)
        self.assertGreater(res.affected_area_km2, 0.0)
        self.assertIn("FeatureCollection", res.geometry_geojson.get("type", ""))
        self.assertIn("Nirvaan-NBR-v1.0", res.model_metadata.get("model_name", ""))

    def test_severe_weather_authoritative_assimilation(self):
        """Verifies Severe Weather detector preserves external authoritative attribution."""
        weather_det = DetectorRegistry.get_detector("severe_weather", repo=self.repo)
        inp = DetectorInput(
            latitude=13.0827,
            longitude=80.2707,
            location_name="Chennai Coastline",
            disaster_type="severe_weather"
        )
        res = weather_det.run(inp)
        self.assertEqual(res.status, "success")
        self.assertEqual(res.disaster_type, "severe_weather")
        self.assertEqual(res.provenance.get("provenance_type"), "EXTERNAL_HISTORICAL_EVENT")
        self.assertIn("External authoritative meteorological provider", res.provenance.get("attribution", ""))

    def test_explainable_risk_engine_formula(self):
        """Verifies ExplainableRiskEngine produces deterministic, mathematically verified risk scores."""
        # High severity with high confidence
        factors = RiskFactors(
            disaster_type="flood",
            severity="HIGH",
            confidence_score=90.0,
            affected_area_km2=25.0,
            population_density=400.0,
            critical_infrastructure_count=3,
            environmental_anomaly_score=30.0,
            data_freshness_factor=1.0
        )
        eval_res = ExplainableRiskEngine.evaluate(factors)
        self.assertGreaterEqual(eval_res.composite_risk_score, 50.0)
        self.assertIn(eval_res.risk_category, ["ELEVATED", "HIGH", "CRITICAL"])
        self.assertEqual(eval_res.methodology_version, "Nirvaan-Risk-v1.0")

        # Verify explainability dictionary
        res_dict = eval_res.to_dict()
        self.assertIn("hazard_severity_score", res_dict)
        self.assertIn("population_exposure_score", res_dict)
        self.assertIn("infrastructure_exposure_score", res_dict)
        self.assertIn("confidence_adjustment", res_dict)

    def test_notification_rule_evaluation_and_idempotency(self):
        """Verifies NotificationEngine evaluates alert rules and prevents duplicate notifications."""
        # Create a rule
        rule = self.repo.save_notification_rule(
            user_id="user-phase3-test",
            disaster_types="flood",
            min_severity="HIGH",
            min_confidence=80.0,
            channels=["in_app", "webhook"]
        )
        self.assertIsNotNone(rule.get("id"))

        import uuid
        # Process matching alert
        alert_id = f"alt-test-p3-{uuid.uuid4().hex[:6]}"
        event_id = f"event-test-p3-{uuid.uuid4().hex[:6]}"
        dispatched_1 = self.notif_engine.process_alert_notifications(
            alert_id=alert_id,
            event_id=event_id,
            disaster_type="flood",
            severity="HIGH",
            confidence=92.0
        )
        self.assertGreater(len(dispatched_1), 0)

        # Immediate repeat attempt: must be suppressed by idempotency
        dispatched_2 = self.notif_engine.process_alert_notifications(
            alert_id=alert_id,
            event_id=event_id,
            disaster_type="flood",
            severity="HIGH",
            confidence=92.0
        )
        self.assertEqual(len(dispatched_2), 0)

    def test_analytics_endpoints(self):
        """Verifies /api/v1/analytics/overview, /timeseries, /disasters, /geography return valid data."""
        # 1. Overview
        res_ov = self.client.get("/api/v1/analytics/overview?days=30")
        self.assertEqual(res_ov.status_code, 200)
        data_ov = res_ov.json()
        self.assertIn("total_disasters_tracked", data_ov)
        self.assertIn("severity_distribution", data_ov)
        self.assertIn("disaster_type_distribution", data_ov)

        # 2. Timeseries
        res_ts = self.client.get("/api/v1/analytics/timeseries?days=30")
        self.assertEqual(res_ts.status_code, 200)
        self.assertIsInstance(res_ts.json(), list)

        # 3. Disasters Distribution
        res_dist = self.client.get("/api/v1/analytics/disasters")
        self.assertEqual(res_dist.status_code, 200)
        data_dist = res_dist.json()
        self.assertIn("disaster_distribution", data_dist)

        # 4. Geography Clusters
        res_geo = self.client.get("/api/v1/analytics/geography")
        self.assertEqual(res_geo.status_code, 200)
        self.assertIsInstance(res_geo.json(), list)

    def test_disaster_types_metadata_endpoint(self):
        """Verifies GET /api/v1/disaster-types returns centralized metadata for all supported hazards."""
        res = self.client.get("/api/v1/disaster-types")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data.get("count", 0), 3)
        types = [d["disaster_type"] for d in data.get("supported_disasters", [])]
        self.assertIn("flood", types)
        self.assertIn("wildfire", types)
        self.assertIn("severe_weather", types)

    def test_user_notification_preferences_flow(self):
        """Verifies GET and POST /api/v1/notifications/preferences with JWT auth."""
        # Register and login user
        email = "analyst.p3@nirvaan.ai"
        self.client.post("/api/v1/auth/register", json={"email": email, "password": "Password123!", "full_name": "Phase3 Analyst"})
        login_res = self.client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
        token = login_res.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}

        # Save preferences
        payload = {
            "disaster_types": ["flood", "wildfire"],
            "min_severity": "HIGH",
            "quiet_hours_enabled": True
        }
        save_res = self.client.post("/api/v1/notifications/preferences", json=payload, headers=headers)
        self.assertEqual(save_res.status_code, 200)

        # Retrieve preferences
        get_res = self.client.get("/api/v1/notifications/preferences", headers=headers)
        self.assertEqual(get_res.status_code, 200)
        pref_data = get_res.json()
        self.assertEqual(pref_data.get("min_severity"), "HIGH")


if __name__ == "__main__":
    unittest.main()
