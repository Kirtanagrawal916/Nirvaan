"""
NIRVAAN Analysis Mode Controller Module (TASK-020)

Implements two explicit analysis modes:
1. Instant Demo Mode (Default): Loads precomputed bundle with zero latency and offline guarantee.
2. Live Analyze Mode (Secondary): Executes full end-to-end processing pipeline on imagery.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Union

from demo.precomputed_results import load_demo_result
from detection.pipeline import run_detection
from detection.result_contract import DetectionResultContract


class AnalysisModeController:
    """
    Controller for executing disaster analysis under explicit Instant Demo or Live Analyze modes.
    """

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """Initialize mode controller with configuration."""
        self.config_path = config_path

    def run_analysis(
        self,
        event_id: str,
        mode: str = "INSTANT_DEMO",
        force_refresh: bool = False,
    ) -> DetectionResultContract:
        """
        Executes disaster analysis in the specified mode.

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
                # If demo artifact loading fails, return structured error contract (never silent fallback)
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
            # Live Analyze Mode: full local pipeline execution
            contract = run_detection(event_id, mode="LIVE_ANALYZE", config_path=self.config_path)

        # Attach mode tag to event_metadata for explicit labeling in UI/downstream consumers
        if contract and isinstance(contract.event_metadata, dict):
            contract.event_metadata["analysis_mode"] = clean_mode

        return contract


def execute_mode_analysis(
    event_id: str,
    mode: str = "INSTANT_DEMO",
    config_path: Optional[Union[str, Path]] = None,
) -> DetectionResultContract:
    """Public helper API for mode controller analysis execution."""
    controller = AnalysisModeController(config_path=config_path)
    return controller.run_analysis(event_id, mode=mode)
