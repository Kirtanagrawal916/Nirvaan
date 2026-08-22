"""
tests/test_gemini_integration.py
Automated tests for NIRVAAN Gemini AI integration, multimodal image validation,
disaster analysis, and secret protection.
"""

import io
import os
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from api.main import app
from services.gemini_service import GeminiService, GeminiServiceError, gemini_service

client = TestClient(app)


def create_test_image_bytes(format="JPEG", size=(100, 100), color="blue") -> bytes:
    """Helper to generate in-memory test image bytes."""
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


class TestGeminiValidation:
    """Tests image validation logic and constraints."""

    def test_validate_empty_image_raises_error(self):
        svc = GeminiService(api_key="test-key")
        with pytest.raises(GeminiServiceError) as exc_info:
            svc.validate_image(b"")
        assert exc_info.value.error_code == "EMPTY_IMAGE_PAYLOAD"
        assert exc_info.value.status_code == 400

    def test_validate_too_small_image_raises_error(self):
        svc = GeminiService(api_key="test-key")
        with pytest.raises(GeminiServiceError) as exc_info:
            svc.validate_image(b"short")
        assert exc_info.value.error_code == "IMAGE_TOO_SMALL"
        assert exc_info.value.status_code == 400

    def test_validate_corrupted_image_raises_error(self):
        svc = GeminiService(api_key="test-key")
        with pytest.raises(GeminiServiceError) as exc_info:
            svc.validate_image(b"X" * 500)
        assert exc_info.value.error_code == "CORRUPTED_OR_INVALID_IMAGE"
        assert exc_info.value.status_code == 422

    def test_validate_valid_jpeg(self):
        svc = GeminiService(api_key="test-key")
        img_bytes = create_test_image_bytes("JPEG", (150, 150))
        meta = svc.validate_image(img_bytes, "image/jpeg")
        assert meta["format"] == "JPEG"
        assert meta["width"] == 150
        assert meta["height"] == 150
        assert meta["size_bytes"] == len(img_bytes)

    def test_validate_valid_png(self):
        svc = GeminiService(api_key="test-key")
        img_bytes = create_test_image_bytes("PNG", (80, 80))
        meta = svc.validate_image(img_bytes, "image/png")
        assert meta["format"] == "PNG"
        assert meta["width"] == 80
        assert meta["height"] == 80


class TestGeminiEndpoints:
    """Tests FastAPI endpoints for image upload and disaster analysis."""

    def test_analyze_image_empty_payload_returns_400(self):
        resp = client.post("/api/v1/analyze/image")
        assert resp.status_code == 400
        data = resp.json()
        assert "error" in data
        assert data["error"]["code"] == "EMPTY_IMAGE"

    def test_analyze_image_multipart_upload(self):
        img_bytes = create_test_image_bytes("JPEG", (100, 100))
        files = {"file": ("test_scene.jpg", img_bytes, "image/jpeg")}
        data = {"context": "Test flood inundation scene"}

        mock_result = {
            "status": "success",
            "disaster_type": "Flood Inundation",
            "disaster_icon": "🌊",
            "confidence": 95.0,
            "confidence_score": 95.0,
            "severity": "HIGH",
            "severity_level": "HIGH",
            "severity_score": 78.0,
            "affected_area": "14.2 km²",
            "affectedArea": "14.2 km²",
            "population_exposure": 12000,
            "populationRisk": "~12,000 residents (Estimate)",
            "visual_observations": ["Submerged road networks", "Flooded urban basin"],
            "tactical_recommendations": ["Deploy watercraft rescue teams", "Establish high ground perimeter"],
            "executive_summary": "Major flood inundation detected across surveyed basin.",
            "data_provenance": "USER_UPLOADED_IMAGE_ANALYSIS",
            "disclaimer": "PROTOTYPE ESTIMATE"
        }

        with patch.object(gemini_service, "analyze_disaster_image", return_value=mock_result):
            resp = client.post("/api/v1/analyze/image", files=files, data=data)
            assert resp.status_code == 200
            res = resp.json()
            assert res["disaster_type"] == "Flood Inundation"
            assert res["confidence"] == 95.0
            assert res["severity"] == "HIGH"
            assert res["data_provenance"] == "USER_UPLOADED_IMAGE_ANALYSIS"

    def test_analyze_image_json_base64(self):
        import base64
        img_bytes = create_test_image_bytes("PNG", (60, 60))
        b64_str = base64.b64encode(img_bytes).decode("utf-8")

        payload = {
            "image_base64": f"data:image/png;base64,{b64_str}",
            "context": "Wildfire burn scar"
        }

        mock_result = {
            "status": "success",
            "disaster_type": "Wildfire Active Burn",
            "disaster_icon": "🔥",
            "confidence": 91.0,
            "confidence_score": 91.0,
            "severity": "HIGH",
            "severity_level": "HIGH",
            "severity_score": 82.0,
            "affected_area": "25.0 km²",
            "data_provenance": "USER_UPLOADED_IMAGE_ANALYSIS",
            "disclaimer": "PROTOTYPE ESTIMATE"
        }

        with patch.object(gemini_service, "analyze_disaster_image", return_value=mock_result):
            resp = client.post("/api/v1/analyze/image", json=payload)
            assert resp.status_code == 200
            res = resp.json()
            assert res["disaster_type"] == "Wildfire Active Burn"
            assert res["data_provenance"] == "USER_UPLOADED_IMAGE_ANALYSIS"

    def test_analyze_disaster_endpoint(self):
        payload = {
            "event_id": "flood-emilia-romagna-2023",
            "latitude": 44.4949,
            "longitude": 11.3426,
            "disaster_type": "flood",
            "location_name": "Emilia-Romagna, Italy"
        }

        mock_enrich = {
            "executive_summary": "Satellite telemetry indicates significant flood inundation in Emilia-Romagna basin.",
            "tactical_recommendations": [
                "Establish liaison with regional emergency operating centers.",
                "Prioritize access corridor clearance in mapped inundation perimeters."
            ],
            "critical_vulnerabilities": ["Critical transport intersections and low-lying assets."],
            "ai_status": "ENRICHED_BY_GEMINI"
        }

        with patch.object(gemini_service, "enrich_disaster_analysis", return_value=mock_enrich):
            resp = client.post("/api/v1/analyze/disaster", json=payload)
            assert resp.status_code == 200
            res = resp.json()
            assert res["status"] == "success"
            assert res["event_type"] == "flood"
            assert "executive_summary" in res
            assert "tactical_recommendations" in res
            assert res["data_provenance"] == "REAL_SATELLITE_DATA"
            real_key = os.getenv("GEMINI_API_KEY")
            if real_key:
                assert real_key not in resp.text


class TestSecretProtection:
    """Ensures Gemini API Key is never leaked in responses or public headers."""

    def test_api_key_not_in_error_responses(self):
        resp = client.post("/api/v1/analyze/image", files={"file": ("empty.jpg", b"", "image/jpeg")})
        resp_text = resp.text
        real_key = os.getenv("GEMINI_API_KEY")
        if real_key:
            assert real_key not in resp_text

    def test_service_does_not_expose_key_in_dict(self):
        meta = gemini_service.validate_image(create_test_image_bytes("JPEG", (50, 50)))
        assert "api_key" not in meta
        assert "key" not in meta
