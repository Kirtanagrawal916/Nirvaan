"""
Tests for Copernicus Data Space Ecosystem (CDSE) Sentinel-2 Integration.
Verifies OAuth2 authentication, STAC catalog queries, band retrieval, NDWI/NBR spectral math,
disaster detector integration, provenance integrity, and failure handling.
"""

from datetime import datetime, timezone
import json
import os
import unittest
from unittest.mock import MagicMock, patch
import numpy as np

from services.copernicus_auth import CopernicusAuthManager
from services.satellite_service import SatelliteIngestionService
from detection.detectors import ModularFloodDetector, ModularWildfireDetector
from detection.detector_base import DetectorInput


class TestCopernicusAuth(unittest.TestCase):
    """Tests for CopernicusAuthManager OAuth2 client credentials flow."""

    def test_auth_manager_credential_detection(self):
        auth = CopernicusAuthManager(client_id="test-client-id", client_secret="test-secret")
        self.assertTrue(auth.has_credentials())
        self.assertEqual(auth.client_id, "test-client-id")

    def test_auth_manager_missing_credentials(self):
        auth = CopernicusAuthManager(client_id="", client_secret="")
        self.assertFalse(auth.has_credentials())
        token = auth.get_access_token()
        self.assertIsNone(token)

    @patch("urllib.request.urlopen")
    def test_auth_manager_token_acquisition_and_caching(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "access_token": "mock-copernicus-jwt-token",
            "expires_in": 1800,
            "token_type": "Bearer"
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        auth = CopernicusAuthManager(client_id="my-id", client_secret="my-sec")
        token = auth.get_access_token()

        self.assertEqual(token, "mock-copernicus-jwt-token")
        self.assertTrue(auth.is_token_valid())

        # Second call should use cache without invoking urlopen again
        token2 = auth.get_access_token()
        self.assertEqual(token2, "mock-copernicus-jwt-token")
        self.assertEqual(mock_urlopen.call_count, 1)

        # Invalidate forces refresh
        auth.invalidate_token()
        self.assertFalse(auth.is_token_valid())

    @patch("urllib.request.urlopen")
    def test_auth_manager_handles_http_error(self, mock_urlopen):
        import urllib.error
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://identity.dataspace.copernicus.eu/token",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=None
        )

        auth = CopernicusAuthManager(client_id="bad-id", client_secret="bad-sec")
        token = auth.get_access_token()
        self.assertIsNone(token)


class TestCopernicusSTACService(unittest.TestCase):
    """Tests for Copernicus STAC ingestion service."""

    def test_stac_endpoint_configuration(self):
        service = SatelliteIngestionService(stac_base_url="https://stac.dataspace.copernicus.eu/v1/")
        self.assertEqual(service.stac_base_url, "https://stac.dataspace.copernicus.eu/v1/")
        self.assertEqual(service.stac_search_url, "https://stac.dataspace.copernicus.eu/v1/search")

    @patch("urllib.request.urlopen")
    def test_stac_search_parses_copernicus_features(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "type": "FeatureCollection",
            "features": [{
                "id": "S2B_MSIL2A_20230525T095559_N0510_R122_T32TQQ_20240908T101427",
                "properties": {
                    "datetime": "2023-05-25T09:55:59.024Z",
                    "platform": "sentinel-2b",
                    "eo:cloud_cover": 6.46,
                    "grid:code": "CDSE-32TQQ",
                    "processing:level": "Level-2A (Surface Reflectance)"
                },
                "bbox": [12.0, 44.0, 12.5, 44.5],
                "assets": {
                    "B03_10m": {"href": "https://download.dataspace.copernicus.eu/b03.jp2"},
                    "B08_10m": {"href": "https://download.dataspace.copernicus.eu/b08.jp2"},
                    "thumbnail": {"href": "https://datahub.creodias.eu/thumb.jpg"}
                }
            }]
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        mock_repo = MagicMock()
        mock_repo.save_satellite_observation.side_effect = lambda **kwargs: kwargs

        service = SatelliteIngestionService(repo=mock_repo)
        results = service.search_sentinel2_stac(lat=44.4178, longitude=12.2035, days_back=30)

        self.assertEqual(len(results), 1)
        res = results[0]
        self.assertEqual(res["scene_id"], "S2B_MSIL2A_20230525T095559_N0510_R122_T32TQQ_20240908T101427")
        self.assertEqual(res["cloud_cover"], 6.46)
        self.assertEqual(res["provider"], "Copernicus Data Space Ecosystem (Sentinel-2 L2A)")
        self.assertEqual(res["metadata"]["band_urls"]["b03"], "https://download.dataspace.copernicus.eu/b03.jp2")
        self.assertEqual(res["metadata"]["band_urls"]["b08"], "https://download.dataspace.copernicus.eu/b08.jp2")

    @patch("services.copernicus_auth.CopernicusAuthManager.get_access_token")
    @patch("urllib.request.urlopen")
    def test_fetch_sentinel2_bands_decodes_raster(self, mock_urlopen, mock_get_token):
        mock_get_token.return_value = "valid-test-token"

        # Create a mock 1-channel TIFF in memory using PIL
        import io
        from PIL import Image
        fake_arr = (np.ones((64, 64), dtype=np.float32) * 0.45)
        img = Image.fromarray(fake_arr)
        buf = io.BytesIO()
        img.save(buf, format="TIFF")
        tiff_bytes = buf.getvalue()

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = tiff_bytes
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        service = SatelliteIngestionService()
        bands = service.fetch_sentinel2_bands(
            bbox=[12.0, 44.0, 12.5, 44.5],
            time_from="2023-05-01T00:00:00Z",
            time_to="2023-05-25T23:59:59Z",
            bands=["B03", "B08"]
        )

        self.assertIn("B03", bands)
        self.assertIn("B08", bands)
        self.assertEqual(bands["B03"].shape, (64, 64))
        self.assertAlmostEqual(float(bands["B03"][0, 0]), 0.45, places=2)


class TestCopernicusDetectorIntegration(unittest.TestCase):
    """Tests for end-to-end detector runs with real Copernicus spectral algorithms."""

    def test_modular_flood_detector_ndwi_spectral_calculation(self):
        mock_sat_service = MagicMock()
        mock_sat_service.search_sentinel2_stac.return_value = [{
            "scene_id": "S2_COPERNICUS_FLOOD_TEST",
            "cloud_cover": 4.0,
            "acquisition_time": "2026-08-20T10:00:00Z",
            "provider": "Copernicus Data Space Ecosystem (Sentinel-2 L2A)"
        }]
        mock_sat_service.fetch_open_meteo_flood_data.return_value = {
            "river_discharge_mean_m3s": 75.0,
            "river_discharge_max_m3s": 140.0,
            "daily": {"river_discharge": [50.0, 60.0, 75.0, 90.0, 110.0, 130.0, 140.0]}
        }

        # Create water and non-water pixels
        # In water: B03 (Green, 0.4) > B08 (NIR, 0.1) -> NDWI = (0.4-0.1)/(0.5) = 0.6 (>0.15 => water)
        b03_arr = np.full((64, 64), 0.4, dtype=np.float32)
        b08_arr = np.full((64, 64), 0.1, dtype=np.float32)
        mock_sat_service.fetch_sentinel2_bands.return_value = {
            "B03": b03_arr,
            "B08": b08_arr
        }

        mock_repo = MagicMock()
        detector = ModularFloodDetector(repo=mock_repo, satellite_service=mock_sat_service)

        inp = DetectorInput(latitude=44.4178, longitude=12.2035, location_name="Emilia-Romagna, Italy", disaster_type="flood")
        result = detector.run(inp)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.disaster_type, "flood")
        self.assertEqual(result.provenance["data_provenance"], "REAL_SATELLITE_DATA")
        self.assertEqual(result.provenance["provider"], "Copernicus Data Space Ecosystem (Sentinel-2 L2A)")
        self.assertIn("Copernicus Sentinel-2 NDWI", result.model_metadata["inference_method"])
        self.assertTrue(result.model_metadata["real_spectral_bands_analyzed"])

    def test_modular_wildfire_detector_nbr_spectral_calculation(self):
        mock_sat_service = MagicMock()
        mock_sat_service.search_sentinel2_stac.return_value = [{
            "scene_id": "S2_COPERNICUS_WILDFIRE_TEST",
            "cloud_cover": 2.0,
            "acquisition_time": "2026-08-20T10:00:00Z",
            "provider": "Copernicus Data Space Ecosystem (Sentinel-2 L2A)"
        }]

        # In burned area: NIR drops, SWIR increases
        # B08 (NIR, 0.1), B12 (SWIR, 0.5) -> NBR = (0.1-0.5)/(0.6) = -0.667 (<0.10 => burned)
        b08_arr = np.full((64, 64), 0.1, dtype=np.float32)
        b12_arr = np.full((64, 64), 0.5, dtype=np.float32)
        mock_sat_service.fetch_sentinel2_bands.return_value = {
            "B08": b08_arr,
            "B12": b12_arr
        }

        mock_repo = MagicMock()
        detector = ModularWildfireDetector(repo=mock_repo, satellite_service=mock_sat_service)

        inp = DetectorInput(latitude=36.1700, longitude=27.9400, location_name="Rhodes, Greece", disaster_type="wildfire")
        result = detector.run(inp)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.disaster_type, "wildfire")
        self.assertEqual(result.provenance["data_provenance"], "REAL_SATELLITE_DATA")
        self.assertEqual(result.provenance["provider"], "Copernicus Data Space Ecosystem (Sentinel-2 L2A)")
        self.assertIn("Copernicus Sentinel-2 NBR", result.model_metadata["inference_method"])
        self.assertTrue(result.model_metadata["real_spectral_bands_analyzed"])


if __name__ == "__main__":
    unittest.main()
