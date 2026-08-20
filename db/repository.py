"""
NIRVAAN Database Repository Layer (db/repository.py)

Provides clean Python data access repository for disasters, satellite observations,
detections, alerts, and analysis jobs.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
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

    def create_job(self, disaster_type: str, latitude: float, longitude: float, model_version: str = "NIRVAAN-NDWI-v1.0") -> Dict[str, Any]:
        """Creates a new analysis job in queued status."""
        job_id = f"job-{uuid.uuid4().hex[:10]}"
        now = datetime.now(timezone.utc).isoformat()
        conn = get_db_connection(self.db_path)
        conn.execute(
            """
            INSERT INTO analysis_jobs (id, status, disaster_type, latitude, longitude, created_at, model_version)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (job_id, "queued", disaster_type, latitude, longitude, now, model_version)
        )
        conn.commit()
        conn.close()
        return self.get_job(job_id)

    def update_job_status(
        self,
        job_id: str,
        status: str,
        started_at: Optional[str] = None,
        completed_at: Optional[str] = None,
        error: Optional[str] = None,
        result_dict: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Updates job status, timestamps, error message, and result payload."""
        conn = get_db_connection(self.db_path)
        result_json = json.dumps(result_dict) if result_dict is not None else None

        conn.execute(
            """
            UPDATE analysis_jobs
            SET status = ?,
                started_at = COALESCE(?, started_at),
                completed_at = COALESCE(?, completed_at),
                error = COALESCE(?, error),
                result_json = COALESCE(?, result_json)
            WHERE id = ?
            """,
            (status, started_at, completed_at, error, result_json, job_id)
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
        event_name: str,
        location_name: str,
        latitude: float,
        longitude: float,
        severity: str,
        confidence: float,
        source: str,
        satellite: str,
        product_id: str,
        acquisition_time: str,
        detection_time: str,
        model_version: str,
        geometry_geojson: Optional[Dict[str, Any]] = None,
        status: str = "Active",
    ) -> Dict[str, Any]:
        """Saves or updates a disaster record in the database."""
        now = datetime.now(timezone.utc).isoformat()
        geom_json = json.dumps(geometry_geojson) if geometry_geojson else None

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
                event_id, event_type, event_name, location_name, geom_json,
                latitude, longitude, severity, confidence, source, satellite,
                product_id, acquisition_time, detection_time, model_version, status, now
            )
        )
        conn.commit()
        conn.close()
        return self.get_disaster(event_id)

    def get_disasters(self) -> List[Dict[str, Any]]:
        """Returns all registered disasters."""
        conn = get_db_connection(self.db_path)
        rows = conn.execute("SELECT * FROM disasters ORDER BY detection_time DESC").fetchall()
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


# Default instance
_DEFAULT_REPO = DatabaseRepository()
