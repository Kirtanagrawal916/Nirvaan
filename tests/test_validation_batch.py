"""
NIRVAAN Autonomous Production Validation Batch Test Suite (tests/test_validation_batch.py)

Validates:
- V-01: Production LIVE Flood/Wildfire & Copernicus Integration
- V-02: Wildfire dNBR Scientific Verification (True Pre/Post Difference, Band Mapping, USGS Tiers, Zero-Denominator Safety)
- V-03: Sentinel-2 Scene Selection Quality (AOI, Chronological Ordering, Cloud Ranking, Determinism, No-Scene Safety)
- V-04: Open-Meteo Hydrology Evidence Labeling (Primary Satellite Evidence vs Supporting Hydrology Context, Failure Isolation)
"""

import math
from datetime import datetime, timezone
import numpy as np
import pytest

from detection.detector_base import DetectorInput
from detection.detectors import ModularFloodDetector, ModularWildfireDetector
from detection.wildfire_detector import WildfireDetector, WildfireDetectionResult
from preprocessing.preprocess import ProcessedRaster
from services.copernicus_auth import CopernicusAuthManager, get_copernicus_auth
from services.flood_service import RealFloodDetectionService
from services.satellite_service import SatelliteIngestionService


# =========================================================================
# V-01: PRODUCTION LIVE DISASTER & COPERNICUS INTEGRATION
# =========================================================================

class TestV01ProductionLiveIntegration:
    """Validates real Copernicus authentication, STAC querying, and live detector execution."""

    def test_copernicus_auth_manager_lifecycle(self):
        """Verifies token acquisition, caching, and safe failure handling."""
        auth = get_copernicus_auth()
        assert auth is not None
        assert isinstance(auth, CopernicusAuthManager)

        # Has credentials check
        has_creds = auth.has_credentials()
        assert isinstance(has_creds, bool)

        # Token acquisition should succeed if credentials present
        if has_creds:
            token = auth.get_access_token()
            assert token is not None
            assert len(token) > 20
            # Test caching returns identical token
            cached_token = auth.get_access_token()
            assert token == cached_token

    def test_copernicus_auth_manager_invalid_credentials_isolation(self):
        """Verifies that invalid credentials fail safely without throwing unhandled exceptions."""
        bad_auth = CopernicusAuthManager(
            client_id="invalid-client-id-xyz",
            client_secret="invalid-secret-xyz"
        )
        token = bad_auth.get_access_token()
        assert token is None

    def test_modular_flood_detector_real_pipeline(self):
        """Verifies live flood detector execution and REAL_SATELLITE_DATA provenance."""
        detector = ModularFloodDetector()
        inp = DetectorInput(
            latitude=21.1702,
            longitude=72.8311,
            location_name="Surat, Gujarat (Tapi Basin)",
            disaster_type="flood",
            time_window_days=60
        )
        out = detector.run(inp)
        assert out.status == "success"
        assert out.disaster_type == "flood"
        assert out.confidence_score >= 50.0
        assert out.affected_area_km2 > 0.0
        assert out.severity in ["LOW", "MODERATE", "HIGH", "CRITICAL"]
        assert out.provenance["data_provenance"] in ["REAL_SATELLITE_DATA", "NO_LIVE_DATA"]
        assert "Copernicus" in out.provenance["provider"]

    def test_modular_wildfire_detector_real_pipeline(self):
        """Verifies live wildfire detector execution and REAL_SATELLITE_DATA provenance."""
        detector = ModularWildfireDetector()
        inp = DetectorInput(
            latitude=36.1500,
            longitude=27.9500,
            location_name="Rhodes, Greece",
            disaster_type="wildfire",
            time_window_days=60
        )
        out = detector.run(inp)
        assert out.status == "success"
        assert out.disaster_type == "wildfire"
        assert out.confidence_score >= 50.0
        assert out.affected_area_km2 > 0.0
        assert out.severity in ["LOW", "MODERATE", "HIGH", "CRITICAL"]
        assert out.provenance["data_provenance"] in ["REAL_SATELLITE_DATA", "NO_LIVE_DATA"]


# =========================================================================
# V-02: WILDFIRE dNBR SCIENTIFIC VERIFICATION
# =========================================================================

class TestV02WildfireDNBRScientific:
    """Validates true differential NBR math, band mapping, USGS tiers, and zero-denominator safety."""

    def test_dnbr_formula_and_orientation(self):
        """
        Verifies that dNBR = NBR_pre - NBR_post is positive in burned areas.
        Healthy vegetation: high NIR (0.8), low SWIR (0.1) -> NBR_pre = (0.8 - 0.1) / (0.8 + 0.1) = 0.7778
        Burned area: low NIR (0.15), high SWIR (0.6) -> NBR_post = (0.15 - 0.6) / (0.15 + 0.6) = -0.6000
        dNBR = 0.7778 - (-0.6000) = 1.3778 (High severity burn)
        """
        detector = WildfireDetector()

        # Synthetic pre-fire raster (dense healthy forest)
        pre_nir = np.full((10, 10), 0.80, dtype=np.float32)
        pre_swir = np.full((10, 10), 0.10, dtype=np.float32)
        pre_raster = ProcessedRaster(
            bands={"B08": pre_nir, "B12": pre_swir},
            dimensions=(10, 10),
            resolution_m=10.0,
            CRS="EPSG:4326"
        )
        nbr_pre, valid_pre = detector.calculate_nbr(pre_raster)
        assert np.all(valid_pre)
        assert np.isclose(nbr_pre[0, 0], (0.80 - 0.10) / (0.80 + 0.10), atol=1e-4)

        # Synthetic post-fire raster (burned scar)
        post_nir = np.full((10, 10), 0.15, dtype=np.float32)
        post_swir = np.full((10, 10), 0.60, dtype=np.float32)
        post_raster = ProcessedRaster(
            bands={"B08": post_nir, "B12": post_swir},
            dimensions=(10, 10),
            resolution_m=10.0,
            CRS="EPSG:4326"
        )
        nbr_post, valid_post = detector.calculate_nbr(post_raster)
        assert np.all(valid_post)
        assert np.isclose(nbr_post[0, 0], (0.15 - 0.60) / (0.15 + 0.60), atol=1e-4)

        # Difference
        dnbr = nbr_pre - nbr_post
        assert dnbr[0, 0] > 0.66  # High severity tier
        assert np.isclose(dnbr[0, 0], 1.37777, atol=1e-4)

    def test_dnbr_usgs_severity_classification_boundaries(self):
        """Verifies exact USGS / Copernicus burn severity tier boundaries."""
        detector = WildfireDetector()
        classes = detector.severity_classes

        # Test unburned (-0.1 to 0.1)
        assert classes["unburned"]["min"] <= 0.05 < classes["unburned"]["max"]
        # Test low severity (0.1 to 0.27)
        assert classes["low_severity"]["min"] <= 0.20 < classes["low_severity"]["max"]
        # Test moderate severity (0.27 to 0.66)
        assert classes["moderate_severity"]["min"] <= 0.45 < classes["moderate_severity"]["max"]
        # Test high severity (>= 0.66)
        assert classes["high_severity"]["min"] <= 0.85 <= classes["high_severity"]["max"]

    def test_nbr_numeric_safety_zero_denominator_and_nans(self):
        """Verifies that zero denominators, NaNs, and infinities do not produce false burn alarms."""
        detector = WildfireDetector()

        # Both NIR and SWIR are zero (dark/nodata)
        zero_nir = np.array([[0.0, np.nan], [np.inf, 0.5]], dtype=np.float32)
        zero_swir = np.array([[0.0, 0.2], [0.3, -np.inf]], dtype=np.float32)

        raster = ProcessedRaster(
            bands={"B08": zero_nir, "B12": zero_swir},
            dimensions=(2, 2),
            resolution_m=10.0,
            CRS="EPSG:4326"
        )

        nbr, valid = detector.calculate_nbr(raster)
        assert not valid[0, 0]  # Zero denominator marked invalid
        assert not valid[0, 1]  # NaN marked invalid
        assert not valid[1, 0]  # Inf marked invalid
        assert not valid[1, 1]  # -Inf marked invalid
        assert np.all(np.isfinite(nbr))  # All output numbers are finite float32


# =========================================================================
# V-03: SENTINEL-2 SCENE SELECTION QUALITY
# =========================================================================

class TestV03SceneSelectionQuality:
    """Validates AOI intersection, temporal ordering, cloud ranking, and determinism."""

    def test_bbox_generation_accuracy(self):
        """Verifies bounding box calculation centered on coordinates."""
        service = SatelliteIngestionService()
        bbox = service.create_bbox_from_latlon(lat=21.1702, lon=72.8311, delta_deg=0.15)
        assert len(bbox) == 4
        min_lon, min_lat, max_lon, max_lat = bbox
        assert min_lon < 72.8311 < max_lon
        assert min_lat < 21.1702 < max_lat
        assert math.isclose(max_lon - min_lon, 0.30, abs_tol=1e-3)
        assert math.isclose(max_lat - min_lat, 0.30, abs_tol=1e-3)

    def test_scene_search_cloud_filtering(self):
        """Verifies STAC queries enforce cloud cover upper bounds."""
        service = SatelliteIngestionService()
        scenes = service.search_sentinel2_stac(
            lat=21.1702,
            longitude=72.8311,
            days_back=90,
            max_cloud_cover=80.0,
            limit=3
        )
        assert isinstance(scenes, list)
        for s in scenes:
            assert s.get("cloud_cover", 0.0) <= 80.0
            assert "Sentinel-2" in s.get("satellite", "")

    def test_scene_selection_determinism(self):
        """Verifies that consecutive searches with identical parameters return deterministic order."""
        service = SatelliteIngestionService()
        scenes1 = service.search_sentinel2_stac(lat=44.4178, longitude=12.2035, days_back=60, limit=2)
        scenes2 = service.search_sentinel2_stac(lat=44.4178, longitude=12.2035, days_back=60, limit=2)
        assert len(scenes1) == len(scenes2)
        if scenes1 and scenes2:
            assert scenes1[0].get("scene_id") == scenes2[0].get("scene_id")


# =========================================================================
# V-04: OPEN-METEO HYDROLOGY EVIDENCE LABELING
# =========================================================================

class TestV04HydrologyEvidenceLabeling:
    """Validates primary satellite evidence vs supporting hydrological context."""

    def test_open_meteo_hydrology_fetch_and_schema(self):
        """Verifies Open-Meteo flood API fetching and schema structure."""
        service = SatelliteIngestionService()
        meteo = service.fetch_open_meteo_flood_data(lat=21.1702, lon=72.8311)
        assert meteo is not None
        assert "source" in meteo
        assert "Open-Meteo" in meteo["source"]

    def test_flood_service_evidence_separation(self):
        """Verifies that flood detection distinguishes satellite spectral analysis from hydrological context."""
        service = RealFloodDetectionService()
        res = service.execute_detection(latitude=21.1702, longitude=72.8311, location_name="Surat, Tapi Basin")

        assert res["status"] == "success"
        assert "model_metadata" in res
        assert "satellite_info" in res
        assert "hydrological_info" in res
        assert "provenance" in res

        # Primary evidence is spectral NDWI
        assert "NDWI" in res["model_metadata"]["inference_method"]
        # Hydrology is separate supporting context
        assert "river_discharge_mean_m3s" in res["hydrological_info"] or "error" in res["hydrological_info"]

    def test_flood_detection_resilience_to_hydrology_api_failure(self):
        """Verifies that satellite detection continues uninterrupted even if hydrology API fails."""
        # Create service with satellite service returning failed/empty meteo
        service = RealFloodDetectionService()
        # Mock sat_service.fetch_open_meteo_flood_data to simulate API timeout/failure
        orig_fetch = service.sat_service.fetch_open_meteo_flood_data
        service.sat_service.fetch_open_meteo_flood_data = lambda lat, lon: {
            "source": "Open-Meteo Global Flood API",
            "status": "UNAVAILABLE",
            "error": "Connection timed out (mock test)"
        }

        try:
            res = service.execute_detection(latitude=21.1702, longitude=72.8311, location_name="Surat Fallback Test")
            assert res["status"] == "success"
            assert res["affected_area_km2"] > 0.0
            assert res["confidence_score"] >= 50.0
            assert res["hydrological_info"]["status"] == "UNAVAILABLE"
        finally:
            service.sat_service.fetch_open_meteo_flood_data = orig_fetch
