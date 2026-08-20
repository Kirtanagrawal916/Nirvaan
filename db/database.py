"""
NIRVAAN SQLite Database Initialization & Schema Manager (db/database.py)

Manages persistent SQLite database connection and schema tables for:
- disasters
- satellite_observations
- detections
- alerts
- analysis_jobs
"""

import os
from pathlib import Path
import sqlite3
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.getenv("NIRVAAN_DB_PATH", str(BASE_DIR / "data" / "nirvaan.db")))


def get_db_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """
    Returns a configured sqlite3 connection with Row factory.
    """
    target_path = db_path or DB_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target_path), timeout=15.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Optional[Path] = None) -> None:
    """
    Creates database schema tables if they do not exist.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # 1. Disasters Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS disasters (
        id TEXT PRIMARY KEY,
        event_type TEXT NOT NULL,
        event_name TEXT,
        location_name TEXT NOT NULL,
        geometry_geojson TEXT,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        severity TEXT NOT NULL,
        confidence REAL NOT NULL,
        source TEXT NOT NULL,
        satellite TEXT NOT NULL,
        product_id TEXT,
        acquisition_time TEXT NOT NULL,
        detection_time TEXT NOT NULL,
        model_version TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Active',
        created_at TEXT NOT NULL
    );
    """)

    # 2. Satellite Observations Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS satellite_observations (
        id TEXT PRIMARY KEY,
        provider TEXT NOT NULL,
        satellite TEXT NOT NULL,
        sensor TEXT NOT NULL,
        scene_id TEXT NOT NULL UNIQUE,
        cloud_cover REAL,
        acquisition_time TEXT NOT NULL,
        bbox_json TEXT NOT NULL,
        source_url TEXT,
        metadata_json TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    # 3. Detections Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detections (
        id TEXT PRIMARY KEY,
        event_id TEXT NOT NULL,
        disaster_type TEXT NOT NULL,
        status TEXT NOT NULL,
        detection_summary_json TEXT,
        affected_area_json TEXT,
        severity_json TEXT,
        hotspots_json TEXT,
        mask_reference_json TEXT,
        provenance_json TEXT,
        data_provenance TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (event_id) REFERENCES disasters (id) ON DELETE CASCADE
    );
    """)

    # 4. Alerts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id TEXT PRIMARY KEY,
        disaster_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        location TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        confidence REAL NOT NULL,
        source TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'UNREAD',
        created_at TEXT NOT NULL,
        FOREIGN KEY (disaster_id) REFERENCES disasters (id) ON DELETE CASCADE
    );
    """)

    # 5. Analysis Jobs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analysis_jobs (
        id TEXT PRIMARY KEY,
        status TEXT NOT NULL, -- queued, processing, completed, failed
        disaster_type TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        created_at TEXT NOT NULL,
        started_at TEXT,
        completed_at TEXT,
        error TEXT,
        model_version TEXT NOT NULL,
        result_json TEXT
    );
    """)

    conn.commit()
    conn.close()
