"""
NIRVAAN Structured Logging & Request Correlation Engine (utils/logging.py)

Provides request correlation IDs (X-Request-ID) and structured JSON logging across FastAPI,
background job workers, database queries, and ML inference operations.
"""

import contextvars
import json
import logging
import time
from typing import Any, Dict, Optional
import uuid

_request_id_ctx_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")
_job_id_ctx_var: contextvars.ContextVar[str] = contextvars.ContextVar("job_id", default="")
_user_id_ctx_var: contextvars.ContextVar[str] = contextvars.ContextVar("user_id", default="")


def set_request_id(req_id: Optional[str] = None) -> str:
    """Sets or generates a request correlation ID for current context."""
    val = req_id or f"req-{uuid.uuid4().hex[:12]}"
    _request_id_ctx_var.set(val)
    return val


def get_request_id() -> str:
    """Returns current context request ID."""
    return _request_id_ctx_var.get() or f"req-{uuid.uuid4().hex[:12]}"


def set_job_id(job_id: str) -> None:
    """Sets job ID in current execution context."""
    _job_id_ctx_var.set(job_id)


def get_job_id() -> str:
    """Returns current context job ID."""
    return _job_id_ctx_var.get()


def set_user_id(user_id: str) -> None:
    """Sets user ID in current execution context."""
    _user_id_ctx_var.set(user_id)


def get_user_id() -> str:
    """Returns current context user ID."""
    return _user_id_ctx_var.get()


class NirvaanJsonFormatter(logging.Formatter):
    """Formats log records into structured JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": get_request_id(),
        }
        job_id = get_job_id()
        if job_id:
            log_obj["job_id"] = job_id
        user_id = get_user_id()
        if user_id:
            log_obj["user_id"] = user_id

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


def configure_nirvaan_logging(level: int = logging.INFO) -> None:
    """Configures root NIRVAAN logger with structured JSON output."""
    root = logging.getLogger("nirvaan")
    root.setLevel(level)
    if not root.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(NirvaanJsonFormatter())
        root.addHandler(handler)
