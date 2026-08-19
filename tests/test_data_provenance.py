import json
import logging
from pathlib import Path
import unittest

from data.event_schema import DisasterEvent
from data.loader import DatasetLoader, load_event
from detection.result_contract import DetectionResultContract
from detection.pipeline import run_detection
from api.server import (
    handle_readiness_check,
    handle_disaster_latest_endpoint,
    handle_disasters_history_endpoint,
    handle_satellite_latest_endpoint,
    handle_detect_endpoint,
    handle_analyze_endpoint,
    handle_report_endpoint,
)
from reports.situation_report import generate_situation_report, generate_fallback_situation_report
from mapping.map_builder import build_folium_map, generate_provenance_watermark_html


class TestDataProvenance(unittest.TestCase):

    def test_disaster_event_provenance_defaults(self):
        """Verify DisasterEvent defaults to REAL_SATELLITE_DATA and serializes clean provenance."""
        raw_event = {
            "event_id": "test-event-01",
            "disaster_type": "flood",
            "location_name": "Test AOI",
            "latitude": 44.5,
            "longitude": 11.3,
            "before_image": "data/canonical/flood/before",
            "after_image": "data/canonical/flood/after",
            "before_date": "2023-05-04",
            "after_date": "2023-05-19",
            "source": "Sentinel-2",
            "CRS": "EPSG:4326",
            "resolution_m": 10.0,
            "available_bands": ["B03", "B08"]
        }
        event = DisasterEvent.from_dict(raw_event)
        self.assertEqual(event.data_provenance, "REAL_SATELLITE_DATA")
        event_dict = event.to_dict()
        self.assertEqual(event_dict["data_provenance"], "REAL_SATELLITE_DATA")

        reconstructed = DisasterEvent.from_dict(event_dict)
        self.assertEqual(reconstructed.data_provenance, "REAL_SATELLITE_DATA")

    def test_dataset_loader_synthetic_fallback_logging(self):
        """Verify DatasetLoader sets SYNTHETIC_FALLBACK and logs warning when band files are missing."""
        with self.assertLogs("nirvaan.loader", level="WARNING") as cm:
            event = load_event("flood-emilia-romagna-2023", verify_files=False)
            self.assertEqual(event.data_provenance, "SYNTHETIC_FALLBACK")
            self.assertTrue(any("Synthetic fallback triggered" in msg for msg in cm.output))

    def test_detection_result_contract_synthetic_warning_disclosure(self):
        """Verify DetectionResultContract auto-appends disclosure warning when SYNTHETIC_FALLBACK."""
        contract = DetectionResultContract(
            event_id="test-event",
            disaster_type="flood",
            status="success",
            timestamp="2026-08-20T00:00:00Z",
            event_metadata={"location_name": "Test Location"},
            detection_summary={"change_pixels": 100},
            affected_area={"affected_area_km2": 5.0},
            severity={"severity_level": "MODERATE"},
            hotspots=[],
            mask_reference={},
            provenance={},
            data_provenance="SYNTHETIC_FALLBACK",
            warnings=[]
        )

        self.assertEqual(contract.data_provenance, "SYNTHETIC_FALLBACK")
        self.assertTrue(any("synthetic placeholder data" in w for w in contract.warnings))

        serialized = contract.to_dict()
        self.assertEqual(serialized["data_provenance"], "SYNTHETIC_FALLBACK")
        self.assertEqual(serialized["event_metadata"]["data_provenance"], "SYNTHETIC_FALLBACK")
        self.assertEqual(serialized["provenance"]["data_provenance"], "SYNTHETIC_FALLBACK")

    def test_readiness_probe_reports_canonical_events_backing(self):
        """Verify /api/v1/ready reports canonical_events_backing."""
        response = handle_readiness_check()
        body = response["data"]
        self.assertEqual(response["status_code"], 200)
        self.assertIn("canonical_events_backing", body)
        self.assertIn("flood-emilia-romagna-2023", body["canonical_events_backing"])
        self.assertIn(body["canonical_events_backing"]["flood-emilia-romagna-2023"], {"REAL_SATELLITE_DATA", "SYNTHETIC_FALLBACK"})

    def test_api_endpoints_surface_data_provenance(self):
        """Verify /api/disaster/latest, /api/disasters, /api/satellite/latest include data_provenance."""
        res_latest = handle_disaster_latest_endpoint()["data"]
        self.assertIn("data_provenance", res_latest)

        res_history = handle_disasters_history_endpoint()["data"]
        self.assertTrue(len(res_history) > 0)
        self.assertIn("data_provenance", res_history[0])

        res_sat = handle_satellite_latest_endpoint()["data"]
        self.assertIn("data_provenance", res_sat)

    def test_detect_and_analyze_endpoints_data_provenance(self):
        """Verify POST /api/v1/detect and /api/v1/analyze return data_provenance."""
        valid_payload = {
            "event": {
                "event_id": "EVT_001",
                "name": "Test Event",
                "type": "flood",
                "lat": 44.5,
                "lon": 11.3,
                "location_name": "Test Location"
            },
            "data_provenance": "SYNTHETIC_FALLBACK"
        }
        res = handle_detect_endpoint(valid_payload)
        self.assertEqual(res["status_code"], 200)
        detect_res = res["data"]
        self.assertEqual(detect_res["data_provenance"], "SYNTHETIC_FALLBACK")

        analyze_res = handle_analyze_endpoint({"data_provenance": "SYNTHETIC_FALLBACK"})["data"]
        self.assertEqual(analyze_res["data_provenance"], "SYNTHETIC_FALLBACK")

    def test_situation_report_provenance_disclosure(self):
        """Verify situation report output contains data provenance disclosure."""
        payload = {
            "event": {"event_name": "Test Flood", "disaster_type": "Flood", "location_name": "Test Loc"},
            "data_provenance": "SYNTHETIC_FALLBACK"
        }
        report_text = generate_fallback_situation_report(payload)
        self.assertIn("**Data Provenance:**", report_text)
        self.assertIn("SYNTHETIC_FALLBACK", report_text)

        full_report = generate_situation_report(payload, force_offline=True)
        self.assertEqual(full_report["data_provenance"], "SYNTHETIC_FALLBACK")

    def test_map_builder_provenance_watermark(self):
        """Verify map builder includes provenance watermark html overlay."""
        watermark_synthetic = generate_provenance_watermark_html("SYNTHETIC_FALLBACK")
        self.assertIn("DEMO MODE: SYNTHETIC DATA", watermark_synthetic)

        watermark_real = generate_provenance_watermark_html("REAL_SATELLITE_DATA")
        self.assertIn("REAL SATELLITE DATA", watermark_real)

        m = build_folium_map(
            event_location={"lat": 44.5, "lon": 11.3, "name": "Emilia Test"},
            data_provenance="SYNTHETIC_FALLBACK"
        )
        map_html = m.get_root().render()
        self.assertIn("DEMO MODE: SYNTHETIC DATA", map_html)


if __name__ == "__main__":
    unittest.main()
