"""
NIRVAAN FastAPI Application Entrypoint (api/main.py)

Exposes versioned REST HTTP endpoints for real disaster intelligence, persistent SQLite database
queries, asynchronous detection job enqueuing, alerts, satellite scene ingestion, and GeoJSON risk mapping.
"""

import os
from typing import Any, Dict, Optional
from fastapi import FastAPI, Header, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi.staticfiles import StaticFiles

from api.server import (
    handle_auth_register,
    handle_auth_login,
    handle_auth_me,
    handle_health_check,
    handle_readiness_check,
    handle_disaster_latest_endpoint,
    handle_disasters_history_endpoint,
    handle_disaster_detail_endpoint,
    handle_satellite_latest_endpoint,
    handle_create_detection_job_endpoint,
    handle_get_detection_job_endpoint,
    handle_create_report_endpoint,
    handle_list_reports_endpoint,
    handle_get_report_endpoint,
    handle_alerts_endpoint,
    handle_satellite_scenes_endpoint,
    handle_risk_map_endpoint,
)
from utils.auth import get_current_user_from_header
from utils.logging import configure_nirvaan_logging, set_request_id

configure_nirvaan_logging()

app = FastAPI(
    title="NIRVAAN Disaster Intelligence API",
    version="2.0.0",
    description="Satellite-Based Disaster Intelligence & Spatial Risk API",
)

# Request Correlation ID Middleware
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID")
    actual_id = set_request_id(req_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = actual_id
    return response

# CORS Configuration
default_origins = [
    "https://nirvaan-one.vercel.app",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]
env_origins = os.getenv("CORS_ORIGINS")
if env_origins:
    allowed_origins = [origin.strip() for origin in env_origins.split(",") if origin.strip()]
else:
    allowed_origins = default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "Content-Length", "Content-Type"],
)

# Satellite Asset Serving
BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "frontend" / "assets"

if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")


# Root Endpoint — GET /
@app.get("/")
def root() -> Dict[str, str]:
    """Root endpoint returning API status message."""
    return {
        "status": "ok",
        "message": "Nirvaan API is running"
    }


# Auth Endpoints
@app.post("/api/v1/auth/register")
def register_user(payload: Dict[str, Any], response: Response) -> Dict[str, Any]:
    """Registers a new user account."""
    res = handle_auth_register(payload)
    response.status_code = res["status_code"]
    return res["data"]


@app.post("/api/v1/auth/login")
def login_user(payload: Dict[str, Any], response: Response) -> Dict[str, Any]:
    """Authenticates a user and issues a JWT token."""
    res = handle_auth_login(payload)
    response.status_code = res["status_code"]
    return res["data"]


@app.get("/api/v1/auth/me")
def get_authenticated_user_profile(response: Response, authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Returns profile for currently authenticated user."""
    user = get_current_user_from_header(authorization)
    res = handle_auth_me(user)
    response.status_code = res["status_code"]
    return res["data"]


# GET /api/v1/health
@app.get("/api/v1/health")
@app.get("/api/health")
def health_check() -> Dict[str, str]:
    """Health check endpoint returning HTTP 200 OK status."""
    return {"status": "ok"}


# GET /api/v1/ready
@app.get("/api/v1/ready")
@app.get("/api/ready")
def readiness_check(response: Response) -> Dict[str, Any]:
    """Readiness check endpoint verifying database and runtime status."""
    res = handle_readiness_check()
    response.status_code = res["status_code"]
    return res["data"]


# GET /api/v1/disasters
@app.get("/api/v1/disasters")
@app.get("/api/disasters")
def get_disasters(
    response: Response,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    source_type: Optional[str] = Query(None)
) -> Any:
    """Returns real detected disasters from database with pagination & filtering."""
    res = handle_disasters_history_endpoint(
        limit=limit,
        offset=offset,
        event_type=type,
        severity=severity,
        from_date=from_date,
        to_date=to_date,
        source_type=source_type
    )
    response.status_code = res["status_code"]
    return res["data"]


# GET /api/v1/disasters/{id}
@app.get("/api/v1/disasters/{disaster_id}")
def get_disaster_detail(disaster_id: str, response: Response) -> Any:
    """Returns single disaster record by ID."""
    res = handle_disaster_detail_endpoint(disaster_id)
    response.status_code = res["status_code"]
    return res["data"]


# GET /api/disaster/latest
@app.get("/api/disaster/latest")
@app.get("/api/v1/disaster/latest")
def get_latest_disaster(response: Response) -> Dict[str, Any]:
    """Returns the latest disaster detection result formatted for frontend compatibility."""
    res = handle_disaster_latest_endpoint()
    response.status_code = res["status_code"]
    return res["data"]


# POST /api/v1/detection
@app.post("/api/v1/detection")
@app.post("/api/detection")
def create_detection_job(payload: Dict[str, Any], response: Response, authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Enqueues an asynchronous detection job for given coordinates."""
    current_user = get_current_user_from_header(authorization)
    res = handle_create_detection_job_endpoint(payload, current_user=current_user)
    response.status_code = res["status_code"]
    return res["data"]


# GET /api/v1/detection/{job_id}
@app.get("/api/v1/detection/{job_id}")
def get_detection_job_status(job_id: str, response: Response) -> Dict[str, Any]:
    """Queries asynchronous detection job status and results."""
    res = handle_get_detection_job_endpoint(job_id)
    response.status_code = res["status_code"]
    return res["data"]


# POST /api/v1/reports
@app.post("/api/v1/reports")
def create_situation_report(payload: Dict[str, Any], response: Response, authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Generates and stores a SITREP report from a disaster record."""
    current_user = get_current_user_from_header(authorization)
    res = handle_create_report_endpoint(payload, current_user=current_user)
    response.status_code = res["status_code"]
    return res["data"]


# GET /api/v1/reports
@app.get("/api/v1/reports")
def list_situation_reports(
    response: Response,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
) -> Any:
    """Lists generated SITREP reports."""
    res = handle_list_reports_endpoint(limit=limit, offset=offset)
    response.status_code = res["status_code"]
    return res["data"]


# GET /api/v1/reports/{report_id}
@app.get("/api/v1/reports/{report_id}")
def get_situation_report(report_id: str, response: Response) -> Any:
    """Gets single SITREP report by ID."""
    res = handle_get_report_endpoint(report_id)
    response.status_code = res["status_code"]
    return res["data"]


# GET /api/v1/alerts
@app.get("/api/v1/alerts")
@app.get("/api/alerts")
def get_alerts(response: Response) -> Any:
    """Returns real database alerts generated from verified detections."""
    res = handle_alerts_endpoint()
    response.status_code = res["status_code"]
    return res["data"]


# GET /api/v1/satellite-scenes
@app.get("/api/v1/satellite-scenes")
def get_satellite_scenes(response: Response) -> Any:
    """Returns ingested real satellite observations from database."""
    res = handle_satellite_scenes_endpoint()
    response.status_code = res["status_code"]
    return res["data"]


# GET /api/satellite/latest
@app.get("/api/satellite/latest")
@app.get("/api/v1/satellite/latest")
def get_latest_satellite_images(response: Response) -> Dict[str, Any]:
    """Returns latest satellite observation metadata."""
    res = handle_satellite_latest_endpoint()
    response.status_code = res["status_code"]
    return res["data"]


# GET /api/v1/risk
@app.get("/api/v1/risk")
@app.get("/api/risk")
def get_risk_map(response: Response) -> Dict[str, Any]:
    """Returns GeoJSON FeatureCollection of real detected inundations."""
    res = handle_risk_map_endpoint()
    response.status_code = res["status_code"]
    return res["data"]


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=False)
