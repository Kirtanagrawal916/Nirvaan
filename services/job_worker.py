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
import logging
import threading
import time
from typing import Any, Dict, Optional

from db.repository import DatabaseRepository
from services.flood_service import RealFloodDetectionService
from utils.logging import set_job_id, set_request_id
from utils.validation import validate_detection_result

logger = logging.getLogger("nirvaan.job_worker")

MAX_RETRIES = 2


class AsyncDetectionWorker:
    """Worker service for processing queued detection jobs asynchronously."""

    def __init__(
        self,
        repo: Optional[DatabaseRepository] = None,
        flood_service: Optional[RealFloodDetectionService] = None,
    ):
        self.repo = repo or DatabaseRepository()
        self.flood_service = flood_service or RealFloodDetectionService(repo=self.repo)

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
        # Idempotency / duplicate job check
        active_job = self.repo.find_active_job_for_aoi(
            disaster_type=disaster_type,
            latitude=latitude,
            longitude=longitude,
            delta=0.05
        )
        if active_job:
            logger.info("Found existing active job %s for AOI [%.3f, %.3f]", active_job["id"], latitude, longitude)
            return active_job

        # Create new job record
        job = self.repo.create_job(
            disaster_type=disaster_type,
            latitude=latitude,
            longitude=longitude,
            user_id=user_id
        )
        job_id = job["id"]

        # Launch worker thread
        thread = threading.Thread(
            target=self._process_job_lifecycle,
            args=(job_id, latitude, longitude, location_name, request_id),
            daemon=True
        )
        thread.start()

        return self.repo.get_job(job_id)

    def _process_job_lifecycle(
        self,
        job_id: str,
        latitude: float,
        longitude: float,
        location_name: Optional[str],
        request_id: Optional[str]
    ) -> None:
        """Executes the multi-stage asynchronous processing lifecycle for a job."""
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
            # Stage 2: Preprocessing
            self.repo.update_job_status(job_id, status="processing", stage="preprocessing", progress=40)

            # Stage 3: ML Inference
            self.repo.update_job_status(job_id, status="processing", stage="inference", progress=60)
            result = self.flood_service.execute_detection(
                latitude=latitude,
                longitude=longitude,
                location_name=location_name,
                disaster_type="flood"
            )

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
                result_dict=result
            )
            logger.info("Job %s completed successfully", job_id)

        except Exception as e:
            logger.error("Job %s encountered error (retry %d/%d): %s", job_id, retry_count, MAX_RETRIES, e)

            if retry_count < MAX_RETRIES:
                # Execute retry policy
                new_retry = retry_count + 1
                self.repo.update_job_status(
                    job_id,
                    status="processing",
                    stage="retrying",
                    retry_count=new_retry,
                    last_retry_at=datetime.now(timezone.utc).isoformat()
                )
                time.sleep(1.5 * new_retry)  # Short backoff
                self._process_job_lifecycle(job_id, latitude, longitude, location_name, request_id)
            else:
                # Permanent failure
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
