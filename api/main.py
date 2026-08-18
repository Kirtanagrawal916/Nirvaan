"""
NIRVAAN FastAPI Application Entrypoint

Exposes HTTP endpoints for backend services, health monitoring,
CORS configuration, and detection pipeline integration.
"""

import os
from typing import Any, Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


# B-03 — GET /api/v1/health
@app.get("/api/v1/health")
def health_check() -> Dict[str, str]:
    """Health check endpoint returning HTTP 200 OK status."""
    return {"status": "ok"}
