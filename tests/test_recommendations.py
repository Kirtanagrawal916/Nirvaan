"""
Deterministic Unit Tests for NIRVAAN Responder Recommendations Module
"""

import site
import sys
import unittest

# Ensure user site packages are in sys.path
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

from reports.recommendations import (
    generate_response_recommendations,
    PROHIBITED_OPERATIONAL_TERMS,
)
from reports.situation_report import generate_situation_report


class TestResponseRecommendations(unittest.TestCase):

    def test_generate_response_recommendations_high_severity(self):
        sev_result = {"impact_score": 78.0, "impact_band": "Extreme"}
        pop_impact = {"estimated_affected_population": 4500}
        infra_impact = {
            "impacted_infrastructure": [
                {"name": "Assam District Hospital", "category": "hospital", "distance_km": 0.6}
            ]
        }
        zones = [{"zone_type": "core"}, {"zone_type": "buffer_moderate"}]

        res = generate_response_recommendations(sev_result, pop_impact, infra_impact, zones)

        self.assertEqual(res["status"], "PROTOTYPE")
        self.assertEqual(res["provenance_label"], "PROTOTYPE")
        self.assertTrue(res["is_prototype"])
        self.assertGreater(res["recommendations_count"], 0)

        # Check P0 critical item presence
        p0_items = [r for r in res["recommendations"] if r["priority"] == "P0_CRITICAL_VERIFICATION"]
        self.assertGreater(len(p0_items), 0)
        self.assertIn("Assam District Hospital", p0_items[1]["suggestion"])

    def test_generate_response_recommendations_low_severity(self):
        sev_result = {"impact_score": 10.0, "impact_band": "Low"}
        res = generate_response_recommendations(sev_result, None, None, [])

        self.assertEqual(res["status"], "PROTOTYPE")
        # Baseline P2 monitoring suggestions should be present
        p2_items = [r for r in res["recommendations"] if r["priority"] == "P2_MONITORING"]
        self.assertGreater(len(p2_items), 0)

    def test_prohibited_operational_terms_absence(self):
        sev_result = {"impact_score": 85.0, "impact_band": "Extreme"}
        pop_impact = {"estimated_affected_population": 12000}
        infra_impact = {
            "impacted_infrastructure": [
                {"name": "District Hospital", "category": "hospital", "distance_km": 0.3}
            ]
        }

        res = generate_response_recommendations(sev_result, pop_impact, infra_impact)
        full_text = " ".join(res["formatted_suggestions"]).lower()

        for term in PROHIBITED_OPERATIONAL_TERMS:
            self.assertNotIn(term, full_text)

    def test_situation_report_recommendations_integration(self):
        event_info = {"name": "Assam Flood 2024", "type": "Flood"}
        sev_result = {"impact_score": 65.0, "impact_band": "High"}
        pop_impact = {"status": "SUCCESS", "estimated_affected_population": 3000}
        infra_impact = {
            "status": "SUCCESS",
            "impacted_infrastructure": [{"name": "Bridge 1", "category": "bridge", "distance_km": 0.8}],
            "advisory_statements": ["Bridge ('Bridge 1') within 0.8 km — field verification recommended."]
        }

        report_res = generate_situation_report(
            (event_info, {}, [], pop_impact, infra_impact, sev_result),
            force_offline=True
        )

        md = report_res["report_markdown"]
        self.assertIn("## 4. Responder Recommendations", md)
        self.assertIn("Prioritize ground verification in core affected zone", md)


if __name__ == "__main__":
    unittest.main()
