"""
NIRVAAN Phase 2 Comprehensive Reliability, Security, Async Detection & Provenance Test Suite

Executes automated end-to-end tests for:
1. User Authentication & JWT RBAC (/api/v1/auth/register, login, me)
2. Asynchronous Detection Job System & Lifecycle Stages (/api/v1/detection)
3. Idempotency & AOI Duplicate Prevention
4. Real Disasters History Filtering & Provenance Attribution (/api/v1/disasters)
5. Grounded SITREP Situation Report Generation & Retrieval (/api/v1/reports)
6. Standardized Error Contracts & Request Correlation IDs (X-Request-ID)
"""

from datetime import datetime
import json
import os
import pytest
from fastapi.testclient import TestClient

from api.main import app
from db.database import init_db
from db.repository import DatabaseRepository
from utils.auth import create_access_token, hash_password, verify_password

client = TestClient(app)


import uuid

@pytest.fixture(autouse=True)
def setup_test_environment(tmp_path):
    """Initializes a fresh test database for isolated test execution."""
    test_db = tmp_path / f"test_nirvaan_{uuid.uuid4().hex[:6]}.db"
    init_db(test_db)
    os.environ["NIRVAAN_DB_PATH"] = str(test_db)
    import db.repository
    db.repository.DatabaseRepository.db_path = test_db
    yield
    if test_db.exists():
        try:
            test_db.unlink()
        except Exception:
            pass


# 1. Authentication & Security Tests
def test_auth_registration_login_flow():
    """Tests user registration, login, password hashing, and JWT token issuance."""
    test_email = f"analyst-{uuid.uuid4().hex[:6]}@nirvaan.ai"
    reg_payload = {
        "email": test_email,
        "password": "SecurePassword123!",
        "full_name": "Senior Disaster Analyst",
        "role": "analyst"
    }
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201, reg_res.text
    reg_data = reg_res.json()
    assert reg_data["status"] == "success"
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == test_email
    assert reg_data["user"]["role"] == "analyst"

    # 2. Duplicate Registration Rejection
    dup_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert dup_res.status_code == 409
    assert dup_res.json()["error"]["code"] == "USER_ALREADY_EXISTS"

    # 3. Login User
    login_res = client.post("/api/v1/auth/login", json={
        "email": test_email,
        "password": "SecurePassword123!"
    })
    assert login_res.status_code == 200
    login_data = login_res.json()
    token = login_data["access_token"]
    assert token is not None

    # 4. Fetch User Profile (/api/v1/auth/me) with Bearer token
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == test_email


def test_auth_invalid_credentials_and_protected_access():
    """Verifies that invalid password returns 401 and protected endpoints require token."""
    # Register user
    client.post("/api/v1/auth/register", json={
        "email": "user@nirvaan.ai",
        "password": "CorrectPassword123!"
    })

    # Incorrect password
    bad_res = client.post("/api/v1/auth/login", json={
        "email": "user@nirvaan.ai",
        "password": "WrongPassword!"
    })
    assert bad_res.status_code == 401
    assert bad_res.json()["error"]["code"] == "AUTHENTICATION_FAILED"

    # Unauthenticated /api/v1/auth/me
    no_token_res = client.get("/api/v1/auth/me")
    assert no_token_res.status_code == 401
    assert no_token_res.json()["error"]["code"] == "UNAUTHORIZED"


# 2. Request Correlation & Error Handling Tests
import time

def test_request_id_correlation_header():
    """Verifies X-Request-ID propagation across HTTP endpoints."""
    custom_req_id = "req-test-998877665544"
    res = client.get("/api/v1/health", headers={"X-Request-ID": custom_req_id})
    assert res.status_code == 200
    assert res.headers.get("X-Request-ID") == custom_req_id

    # Test error correlation ID
    err_res = client.post("/api/v1/detection", json={"latitude": "invalid", "longitude": 72.83}, headers={"X-Request-ID": custom_req_id})
    assert err_res.status_code == 400
    err_json = err_res.json()
    assert err_json["error"]["request_id"] == custom_req_id
    assert err_json["error"]["code"] == "INVALID_COORDINATES"


# 3. Asynchronous Job & Lifecycle Tests
def test_async_detection_job_execution_lifecycle():
    """Tests job creation, initial queued/processing state, polling, and completion."""
    rand_lat = 21.0 + (hash(uuid.uuid4()) % 1000) / 100.0
    rand_lon = 72.0 + (hash(uuid.uuid4()) % 1000) / 100.0

    job_payload = {
        "latitude": rand_lat,
        "longitude": rand_lon,
        "disaster_type": "flood",
        "location_name": "Surat Tapi Basin Test"
    }

    # Submit job
    submit_res = client.post("/api/v1/detection", json=job_payload)
    assert submit_res.status_code == 202
    sub_data = submit_res.json()
    assert "job_id" in sub_data
    job_id = sub_data["job_id"]
    assert sub_data["status"] in ["queued", "processing"]

    # Poll status until completed (max 25 iterations with 0.4s pause = 10s timeout)
    completed = False
    final_data = None
    for _ in range(25):
        time.sleep(0.4)
        status_res = client.get(f"/api/v1/detection/{job_id}")
        assert status_res.status_code == 200
        status_data = status_res.json()
        assert "stage" in status_data
        assert "progress" in status_data

        if status_data["status"] == "completed":
            completed = True
            final_data = status_data
            break

    assert completed, f"Job did not transition to completed state. Final status: {status_data if 'status_data' in locals() else None}"
    result = final_data["result"]
    assert result["disaster_type"] == "flood"
    assert "confidence_score" in result
    assert "model_metadata" in result
    assert result["model_metadata"]["model_name"] == "Nirvaan-NDWI-v1.0"
    assert "processing_duration_ms" in result["model_metadata"]


def test_job_idempotency_for_duplicate_aoi():
    """Verifies that submitting a second job for an active AOI returns the existing active job."""
    job_payload = {
        "latitude": 22.3072,
        "longitude": 73.1812,
        "disaster_type": "flood",
        "location_name": "Vadodara Active AOI"
    }

    job1 = client.post("/api/v1/detection", json=job_payload).json()
    job2 = client.post("/api/v1/detection", json=job_payload).json()

    assert job1["job_id"] == job2["job_id"]


# 4. History API & Provenance Tests
def test_disasters_history_filtering_and_provenance():
    """Tests /api/v1/disasters with pagination, filters, and provenance attribution."""
    res = client.get("/api/v1/disasters?limit=10&offset=0")
    assert res.status_code == 200
    items = res.json()
    assert isinstance(items, list)

    for d in items:
        assert "provenance_type" in d
        assert d["provenance_type"] in ["NIRVAAN_DETECTION", "EXTERNAL_HISTORICAL_EVENT"]
        assert "data_provenance" in d


# 5. SITREP Reports Generation & API Tests
def test_report_generation_and_retrieval():
    """Tests generating a SITREP report and listing/fetching reports."""
    report_req = {
        "disaster_type": "flood",
        "location_name": "Surat Tapi Basin",
        "latitude": 21.17,
        "longitude": 72.83
    }
    create_res = client.post("/api/v1/reports", json=report_req)
    assert create_res.status_code == 201
    report = create_res.json()
    assert "id" in report
    assert "report_markdown" in report
    assert "report_json" in report

    # List reports
    list_res = client.get("/api/v1/reports")
    assert list_res.status_code == 200
    reports = list_res.json()
    assert len(reports) >= 1

    # Fetch single report
    single_res = client.get(f"/api/v1/reports/{report['id']}")
    assert single_res.status_code == 200
    assert single_res.json()["id"] == report["id"]
