"""
Deterministic Unit Tests for NIRVAAN Confidence & Uncertainty Estimation Engine
"""

import site
import sys
import unittest
import numpy as np

# Ensure user site packages are in sys.path
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

from analysis.confidence import calculate_evidence_confidence


class TestConfidenceEstimation(unittest.TestCase):

    def test_calculate_evidence_confidence_valid(self):
        # 10x10 array with strong signal in middle
        diff_arr = np.zeros((10, 10), dtype=float)
        diff_arr[3:7, 3:7] = 0.6  # Active signal
        diff_arr[0:2, 0:2] = 0.02 # Background noise

        mask_arr = diff_arr > 0.1

        res = calculate_evidence_confidence(diff_arr, mask_arr)

        self.assertEqual(res["provenance_label"], "ESTIMATE")
        self.assertTrue(res["is_prototype"])
        self.assertGreater(res["confidence_score"], 0.5)
        self.assertEqual(len(res["uncertainty_band"]), 2)
        self.assertLessEqual(res["uncertainty_band"][0], res["confidence_score"])
        self.assertGreaterEqual(res["uncertainty_band"][1], res["confidence_score"])

    def test_calculate_evidence_confidence_empty_or_none(self):
        res_none = calculate_evidence_confidence(None)
        self.assertEqual(res_none["confidence_score"], 0.0)
        self.assertEqual(res_none["quality_tier"], "UNASSESSED")
        self.assertEqual(res_none["provenance_label"], "ESTIMATE")

        res_empty = calculate_evidence_confidence(np.array([]))
        self.assertEqual(res_empty["confidence_score"], 0.0)
        self.assertEqual(res_empty["quality_tier"], "INVALID_DATA")

    def test_safety_disclaimer_presence(self):
        diff_arr = np.ones((5, 5), dtype=float) * 0.8
        res = calculate_evidence_confidence(diff_arr)

        self.assertIn("not an operational emergency standard", res["disclaimer"].lower())


if __name__ == "__main__":
    unittest.main()
