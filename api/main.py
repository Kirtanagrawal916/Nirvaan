"""
NIRVAAN FastAPI Application Entrypoint (api/main.py)

Exposes versioned REST HTTP endpoints for real disaster intelligence, persistent SQLite database
queries, asynchronous detection job enqueuing, alerts, satellite scene ingestion, and GeoJSON risk mapping.
"""

import os
from typing import Any, Dict
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi.staticfiles import StaticFiles

from api.server import (
    handle_health_check,
    handle_readiness_check,
    handle_disaster_latest_endpoint,
    handle_disasters_history_endpoint,
    handle_disaster_detail_endpoint,
    handle_satellite_latest_endpoint,
    handle_create_detection_job_endpoint,
    handle_get_detection_job_endpoint,
    handle_alerts_endpoint,
    handle_satellite_scenes_endpoint,
    handle_risk_map_endpoint,
)

app = FastAPI(
    title="NIRVAAN Disaster Intelligence API",
    version="1.0.0-mvp",
    description="Satellite-Based Disaster Intelligence & Spatial Risk API",
)

# CORS Configuration
allowed_origins_raw = os.getenv("CORS_ORIGINS", "*")
allowed_origins = [
    origin.strip()
    for origin in allowed_origins_raw.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
def get_disasters(response: Response) -> Any:
    """Returns real detected disasters from database."""
    res = handle_disasters_history_endpoint()
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
def create_detection_job(payload: Dict[str, Any], response: Response) -> Dict[str, Any]:
    """Enqueues an asynchronous detection job for given coordinates."""
    res = handle_create_detection_job_endpoint(payload)
    response.status_code = res["status_code"]
    return res["data"]


# GET /api/v1/detection/{job_id}
@app.get("/api/v1/detection/{job_id}")
def get_detection_job_status(job_id: str, response: Response) -> Dict[str, Any]:
    """Queries asynchronous detection job status and results."""
    res = handle_get_detection_job_endpoint(job_id)
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
