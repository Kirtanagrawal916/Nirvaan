"""
Deterministic Unit Tests for NIRVAAN Dataset Evidence & Provenance Tracking
"""

import site
import sys
import unittest

# Ensure user site packages are in sys.path
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

from utils.provenance import (
    create_provenance_record,
    validate_provenance_completeness,
    attach_provenance,
)


class TestProvenanceTracking(unittest.TestCase):

    def test_create_provenance_record(self):
        record = create_provenance_record(
            dataset_id="CANONICAL_SENTINEL2_ASSAM_2024",
            source_url="https://scihub.copernicus.eu/s2",
            before_date="2024-05-10",
            after_date="2024-05-20",
            bands_used=["B03", "B08"],
            thresholds={"ndwi_threshold": 0.3}
        )

        self.assertEqual(record["dataset_id"], "CANONICAL_SENTINEL2_ASSAM_2024")
        self.assertEqual(record["acquisition_dates"]["before_date"], "2024-05-10")
        self.assertEqual(record["acquisition_dates"]["after_date"], "2024-05-20")
        self.assertEqual(record["bands_used"], ["B03", "B08"])
        self.assertEqual(record["provenance_label"], "VERIFIED_SOURCE_LINEAGE")

    def test_validate_provenance_completeness_valid(self):
        record = create_provenance_record(
            dataset_id="DS_001",
            source_url="https://example.com",
            before_date="2024-01-01",
            after_date="2024-01-05",
            bands_used=["B03"],
            thresholds={}
        )
        is_complete, errors = validate_provenance_completeness(record)
        self.assertTrue(is_complete)
        self.assertEqual(len(errors), 0)

    def test_validate_provenance_completeness_invalid(self):
        incomplete_record = {
            "dataset_id": "DS_001",
            # Missing source_url, acquisition_dates, bands_used
        }
        is_complete, errors = validate_provenance_completeness(incomplete_record)
        self.assertFalse(is_complete)
        self.assertGreater(len(errors), 0)

    def test_attach_provenance(self):
        output = {"status": "SUCCESS", "data": [1, 2, 3]}
        prov = create_provenance_record("DS_001", "http://src", "2024-01-01", "2024-01-02", ["B03"], {})
        
        result = attach_provenance(output, prov)
        self.assertIn("provenance", result)
        self.assertEqual(result["provenance"]["dataset_id"], "DS_001")


if __name__ == "__main__":
    unittest.main()
