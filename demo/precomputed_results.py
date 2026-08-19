"""
NIRVAAN Instant Demo / Precomputed Results Module (TASK-017)

Provides precomputed result generation and loading mechanisms for hackathon instant demo mode.
All precomputed artifacts are generated from the actual live detection pipeline (TASK-016).
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

from detection.pipeline import run_detection
from detection.result_contract import DetectionResultContract


DEFAULT_PRECOMPUTED_DIR = Path(__file__).resolve().parent.parent / "data" / "precomputed"


def generate_precomputed_artifacts(output_dir: Optional[Union[str, Path]] = None) -> Dict[str, Path]:
    """
    Executes live TASK-016 detection pipeline for canonical events and saves precomputed JSON artifacts.

    :param output_dir: Optional destination directory (defaults to data/precomputed).
    :return: Dictionary of event_id -> artifact Path.
    """
    target_dir = Path(output_dir) if output_dir else DEFAULT_PRECOMPUTED_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    canonical_events = ["flood-emilia-romagna-2023", "wildfire-rhodes-2023"]
    artifact_paths = {}

    for event_id in canonical_events:
        # Execute live pipeline to generate authentic contract
        contract = run_detection(event_id)
        if contract.status != "success":
            raise RuntimeError(f"Failed to generate precomputed artifact for '{event_id}': {contract.warnings}")

        file_path = target_dir / f"{event_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(contract.to_json(indent=2))

        artifact_paths[event_id] = file_path

    return artifact_paths


def load_demo_result(
    event_id: str, precomputed_dir: Optional[Union[str, Path]] = None
) -> DetectionResultContract:
    """
    Loads and validates a precomputed DetectionResultContract artifact for Instant Demo Mode.

    :param event_id: Canonical event ID string.
    :param precomputed_dir: Optional directory containing precomputed JSON artifacts.
    :return: Validated DetectionResultContract object.
    """
    target_dir = Path(precomputed_dir) if precomputed_dir else DEFAULT_PRECOMPUTED_DIR
    file_path = target_dir / f"{event_id}.json"

    if not file_path.exists():
        # Attempt generation on demand if precomputed artifact missing
        try:
            generate_precomputed_artifacts(output_dir=target_dir)
        except Exception as e:
            raise FileNotFoundError(
                f"Instant Demo artifact for event '{event_id}' not found at '{file_path}' "
                f"and auto-generation failed: {str(e)}"
            )

    if not file_path.exists():
        raise FileNotFoundError(f"Instant Demo artifact for event '{event_id}' not found at '{file_path}'")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise ValueError(f"Corrupted Instant Demo JSON artifact at '{file_path}': {str(e)}")

    # Validate contract structure and schema compatibility
    try:
        if isinstance(data, dict) and "data_provenance" not in data:
            data["data_provenance"] = "SYNTHETIC_FALLBACK"
        contract = DetectionResultContract.from_dict(data)
        contract.validate()
        return contract
    except Exception as e:
        raise ValueError(f"Instant Demo artifact for '{event_id}' failed schema validation: {str(e)}")
