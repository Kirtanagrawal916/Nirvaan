"""
NIRVAAN Database Repository Layer (db/repository.py)

Provides clean Python data access repository for disasters, satellite observations,
detections, alerts, and analysis jobs.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional, Union
import uuid

from db.database import get_db_connection, init_db


class DatabaseRepository:
    """
    Repository providing persistence methods for NIRVAAN data entities.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize repository and ensure schema tables exist."""
        self.db_path = db_path
        init_db(db_path=self.db_path)

    def _get_conn(self):
        return get_db_connection(self.db_path)

    def create_user(self, email: str, password_hash: str, full_name: Optional[str] = None, role: str = "user") -> Dict[str, Any]:
        """Creates a new user record in database."""
        user_id = f"usr-{uuid.uuid4().hex[:10]}"
        now = datetime.now(timezone.utc).isoformat()
        conn = get_db_connection(self.db_path)
        conn.execute(
            """
            INSERT INTO users (id, email, password_hash, full_name, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, email.lower().strip(), password_hash, full_name, role, now)
        )
        conn.commit()
        conn.close()
        return self.get_user_by_id(user_id)

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Retrieves single user by email."""
        conn = get_db_connection(self.db_path)
        row = conn.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email.lower().strip(),)).fetchone()
        conn.close()
        return dict(row) if row else None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves single user by ID."""
        conn = get_db_connection(self.db_path)
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def create_job(
        self,
        disaster_type: str,
        latitude: float,
        longitude: float,
        user_id: Optional[str] = None,
        model_version: str = "NIRVAAN-NDWI-v1.0"
    ) -> Dict[str, Any]:
        """Creates a new analysis job in queued status."""
        job_id = f"job-{uuid.uuid4().hex[:10]}"
        now = datetime.now(timezone.utc).isoformat()
        conn = get_db_connection(self.db_path)
        conn.execute(
            """
            INSERT INTO analysis_jobs (id, status, stage, progress, disaster_type, latitude, longitude, user_id, created_at, model_version)
            VALUES (?, 'queued', 'queued', 0, ?, ?, ?, ?, ?, ?)
            """,
            (job_id, disaster_type, latitude, longitude, user_id, now, model_version)
        )
        conn.commit()
        conn.close()
        return self.get_job(job_id)

    def find_active_job_for_aoi(self, disaster_type: str, latitude: float, longitude: float, delta: float = 0.05) -> Optional[Dict[str, Any]]:
        """Finds if a job with identical AOI is currently queued or processing."""
        conn = get_db_connection(self.db_path)
        row = conn.execute(
            """
            SELECT * FROM analysis_jobs
            WHERE disaster_type = ?
              AND status IN ('queued', 'processing')
              AND ABS(latitude - ?) < ?
              AND ABS(longitude - ?) < ?
            ORDER BY created_at DESC LIMIT 1
            """,
            (disaster_type, latitude, delta, longitude, delta)
        ).fetchone()
        conn.close()
        return self.get_job(row["id"]) if row else None

    def update_job_status(
        self,
        job_id: str,
        status: str,
        stage: Optional[str] = None,
        progress: Optional[int] = None,
        started_at: Optional[str] = None,
        completed_at: Optional[str] = None,
        error: Optional[str] = None,
        retry_count: Optional[int] = None,
        last_retry_at: Optional[str] = None,
        result_dict: Optional[Dict[str, Any]] = None,
        result_json: Optional[Union[Dict[str, Any], str]] = None,
        **kwargs
    ) -> None:
        """Updates job status, stage, progress, timestamps, error message, and result payload."""
        conn = get_db_connection(self.db_path)
        final_res = result_json if result_json is not None else result_dict
        if isinstance(final_res, dict):
            final_res_str = json.dumps(final_res)
        elif isinstance(final_res, str):
            final_res_str = final_res
        else:
            final_res_str = None

        conn.execute(
            """
            UPDATE analysis_jobs
            SET status = ?,
                stage = COALESCE(?, stage),
                progress = COALESCE(?, progress),
                started_at = COALESCE(?, started_at),
                completed_at = COALESCE(?, completed_at),
                error = COALESCE(?, error),
                retry_count = COALESCE(?, retry_count),
                last_retry_at = COALESCE(?, last_retry_at),
                result_json = COALESCE(?, result_json)
            WHERE id = ?
            """,
            (status, stage, progress, started_at, completed_at, error, retry_count, last_retry_at, final_res_str, job_id)
        )
        conn.commit()
        conn.close()

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves single job record by ID."""
        conn = get_db_connection(self.db_path)
        row = conn.execute("SELECT * FROM analysis_jobs WHERE id = ?", (job_id,)).fetchone()
        conn.close()
        if not row:
            return None
        res = dict(row)
        if res.get("result_json"):
            try:
                res["result"] = json.loads(res["result_json"])
            except Exception:
                res["result"] = {}
        return res

    def save_disaster(
        self,
        event_id: str,
        event_type: str,
        event_name: Optional[str] = None,
        location_name: Optional[str] = None,
        latitude: float = 0.0,
        longitude: float = 0.0,
        severity: str = "MODERATE",
        confidence: float = 90.0,
        source: str = "Sentinel-2 L2A STAC",
        satellite: str = "Sentinel-2",
        product_id: Optional[str] = None,
        acquisition_time: Optional[str] = None,
        detection_time: Optional[str] = None,
        model_version: str = "NIRVAAN-NDWI-v1.0",
        geometry_geojson: Optional[Union[Dict[str, Any], str]] = None,
        status: str = "Active",
        **kwargs
    ) -> Dict[str, Any]:
        """Saves or updates a disaster record in the database."""
        now = datetime.now(timezone.utc).isoformat()
        
        if isinstance(geometry_geojson, str):
            geom_json = geometry_geojson
        elif isinstance(geometry_geojson, dict):
            geom_json = json.dumps(geometry_geojson)
        else:
            geom_json = None

        final_loc = location_name or "Target Observation Area"
        final_name = event_name or f"{event_type.capitalize()} Event - {final_loc}"
        final_acq = acquisition_time or now
        final_det = detection_time or now

        conn = get_db_connection(self.db_path)
        conn.execute(
            """
            INSERT INTO disasters (
                id, event_type, event_name, location_name, geometry_geojson,
                latitude, longitude, severity, confidence, source, satellite,
                product_id, acquisition_time, detection_time, model_version, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                event_type=excluded.event_type,
                event_name=excluded.event_name,
                location_name=excluded.location_name,
                geometry_geojson=excluded.geometry_geojson,
                latitude=excluded.latitude,
                longitude=excluded.longitude,
                severity=excluded.severity,
                confidence=excluded.confidence,
                source=excluded.source,
                satellite=excluded.satellite,
                product_id=excluded.product_id,
                acquisition_time=excluded.acquisition_time,
                detection_time=excluded.detection_time,
                model_version=excluded.model_version,
                status=excluded.status
            """,
            (
                event_id, event_type, final_name, final_loc, geom_json,
                latitude, longitude, severity, confidence, source, satellite,
                product_id, final_acq, final_det, model_version, status, now
            )
        )
        conn.commit()
        conn.close()
        return self.get_disaster(event_id)

    def get_disasters(
        self,
        limit: int = 50,
        offset: int = 0,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        status: Optional[str] = None,
        source_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Returns disasters with support for pagination and filtering."""
        conn = get_db_connection(self.db_path)
        query = "SELECT * FROM disasters WHERE 1=1"
        params: List[Any] = []

        if event_type:
            query += " AND LOWER(event_type) = ?"
            params.append(event_type.lower().strip())
        if severity:
            query += " AND UPPER(severity) = ?"
            params.append(severity.upper().strip())
        if status:
            query += " AND LOWER(status) = ?"
            params.append(status.lower().strip())
        if from_date:
            query += " AND detection_time >= ?"
            params.append(from_date)
        if to_date:
            query += " AND detection_time <= ?"
            params.append(to_date)
        if source_type:
            if source_type.lower() == "nirvaan":
                query += " AND (source LIKE '%NIRVAAN%' OR id LIKE 'flood-real-%' OR id LIKE 'NV-%')"
            elif source_type.lower() == "external":
                query += " AND NOT (source LIKE '%NIRVAAN%' OR id LIKE 'flood-real-%' OR id LIKE 'NV-%')"

        query += " ORDER BY detection_time DESC LIMIT ? OFFSET ?"
        params.extend([max(1, min(limit, 200)), max(0, offset)])

        rows = conn.execute(query, params).fetchall()
        conn.close()

        items = []
        for r in rows:
            d = dict(r)
            if d.get("geometry_geojson"):
                try:
                    d["geometry"] = json.loads(d["geometry_geojson"])
                except Exception:
                    d["geometry"] = None
            items.append(d)
        return items

    def save_report(
        self,
        disaster_id: str,
        title: str,
        report_json: Dict[str, Any],
        report_markdown: str,
        data_provenance: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Saves a generated SITREP report."""
        report_id = f"rpt-{uuid.uuid4().hex[:10]}"
        now = datetime.now(timezone.utc).isoformat()
        r_json = json.dumps(report_json)

        conn = get_db_connection(self.db_path)
        conn.execute(
            """
            INSERT INTO reports (id, disaster_id, user_id, title, report_json, report_markdown, data_provenance, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (report_id, disaster_id, user_id, title, r_json, report_markdown, data_provenance, now)
        )
        conn.commit()
        conn.close()
        return self.get_report(report_id)

    def get_reports(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Returns list of generated SITREP reports."""
        conn = get_db_connection(self.db_path)
        rows = conn.execute(
            "SELECT * FROM reports ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (max(1, min(limit, 200)), max(0, offset))
        ).fetchall()
        conn.close()
        items = []
        for r in rows:
            d = dict(r)
            if d.get("report_json"):
                try:
                    d["report_json"] = json.loads(d["report_json"])
                except Exception:
                    d["report_json"] = {}
            items.append(d)
        return items

    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves single SITREP report by ID."""
        conn = get_db_connection(self.db_path)
        row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
        conn.close()
        if not row:
            return None
        d = dict(row)
        if d.get("report_json"):
            try:
                d["report_json"] = json.loads(d["report_json"])
            except Exception:
                d["report_json"] = {}
        return d

    def get_disaster(self, disaster_id: str) -> Optional[Dict[str, Any]]:
        """Returns single disaster by ID."""
        conn = get_db_connection(self.db_path)
        row = conn.execute("SELECT * FROM disasters WHERE id = ?", (disaster_id,)).fetchone()
        conn.close()
        if not row:
            return None
        d = dict(row)
        if d.get("geometry_geojson"):
            try:
                d["geometry"] = json.loads(d["geometry_geojson"])
            except Exception:
                d["geometry"] = None
        return d

    def save_satellite_observation(
        self,
        scene_id: str,
        provider: str,
        satellite: str,
        sensor: str,
        cloud_cover: float,
        acquisition_time: str,
        bbox: List[float],
        source_url: str,
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Saves a satellite scene observation record."""
        obs_id = f"obs-{uuid.uuid4().hex[:10]}"
        now = datetime.now(timezone.utc).isoformat()
        bbox_json = json.dumps(bbox)
        meta_json = json.dumps(metadata)

        conn = get_db_connection(self.db_path)
        conn.execute(
            """
            INSERT INTO satellite_observations (
                id, provider, satellite, sensor, scene_id, cloud_cover,
                acquisition_time, bbox_json, source_url, metadata_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(scene_id) DO UPDATE SET
                cloud_cover=excluded.cloud_cover,
                acquisition_time=excluded.acquisition_time,
                metadata_json=excluded.metadata_json
            """,
            (obs_id, provider, satellite, sensor, scene_id, cloud_cover, acquisition_time, bbox_json, source_url, meta_json, now)
        )
        conn.commit()
        conn.close()
        return self.get_satellite_scene_by_scene_id(scene_id)

    def get_satellite_scenes(self) -> List[Dict[str, Any]]:
        """Returns list of all ingested satellite observations."""
        conn = get_db_connection(self.db_path)
        rows = conn.execute("SELECT * FROM satellite_observations ORDER BY acquisition_time DESC").fetchall()
        conn.close()
        items = []
        for r in rows:
            d = dict(r)
            if d.get("bbox_json"):
                try:
                    d["bbox"] = json.loads(d["bbox_json"])
                except Exception:
                    d["bbox"] = []
            if d.get("metadata_json"):
                try:
                    d["metadata"] = json.loads(d["metadata_json"])
                except Exception:
                    d["metadata"] = {}
            items.append(d)
        return items

    def get_satellite_scene_by_scene_id(self, scene_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves satellite observation by scene_id."""
        conn = get_db_connection(self.db_path)
        row = conn.execute("SELECT * FROM satellite_observations WHERE scene_id = ?", (scene_id,)).fetchone()
        conn.close()
        if not row:
            return None
        d = dict(row)
        if d.get("bbox_json"):
            try:
                d["bbox"] = json.loads(d["bbox_json"])
            except Exception:
                d["bbox"] = []
        if d.get("metadata_json"):
            try:
                d["metadata"] = json.loads(d["metadata_json"])
            except Exception:
                d["metadata"] = {}
        return d

    def create_alert_if_needed(
        self,
        disaster_id: str,
        event_type: str,
        severity: str,
        location: str,
        latitude: float,
        longitude: float,
        confidence: float,
        source: str,
        min_confidence: float = 80.0
    ) -> Optional[Dict[str, Any]]:
        """
        Creates an alert ONLY if confidence meets the min_confidence threshold.
        """
        if confidence < min_confidence:
            return None

        alert_id = f"ALT-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now(timezone.utc).isoformat()
        conn = get_db_connection(self.db_path)
        conn.execute(
            """
            INSERT INTO alerts (id, disaster_id, event_type, severity, location, latitude, longitude, confidence, source, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'UNREAD', ?)
            """,
            (alert_id, disaster_id, event_type, severity, location, latitude, longitude, confidence, source, now)
        )
        conn.commit()
        conn.close()
        return self.get_alert(alert_id)

    def save_alert(
        self,
        event_id: str,
        title: Optional[str] = None,
        severity: str = "MODERATE",
        location: str = "Observation Area",
        latitude: float = 0.0,
        longitude: float = 0.0,
        confidence: float = 90.0,
        source: str = "NIRVAAN Multi-Hazard Engine",
        **kwargs
    ) -> Dict[str, Any]:
        """Saves an alert directly into the alerts table."""
        alert_id = f"ALT-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now(timezone.utc).isoformat()
        disaster_type = kwargs.get("disaster_type") or kwargs.get("event_type") or ("wildfire" if "wildfire" in str(event_id).lower() else ("severe_weather" if "weather" in str(event_id).lower() or "cyclone" in str(event_id).lower() else "flood"))
        conn = get_db_connection(self.db_path)
        conn.execute(
            """
            INSERT INTO alerts (id, disaster_id, event_type, severity, location, latitude, longitude, confidence, source, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'UNREAD', ?)
            """,
            (alert_id, event_id, disaster_type, severity, location, latitude, longitude, confidence, source, now)
        )
        conn.commit()
        conn.close()
        return self.get_alert(alert_id)

    def get_alerts(self) -> List[Dict[str, Any]]:
        """Returns all registered alerts."""
        conn = get_db_connection(self.db_path)
        rows = conn.execute("SELECT * FROM alerts ORDER BY created_at DESC").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves alert by ID."""
        conn = get_db_connection(self.db_path)
        row = conn.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    # =========================================================
    # PHASE 3: NOTIFICATIONS & ALERT RULES
    # =========================================================

    def save_notification_rule(
        self,
        user_id: Optional[str],
        disaster_types: str = "all",
        min_severity: str = "MODERATE",
        min_confidence: float = 70.0,
        channels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Creates a configurable notification rule."""
        rule_id = f"rule-{uuid.uuid4().hex[:8]}"
        channels_json = json.dumps(channels or ["in_app"])
        now = datetime.now(timezone.utc).isoformat()
        conn = get_db_connection(self.db_path)
        conn.execute(
            """
            INSERT INTO notification_rules (id, user_id, disaster_types, min_severity, min_confidence, channels_json, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?)
            """,
            (rule_id, user_id, disaster_types, min_severity, min_confidence, channels_json, now)
        )
        conn.commit()
        row = conn.execute("SELECT * FROM notification_rules WHERE id = ?", (rule_id,)).fetchone()
        conn.close()
        return dict(row)

    def get_active_notification_rules(self) -> List[Dict[str, Any]]:
        """Retrieves all active notification rules."""
        conn = get_db_connection(self.db_path)
        rows = conn.execute("SELECT * FROM notification_rules WHERE is_active = 1").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def log_notification(
        self,
        alert_id: str,
        event_id: str,
        channel: str,
        recipient: Optional[str],
        status: str = "DELIVERED",
        failure_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Logs a sent notification with strict idempotency."""
        notif_id = f"notif-{uuid.uuid4().hex[:10]}"
        idempotency_key = f"{alert_id}:{channel}:{recipient or 'default'}"
        now = datetime.now(timezone.utc).isoformat()

        conn = get_db_connection(self.db_path)
        try:
            conn.execute(
                """
                INSERT INTO notifications_log (id, alert_id, event_id, channel, recipient, status, idempotency_key, failure_reason, sent_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (notif_id, alert_id, event_id, channel, recipient, status, idempotency_key, failure_reason, now, now)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            # Duplicate suppressed by idempotency key
            pass

        row = conn.execute("SELECT * FROM notifications_log WHERE idempotency_key = ?", (idempotency_key,)).fetchone()
        conn.close()
        return dict(row) if row else {}

    def is_notification_sent_for_alert(self, alert_id: str, channel: str, recipient: Optional[str] = None) -> bool:
        """Checks if a notification was already delivered for an alert/channel combo."""
        idempotency_key = f"{alert_id}:{channel}:{recipient or 'default'}"
        conn = get_db_connection(self.db_path)
        row = conn.execute("SELECT id FROM notifications_log WHERE idempotency_key = ?", (idempotency_key,)).fetchone()
        conn.close()
        return row is not None

    def has_any_notification_been_sent_for_alert(self, alert_id: str) -> bool:
        """Checks if any notification was already logged for this alert."""
        conn = get_db_connection(self.db_path)
        row = conn.execute("SELECT id FROM notifications_log WHERE alert_id = ?", (alert_id,)).fetchone()
        conn.close()
        return row is not None

    def save_user_preferences(
        self,
        user_id: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        disaster_types: Optional[List[str]] = None,
        min_severity: str = "MODERATE",
        quiet_hours_enabled: bool = False
    ) -> Dict[str, Any]:
        """Saves or updates user notification preferences."""
        types_json = json.dumps(disaster_types or ["flood", "wildfire", "severe_weather"])
        now = datetime.now(timezone.utc).isoformat()
        conn = get_db_connection(self.db_path)
        conn.execute(
            """
            INSERT INTO user_preferences (user_id, email, phone, disaster_types_json, min_severity, quiet_hours_enabled, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                email = coalesce(excluded.email, user_preferences.email),
                phone = coalesce(excluded.phone, user_preferences.phone),
                disaster_types_json = excluded.disaster_types_json,
                min_severity = excluded.min_severity,
                quiet_hours_enabled = excluded.quiet_hours_enabled,
                updated_at = excluded.updated_at
            """,
            (user_id, email, phone, types_json, min_severity, 1 if quiet_hours_enabled else 0, now)
        )
        conn.commit()
        row = conn.execute("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,)).fetchone()
        conn.close()
        return dict(row)

    def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves user notification preferences."""
        conn = get_db_connection(self.db_path)
        row = conn.execute("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    # =========================================================
    # PHASE 3: ADVANCED ANALYTICS AGGREGATION QUERIES
    # =========================================================

    def get_analytics_overview(self, days: int = 30) -> Dict[str, Any]:
        """Computes high-level aggregated disaster metrics across real database records."""
        conn = get_db_connection(self.db_path)
        
        total_events = conn.execute("SELECT COUNT(*) FROM disasters").fetchone()[0]
        active_alerts = conn.execute("SELECT COUNT(*) FROM alerts WHERE status = 'UNREAD'").fetchone()[0]
        avg_conf = conn.execute("SELECT AVG(confidence) FROM disasters").fetchone()[0] or 0.0
        
        # Severity breakdown
        sev_rows = conn.execute(
            "SELECT severity, COUNT(*) as cnt FROM disasters GROUP BY severity"
        ).fetchall()
        severity_dist = {r["severity"]: r["cnt"] for r in sev_rows}

        # Type breakdown
        type_rows = conn.execute(
            "SELECT event_type, COUNT(*) as cnt FROM disasters GROUP BY event_type"
        ).fetchall()
        type_dist = {r["event_type"]: r["cnt"] for r in type_rows}

        conn.close()
        return {
            "total_disasters_tracked": total_events,
            "active_unread_alerts": active_alerts,
            "average_detection_confidence": round(float(avg_conf), 1),
            "severity_distribution": severity_dist,
            "disaster_type_distribution": type_dist,
            "time_window_days": days,
            "data_provenance": "REAL_DATABASE_ANALYTICS"
        }

    def get_analytics_timeseries(self, days: int = 30) -> List[Dict[str, Any]]:
        """Aggregates disaster events over time intervals."""
        conn = get_db_connection(self.db_path)
        rows = conn.execute(
            """
            SELECT substr(created_at, 1, 10) as date_bucket,
                   COUNT(*) as event_count,
                   AVG(confidence) as avg_confidence,
                   event_type
            FROM disasters
            GROUP BY date_bucket, event_type
            ORDER BY date_bucket ASC
            LIMIT 60
            """
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_analytics_geographic_clusters(self) -> List[Dict[str, Any]]:
        """Groups real disaster detections by geographic location and severity."""
        conn = get_db_connection(self.db_path)
        rows = conn.execute(
            """
            SELECT location_name,
                   event_type,
                   ROUND(latitude, 2) as lat_cluster,
                   ROUND(longitude, 2) as lon_cluster,
                   COUNT(*) as event_count,
                   MAX(severity) as max_severity,
                   AVG(confidence) as avg_confidence
            FROM disasters
            GROUP BY lat_cluster, lon_cluster, event_type
            ORDER BY event_count DESC
            LIMIT 50
            """
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]


# Default instance
_DEFAULT_REPO = DatabaseRepository()
