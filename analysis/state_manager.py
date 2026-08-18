"""
NIRVAAN State Management & Caching Module (TASK-019)

Provides deterministic state management and caching helpers for NIRVAAN analysis runs.
Ensures session state preservation across reruns, efficient resource initialization,
and event state resetting without wiping global user configuration.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Union

from demo.precomputed_results import load_demo_result
from detection.pipeline import run_detection
from detection.result_contract import DetectionResultContract


# Try importing streamlit if available
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False


@dataclass
class AnalysisState:
    """
    State container for tracking active disaster analysis sessions.
    """
    selected_event_id: str = "flood-emilia-romagna-2023"
    selected_mode: str = "INSTANT_DEMO"  # 'INSTANT_DEMO' or 'LIVE_ANALYZE'
    current_result: Optional[DetectionResultContract] = None
    ui_stage: str = "DETECT"            # 'DETECT', 'COMPARE', 'MAP', 'ASSESS'
    is_analyzing: bool = False
    error_message: Optional[str] = None
    cached_contracts: Dict[str, DetectionResultContract] = field(default_factory=dict)

    def reset_event_state(self):
        """Resets event-specific analysis state while preserving selected_mode."""
        self.current_result = None
        self.ui_stage = "DETECT"
        self.is_analyzing = False
        self.error_message = None

    def set_event(self, event_id: str):
        """Updates selected event and resets event-specific result state if event changed."""
        if self.selected_event_id != event_id:
            self.selected_event_id = event_id
            self.reset_event_state()

    def set_mode(self, mode: str):
        """Updates analysis execution mode ('INSTANT_DEMO' or 'LIVE_ANALYZE')."""
        clean_mode = mode.upper().strip()
        if clean_mode not in {"INSTANT_DEMO", "LIVE_ANALYZE"}:
            raise ValueError(f"Invalid mode '{mode}'. Must be 'INSTANT_DEMO' or 'LIVE_ANALYZE'.")
        self.selected_mode = clean_mode

    def set_result(self, result: DetectionResultContract):
        """Stores result and updates cached results dictionary."""
        self.current_result = result
        self.error_message = None
        self.is_analyzing = False
        if result and result.status == "success":
            cache_key = f"{result.event_id}_{self.selected_mode}"
            self.cached_contracts[cache_key] = result

    def get_cached_result(self, event_id: str, mode: str) -> Optional[DetectionResultContract]:
        """Retrieves cached result contract if present."""
        cache_key = f"{event_id}_{mode.upper().strip()}"
        return self.cached_contracts.get(cache_key)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes summary state to dictionary."""
        return {
            "selected_event_id": self.selected_event_id,
            "selected_mode": self.selected_mode,
            "has_current_result": self.current_result is not None,
            "ui_stage": self.ui_stage,
            "is_analyzing": self.is_analyzing,
            "error_message": self.error_message,
            "cached_event_count": len(self.cached_contracts),
        }


def get_or_create_analysis_state(session_state_dict: Optional[Dict[str, Any]] = None) -> AnalysisState:
    """
    Retrieves existing AnalysisState from Streamlit session_state or dictionary,
    initializing one if missing.
    """
    if session_state_dict is not None:
        if "nirvaan_analysis_state" not in session_state_dict:
            session_state_dict["nirvaan_analysis_state"] = AnalysisState()
        return session_state_dict["nirvaan_analysis_state"]

    if HAS_STREAMLIT:
        if "nirvaan_analysis_state" not in st.session_state:
            st.session_state["nirvaan_analysis_state"] = AnalysisState()
        return st.session_state["nirvaan_analysis_state"]

    return AnalysisState()


def get_cached_detection_result(
    event_id: str,
    mode: str = "INSTANT_DEMO",
    config_path: Optional[Union[str, Path]] = None,
) -> DetectionResultContract:
    """
    Cached analysis loader. Loads precomputed result for INSTANT_DEMO mode,
    or executes live detection pipeline for LIVE_ANALYZE mode.
    """
    clean_mode = mode.upper().strip()

    if clean_mode == "INSTANT_DEMO":
        return load_demo_result(event_id)
    else:
        return run_detection(event_id, mode="LIVE_ANALYZE", config_path=config_path)
