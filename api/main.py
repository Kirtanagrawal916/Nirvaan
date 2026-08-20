"""
NIRVAAN FastAPI Application Entrypoint

Exposes HTTP endpoints for backend services, health monitoring,
CORS configuration, and detection pipeline integration.
"""

import os
from typing import Any, Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.server import (
    handle_health_check,
    handle_readiness_check,
    handle_disaster_latest_endpoint,
    handle_disasters_history_endpoint,
    handle_satellite_latest_endpoint,
)

app = FastAPI(
    title="NIRVAAN Disaster Monitoring API",
    version="1.0.0-prototype",
    description="Satellite-Based Disaster Monitoring and Spatial Intelligence API",
)

# B-04 — CORS Configuration
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

# BH-02 — Browser-Accessible Satellite Asset Serving
from pathlib import Path
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "frontend" / "assets"

if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")


# B-03 — GET /api/v1/health
@app.get("/api/v1/health")
@app.get("/api/health")
def health_check() -> Dict[str, str]:
    """Health check endpoint returning HTTP 200 OK status."""
    return {"status": "ok"}


# BH-05 — GET /api/v1/ready
@app.get("/api/v1/ready")
@app.get("/api/ready")
def readiness_check() -> Dict[str, Any]:
    """Readiness check endpoint verifying runtime data and configuration."""
    response = handle_readiness_check()
    return response["data"]


# API-01 — GET /api/disaster/latest
@app.get("/api/disaster/latest")
@app.get("/api/v1/disaster/latest")
def get_latest_disaster() -> Dict[str, Any]:
    """Returns the latest disaster detection result formatted for frontend compatibility."""
    response = handle_disaster_latest_endpoint()
    return response["data"]


# API-02 — GET /api/disasters
@app.get("/api/disasters")
@app.get("/api/v1/disasters")
def get_disaster_history() -> Any:
    """Returns history of disaster events formatted for frontend compatibility."""
    response = handle_disasters_history_endpoint()
    return response["data"]


# API-03 — GET /api/satellite/latest
@app.get("/api/satellite/latest")
@app.get("/api/v1/satellite/latest")
def get_latest_satellite_images() -> Dict[str, Any]:
    """Returns satellite imagery URLs formatted for frontend compatibility."""
    response = handle_satellite_latest_endpoint()
    return response["data"]
