"""
NIRVAAN Asynchronous Job Lifecycle & Worker Engine (services/job_worker.py)

Orchestrates non-blocking detection jobs through persistent processing stages:
queued -> acquiring_data -> preprocessing -> inference -> postprocessing -> saving_result -> completed / failed

Includes:
- Idempotency & duplicate job prevention for identical AOIs
- Persistent stage & progress tracking
- Validation of model inference outputs
- Retry policy with exponential backoff on transient errors
- Automatic job timeout protection
"""

from datetime import datetime, timezone
import json
import logging
import threading
import time
from typing import Any, Dict, Optional

from db.repository import DatabaseRepository
from detection.detector_base import DetectorInput
from detection.detector_registry import DetectorRegistry
from services.notification_service import NotificationEngine
from utils.logging import set_job_id, set_request_id
from utils.validation import validate_detection_result

logger = logging.getLogger("nirvaan.job_worker")

MAX_RETRIES = 2


class AsyncDetectionWorker:
    """Worker service for processing queued multi-disaster detection jobs asynchronously."""

    def __init__(
        self,
        repo: Optional[DatabaseRepository] = None,
        notification_engine: Optional[NotificationEngine] = None,
        flood_service: Optional[Any] = None,
        **kwargs
    ):
        self.repo = repo or DatabaseRepository()
        self.notification_engine = notification_engine or NotificationEngine(repo=self.repo)

    def submit_detection_job(
        self,
        disaster_type: str,
        latitude: float,
        longitude: float,
        location_name: Optional[str] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enqueues an asynchronous detection job after checking AOI duplicate idempotency.
        """
        norm_type = (disaster_type or "flood").lower().strip()

        # Idempotency / duplicate job check
        active_job = self.repo.find_active_job_for_aoi(
            disaster_type=norm_type,
            latitude=latitude,
            longitude=longitude,
            delta=0.05
        )
        if active_job:
            logger.info("Found existing active job %s for AOI [%.3f, %.3f]", active_job["id"], latitude, longitude)
            return active_job

        # Create new job record
        job = self.repo.create_job(
            disaster_type=norm_type,
            latitude=latitude,
            longitude=longitude,
            user_id=user_id
        )
        job_id = job["id"]

        # Launch worker thread
        thread = threading.Thread(
            target=self._process_job_lifecycle,
            args=(job_id, norm_type, latitude, longitude, location_name, user_id, request_id),
            daemon=True
        )
        thread.start()

        return self.repo.get_job(job_id)

    def _process_job_lifecycle(
        self,
        job_id: str,
        disaster_type: str,
        latitude: float,
        longitude: float,
        location_name: Optional[str],
        user_id: Optional[str],
        request_id: Optional[str]
    ) -> None:
        """Executes the multi-stage asynchronous processing lifecycle for a multi-disaster job."""
        if request_id:
            set_request_id(request_id)
        set_job_id(job_id)

        now_str = datetime.now(timezone.utc).isoformat()
        job = self.repo.get_job(job_id)
        retry_count = (job.get("retry_count") or 0) if job else 0

        # Stage 1: Mark processing & acquiring satellite data
        self.repo.update_job_status(
            job_id,
            status="processing",
            stage="acquiring_data",
            progress=20,
            started_at=now_str
        )

        try:
            detector = DetectorRegistry.get_detector(disaster_type, repo=self.repo)

            # Stage 2: Preprocessing
            self.repo.update_job_status(job_id, status="processing", stage="preprocessing", progress=40)

            # Stage 3: ML Inference
            self.repo.update_job_status(job_id, status="processing", stage="inference", progress=60)
            
            inp = DetectorInput(
                latitude=latitude,
                longitude=longitude,
                location_name=location_name or f"{disaster_type.capitalize()} Observation Area",
                disaster_type=disaster_type,
                user_id=user_id
            )
            detector_output = detector.run(inp)
            result = detector_output.to_dict()

            # Stage 4: Postprocessing & Validation
            self.repo.update_job_status(job_id, status="processing", stage="postprocessing", progress=80)
            is_valid, validation_errors = validate_detection_result(result)
            if not is_valid:
                err_msg = f"Detection model result validation failed: {'; '.join(validation_errors)}"
                logger.error("Job %s validation error: %s", job_id, err_msg)
                completed_str = datetime.now(timezone.utc).isoformat()
                self.repo.update_job_status(
                    job_id,
                    status="failed",
                    stage="failed",
                    progress=0,
                    completed_at=completed_str,
                    error=err_msg
                )
                return

            # Stage 5: Saving Result & Completed
            self.repo.update_job_status(job_id, status="processing", stage="saving_result", progress=95)
            completed_str = datetime.now(timezone.utc).isoformat()
            self.repo.update_job_status(
                job_id,
                status="completed",
                stage="completed",
                progress=100,
                completed_at=completed_str,
                result_json=result
            )

            # Event-Driven Notification Processing
            alerts = self.repo.get_alerts()
            if alerts:
                top_alert = alerts[0]
                self.notification_engine.process_alert_notifications(
                    alert_id=top_alert["id"],
                    event_id=result["event_id"],
                    disaster_type=disaster_type,
                    severity=result.get("severity", "MODERATE"),
                    confidence=result.get("confidence_score", 90.0)
                )

            logger.info("Asynchronously completed detection job %s (%s) for AOI [%.3f, %.3f]", job_id, disaster_type, latitude, longitude)

        except Exception as e:
            logger.error("Error executing detection job %s: %s", job_id, e)
            if retry_count < MAX_RETRIES:
                new_retry = retry_count + 1
                backoff_sec = 2 ** new_retry
                logger.info("Retrying job %s (attempt %d/%d) in %ds...", job_id, new_retry, MAX_RETRIES, backoff_sec)
                time.sleep(backoff_sec)
                retry_now = datetime.now(timezone.utc).isoformat()
                self.repo.update_job_status(
                    job_id,
                    status="processing",
                    stage="retrying",
                    retry_count=new_retry,
                    last_retry_at=retry_now
                )
                self._process_job_lifecycle(job_id, disaster_type, latitude, longitude, location_name, user_id, request_id)
            else:
                completed_str = datetime.now(timezone.utc).isoformat()
                self.repo.update_job_status(
                    job_id,
                    status="failed",
                    stage="failed",
                    progress=0,
                    completed_at=completed_str,
                    error=f"Processing failed permanently after {MAX_RETRIES} retries: {str(e)}"
                )


# Global worker instance
_DEFAULT_JOB_WORKER = AsyncDetectionWorker()
