import concurrent.futures
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

from demo.precomputed_results import load_demo_result
from detection.pipeline import run_detection
from detection.result_contract import DetectionResultContract

DEFAULT_LIVE_TIMEOUT_SEC = float(os.getenv("LIVE_ANALYSIS_TIMEOUT_SEC", "10.0"))


class AnalysisTimeoutError(TimeoutError):
    """Raised when live analysis exceeds maximum configured execution time."""
    pass


class AnalysisModeController:
    """
    Controller for executing disaster analysis under isolated Instant Demo or Live Analyze modes.
    Enforces deterministic precomputed results for DEMO mode and timeout safeguards for LIVE mode.
    """

    def __init__(self, config_path: Optional[Union[str, Path]] = None, timeout_sec: float = DEFAULT_LIVE_TIMEOUT_SEC):
        """Initialize mode controller with configuration and timeout settings."""
        self.config_path = config_path
        self.timeout_sec = timeout_sec

    def run_analysis(
        self,
        event_id: str,
        mode: str = "INSTANT_DEMO",
        force_refresh: bool = False,
    ) -> DetectionResultContract:
        """
        Executes disaster analysis in the specified mode with timeout protection.

        :param event_id: Canonical event ID string.
        :param mode: Execution mode ('INSTANT_DEMO' or 'LIVE_ANALYZE').
        :param force_refresh: If True, bypasses caches in live mode.
        :return: DetectionResultContract object with mode metadata attached.
        """
        clean_mode = str(mode).upper().strip()
        if clean_mode not in {"INSTANT_DEMO", "LIVE_ANALYZE"}:
            raise ValueError(f"Invalid mode '{mode}'. Supported modes are 'INSTANT_DEMO' and 'LIVE_ANALYZE'.")

        if clean_mode == "INSTANT_DEMO":
            # Instant Demo Mode: zero-latency precomputed artifact load
            try:
                contract = load_demo_result(event_id)
            except Exception as e:
                # If demo artifact loading fails, return structured error contract
                return DetectionResultContract(
                    event_id=event_id,
                    disaster_type="flood",
                    status="failed",
                    timestamp="",
                    event_metadata={"analysis_mode": "INSTANT_DEMO"},
                    detection_summary={"mode_error": str(e)},
                    affected_area={},
                    severity={},
                    hotspots=[],
                    mask_reference={},
                    provenance={},
                    warnings=[f"Instant Demo Mode failed for '{event_id}': {str(e)}"],
                    limitations=["Precomputed demo bundle missing or corrupted."],
                )
        else:
            # Live Analyze Mode: full local pipeline execution with timeout protection
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    run_detection, event_id, mode="LIVE_ANALYZE", config_path=self.config_path
                )
                try:
                    contract = future.result(timeout=self.timeout_sec)
                except concurrent.futures.TimeoutError:
                    raise AnalysisTimeoutError(
                        f"Live analysis for event '{event_id}' timed out after {self.timeout_sec}s."
                    )

        # Attach mode tag to event_metadata for explicit labeling in UI/downstream consumers
        if contract and isinstance(contract.event_metadata, dict):
            contract.event_metadata["analysis_mode"] = clean_mode

        return contract


def execute_mode_analysis(
    event_id: str,
    mode: str = "INSTANT_DEMO",
    config_path: Optional[Union[str, Path]] = None,
    timeout_sec: float = DEFAULT_LIVE_TIMEOUT_SEC,
) -> DetectionResultContract:
    """Public helper API for mode controller analysis execution."""
    controller = AnalysisModeController(config_path=config_path, timeout_sec=timeout_sec)
    return controller.run_analysis(event_id, mode=mode)
