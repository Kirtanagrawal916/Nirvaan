"""
NIRVAAN Dataset Loader

Loads and validates canonical disaster events from catalog and metadata files.
Exposes a clean public interface for downstream modules.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from data.event_schema import (
    DisasterEvent,
    EventValidationError,
    UnsupportedDisasterTypeError,
)


class DatasetCatalogError(FileNotFoundError):
    """Raised when the catalog file is missing or invalid."""
    pass


class EventNotFoundError(KeyError):
    """Raised when an requested event_id is not found in the catalog."""
    pass


class MissingFileError(FileNotFoundError):
    """Raised when required local dataset files/directories are missing."""
    pass


class DatasetLoader:
    """
    Loader class for loading and validating NIRVAAN disaster events.
    """

    def __init__(
        self,
        catalog_path: Optional[Union[str, Path]] = None,
        base_dir: Optional[Union[str, Path]] = None,
        verify_files: bool = True,
    ):
        """
        Initialize DatasetLoader.

        :param catalog_path: Path to data/catalog.json file.
        :param base_dir: Base directory for resolving relative dataset paths.
        :param verify_files: Whether to check local file existence.
        """
        if base_dir:
            self.base_dir = Path(base_dir).resolve()
        else:
            # Default base directory is workspace root (parent of data/)
            self.base_dir = Path(__file__).resolve().parent.parent

        if catalog_path:
            self.catalog_path = Path(catalog_path).resolve()
        else:
            self.catalog_path = self.base_dir / "data" / "catalog.json"

        self.verify_files = verify_files
        self._catalog_cache: Optional[Dict[str, Any]] = None

    def _load_catalog(self) -> Dict[str, Any]:
        """Loads and caches the raw JSON catalog."""
        if self._catalog_cache is not None:
            return self._catalog_cache

        if not self.catalog_path.exists():
            raise DatasetCatalogError(
                f"Dataset catalog file not found at: {self.catalog_path}"
            )

        try:
            with open(self.catalog_path, "r", encoding="utf-8") as f:
                catalog_data = json.load(f)
        except json.JSONDecodeError as err:
            raise DatasetCatalogError(
                f"Invalid catalog JSON format in {self.catalog_path}: {err}"
            )

        if not isinstance(catalog_data, dict) or "canonical_events" not in catalog_data:
            raise DatasetCatalogError(
                f"Catalog JSON in {self.catalog_path} must contain 'canonical_events' list."
            )

        self._catalog_cache = catalog_data
        return catalog_data

    def list_events(self) -> List[Dict[str, Any]]:
        """Returns metadata summaries for all events registered in the catalog."""
        catalog = self._load_catalog()
        events = catalog.get("canonical_events", [])
        return [
            {
                "event_id": item.get("event_id"),
                "disaster_type": item.get("disaster_type"),
                "event_name": item.get("event_name"),
                "location_name": item.get("location_name"),
                "before_date": item.get("before_date"),
                "after_date": item.get("after_date"),
            }
            for item in events
        ]

    def get_raw_event_data(self, event_id: str) -> Dict[str, Any]:
        """Fetches raw dictionary entry for an event_id from catalog."""
        catalog = self._load_catalog()
        events = catalog.get("canonical_events", [])
        for item in events:
            if item.get("event_id") == event_id:
                return item
        raise EventNotFoundError(f"Event ID '{event_id}' not found in catalog.")

    def load_event(self, event_id: str) -> DisasterEvent:
        """
        Loads, resolves paths, and validates a DisasterEvent instance.

        :param event_id: Identifier of the event to load (e.g. 'flood-emilia-romagna-2023').
        :return: Validated DisasterEvent instance.
        """
        raw_data = self.get_raw_event_data(event_id)

        # Copy data to prevent mutating cache
        event_dict = dict(raw_data)

        # Resolve local paths relative to base_dir
        local_paths = event_dict.get("local_paths", {})
        before_raw = event_dict.get("before_image") or local_paths.get("before_dir") or local_paths.get("before_path")
        after_raw = event_dict.get("after_image") or local_paths.get("after_dir") or local_paths.get("after_path")

        if before_raw:
            before_path = Path(before_raw)
            if not before_path.is_absolute():
                before_path = self.base_dir / before_path
            event_dict["before_image"] = before_path

        if after_raw:
            after_path = Path(after_raw)
            if not after_path.is_absolute():
                after_path = self.base_dir / after_path
            event_dict["after_image"] = after_path

        # Instantiate & validate schema
        event = DisasterEvent.from_dict(event_dict)

        # Verify local file paths if requested
        if self.verify_files:
            self._verify_event_files(event)

        return event

    def _verify_event_files(self, event: DisasterEvent) -> None:
        """Verifies that resolved local paths exist on disk."""
        before_p = Path(event.before_image)
        after_p = Path(event.after_image)

        if not before_p.exists():
            raise MissingFileError(
                f"Resolved before_image path for event '{event.event_id}' does not exist: {before_p}"
            )

        if not after_p.exists():
            raise MissingFileError(
                f"Resolved after_image path for event '{event.event_id}' does not exist: {after_p}"
            )


# Global helper functions for simple API calls
_DEFAULT_LOADER = DatasetLoader()


def load_event(event_id: str, catalog_path: Optional[Union[str, Path]] = None, verify_files: bool = True) -> DisasterEvent:
    """
    Public function API to load and validate a NIRVAAN disaster event.

    :param event_id: Identifier of event to load.
    :param catalog_path: Optional custom path to catalog.json.
    :param verify_files: Whether to check local dataset file existence.
    :return: Validated DisasterEvent instance.
    """
    if catalog_path:
        loader = DatasetLoader(catalog_path=catalog_path, verify_files=verify_files)
        return loader.load_event(event_id)
    return _DEFAULT_LOADER.load_event(event_id)


def list_canonical_events(catalog_path: Optional[Union[str, Path]] = None) -> List[Dict[str, Any]]:
    """
    Public function API to list all available canonical disaster events.
    """
    if catalog_path:
        loader = DatasetLoader(catalog_path=catalog_path)
        return loader.list_events()
    return _DEFAULT_LOADER.list_events()
