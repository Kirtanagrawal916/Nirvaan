"""
Deterministic Unit Tests for NIRVAAN AI Situation Report Generation & Offline Fallback
"""

import site
import sys
import unittest

# Ensure user site packages are in sys.path
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

from reports.situation_report import (
    serialize_evidence_payload,
    generate_fallback_situation_report,
    generate_situation_report,
    PROHIBITED_TERMS,
)


class TestSituationReportGeneration(unittest.TestCase):

    def test_serialize_evidence_payload(self):
        event_info = {
            "event_id": "EVT_ASSAM_2024",
            "name": "Assam Flood 2024",
            "type": "Flood",
            "location_name": "Assam AOI",
            "lat": 26.2006,
            "lon": 92.9376,
        }
        spectral_data = {
            "sensor": "Sentinel-2 Level-2A",
            "index_name": "NDWI",
            "before_date": "2024-05-10",
            "after_date": "2024-05-20",
        }
        risk_zones = [{"zone_type": "core"}, {"zone_type": "buffer_moderate"}]
        population_impact = {"status": "SUCCESS", "estimated_affected_population": 4500}
        infra_impact = {
            "status": "SUCCESS",
            "impacted_infrastructure": [{"name": "District Hospital", "category": "hospital", "distance_km": 0.6}],
            "advisory_statements": ["Hospital ('District Hospital') within 0.6 km — field verification recommended."]
        }
        severity_result = {"impact_score": 68.5, "impact_band": "High"}

        payload = serialize_evidence_payload(
            event_info, spectral_data, risk_zones, population_impact, infra_impact, severity_result
        )

        self.assertEqual(payload["event"]["event_id"], "EVT_ASSAM_2024")
        self.assertEqual(payload["spectral_evidence"]["index_name"], "NDWI")
        self.assertEqual(payload["spatial_analytics"]["total_risk_zones"], 2)
        self.assertEqual(payload["population_exposure"]["estimated_affected_population"], 4500)
        self.assertEqual(payload["composite_severity"]["impact_score"], 68.5)

    def test_generate_fallback_situation_report_full_evidence(self):
        event_info = {"name": "Assam Flood 2024", "type": "Flood", "location_name": "Assam", "lat": 26.20, "lon": 92.93}
        spectral_data = {"sensor": "Sentinel-2", "before_date": "2024-05-10", "after_date": "2024-05-20"}
        pop_impact = {"status": "SUCCESS", "estimated_affected_population": 4500}
        infra_impact = {
            "status": "SUCCESS",
            "advisory_statements": ["Hospital ('District Hospital') within 0.6 km — field verification recommended."]
        }
        severity_result = {"impact_score": 68.5, "impact_band": "High"}

        payload = serialize_evidence_payload(event_info, spectral_data, [], pop_impact, infra_impact, severity_result)
        report_md = generate_fallback_situation_report(payload)

        self.assertIn("NIRVAAN Situation Report: Assam Flood 2024", report_md)
        self.assertIn("68.5/100", report_md)
        self.assertIn("4,500", report_md)
        self.assertIn("District Hospital", report_md)
        self.assertIn("ESTIMATE", report_md)
        self.assertIn("PROTOTYPE", report_md)

    def test_generate_fallback_situation_report_missing_evidence(self):
        # Empty/missing evidence payload
        payload = serialize_evidence_payload({}, {}, [], {}, {}, {})
        report_md = generate_fallback_situation_report(payload)

        self.assertIsNotNone(report_md)
        self.assertIn("Executive Situation Summary", report_md)
        self.assertIn("Data Provenance & Limitations", report_md)
        self.assertIn("unavailable or unassessed", report_md)

    def test_prohibited_terms_absence(self):
        event_info = {"name": "Assam Flood 2024", "type": "Flood"}
        payload = serialize_evidence_payload(event_info)
        report_md = generate_fallback_situation_report(payload).lower()

        # Strictly verify no forbidden terms are present in output report
        self.assertNotIn("casualty", report_md)
        self.assertNotIn("fatalities", report_md)
        self.assertNotIn("evacuation order", report_md)
        self.assertNotIn("weather forecast", report_md)
        self.assertNotIn("road closure", report_md)

    def test_generate_situation_report_offline_mode(self):
        event_info = {"name": "Assam Flood 2024", "type": "Flood"}
        result = generate_situation_report(event_info, force_offline=True)

        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["mode"], "OFFLINE_FALLBACK")
        self.assertEqual(result["provenance_label"], "PROTOTYPE")
        self.assertIn("# 🛰️ NIRVAAN Situation Report", result["report_markdown"])


if __name__ == "__main__":
    unittest.main()
