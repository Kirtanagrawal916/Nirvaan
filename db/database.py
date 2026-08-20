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
        status TEXT NOT NULL, -- queued, processing, completed, failed, cancelled
        stage TEXT DEFAULT 'queued',
        progress INTEGER DEFAULT 0,
        disaster_type TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        user_id TEXT,
        retry_count INTEGER DEFAULT 0,
        last_retry_at TEXT,
        created_at TEXT NOT NULL,
        started_at TEXT,
        completed_at TEXT,
        error TEXT,
        model_version TEXT NOT NULL,
        result_json TEXT
    );
    """)

    # 6. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        full_name TEXT,
        role TEXT NOT NULL DEFAULT 'user',
        created_at TEXT NOT NULL
    );
    """)

    # 7. Reports Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id TEXT PRIMARY KEY,
        disaster_id TEXT NOT NULL,
        user_id TEXT,
        title TEXT NOT NULL,
        report_json TEXT NOT NULL,
        report_markdown TEXT NOT NULL,
        data_provenance TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (disaster_id) REFERENCES disasters (id) ON DELETE CASCADE
    );
    """)

    # 8. Notification Rules Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notification_rules (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        disaster_types TEXT NOT NULL DEFAULT 'all',
        min_severity TEXT NOT NULL DEFAULT 'MODERATE',
        min_confidence REAL NOT NULL DEFAULT 70.0,
        channels_json TEXT NOT NULL DEFAULT '["in_app"]',
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL
    );
    """)

    # 9. Notifications Log Table (with Idempotency Key)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications_log (
        id TEXT PRIMARY KEY,
        alert_id TEXT NOT NULL,
        event_id TEXT NOT NULL,
        channel TEXT NOT NULL,
        recipient TEXT,
        status TEXT NOT NULL DEFAULT 'DELIVERED', -- PENDING, DELIVERED, FAILED
        idempotency_key TEXT NOT NULL UNIQUE,
        failure_reason TEXT,
        sent_at TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    # 10. User Notification Preferences Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_preferences (
        user_id TEXT PRIMARY KEY,
        email TEXT,
        phone TEXT,
        disaster_types_json TEXT NOT NULL DEFAULT '["flood", "wildfire", "severe_weather"]',
        min_severity TEXT NOT NULL DEFAULT 'MODERATE',
        quiet_hours_enabled INTEGER NOT NULL DEFAULT 0,
        updated_at TEXT NOT NULL
    );
    """)

    # Indexes for performance and analytics
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_disasters_detection_time ON disasters(detection_time DESC);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_disasters_type_severity ON disasters(event_type, severity);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_disasters_created ON disasters(created_at DESC);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_created_status ON analysis_jobs(status, created_at DESC);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_created ON alerts(created_at DESC);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_event ON alerts(disaster_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_created ON reports(created_at DESC);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_notif_log_alert ON notifications_log(alert_id, status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_notif_log_idempotency ON notifications_log(idempotency_key);")

    # Safe Schema Migrations for existing databases
    existing_job_cols = [r["name"] for r in cursor.execute("PRAGMA table_info(analysis_jobs);").fetchall()]
    if "stage" not in existing_job_cols:
        cursor.execute("ALTER TABLE analysis_jobs ADD COLUMN stage TEXT DEFAULT 'queued';")
    if "progress" not in existing_job_cols:
        cursor.execute("ALTER TABLE analysis_jobs ADD COLUMN progress INTEGER DEFAULT 0;")
    if "user_id" not in existing_job_cols:
        cursor.execute("ALTER TABLE analysis_jobs ADD COLUMN user_id TEXT;")
    if "retry_count" not in existing_job_cols:
        cursor.execute("ALTER TABLE analysis_jobs ADD COLUMN retry_count INTEGER DEFAULT 0;")
    if "last_retry_at" not in existing_job_cols:
        cursor.execute("ALTER TABLE analysis_jobs ADD COLUMN last_retry_at TEXT;")

    conn.commit()
    conn.close()
