"""
NIRVAAN Disaster Event Schema

Provides typed and validated schemas for satellite disaster events.
Supports 'flood' and 'wildfire' disaster types with provenance tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import re


SUPPORTED_DISASTER_TYPES = {"flood", "wildfire"}


class EventValidationError(ValueError):
    """Raised when disaster event metadata fails validation."""
    pass


class UnsupportedDisasterTypeError(EventValidationError):
    """Raised when an unsupported disaster type is provided."""
    pass


@dataclass
class DisasterEvent:
    """
    Typed and validated representation of a NIRVAAN disaster event.
    """
    event_id: str
    disaster_type: str
    location_name: str
    latitude: Optional[float]
    longitude: Optional[float]
    before_image: Union[str, Path]
    after_image: Union[str, Path]
    before_date: str
    after_date: str
    source: str
    CRS: str
    resolution_m: float
    available_bands: Union[List[str], Dict[str, str]]
    product_id: Optional[str] = None
    source_url: Optional[str] = None
    provenance_url: Optional[str] = None
    tile_id: Optional[str] = None
    satellite_platform: Optional[str] = None
    processing_level: Optional[str] = None
    spectral_index: Optional[str] = None
    spectral_formula: Optional[str] = None
    aoi: Optional[Dict[str, Any]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.validate()

    def validate(self) -> None:
        """
        Validates event metadata against NIRVAAN contract rules.
        Raises EventValidationError or UnsupportedDisasterTypeError if invalid.
        """
        # 1. Event ID
        if not self.event_id or not isinstance(self.event_id, str):
            raise EventValidationError("event_id must be a non-empty string.")

        # 2. Disaster Type
        if not self.disaster_type or not isinstance(self.disaster_type, str):
            raise EventValidationError("disaster_type must be a non-empty string.")
        
        normalized_type = self.disaster_type.lower().strip()
        if normalized_type not in SUPPORTED_DISASTER_TYPES:
            raise UnsupportedDisasterTypeError(
                f"Disaster type '{self.disaster_type}' is unsupported. "
                f"Must be one of: {sorted(list(SUPPORTED_DISASTER_TYPES))}"
            )
        self.disaster_type = normalized_type

        # 3. Location Name
        if not self.location_name or not isinstance(self.location_name, str):
            raise EventValidationError("location_name must be a non-empty string.")

        # 4. Latitude & Longitude
        if self.latitude is not None:
            try:
                lat = float(self.latitude)
                if not (-90.0 <= lat <= 90.0):
                    raise EventValidationError(f"latitude {lat} is out of range [-90, 90].")
                self.latitude = lat
            except (ValueError, TypeError):
                raise EventValidationError(f"Invalid latitude value: {self.latitude}")

        if self.longitude is not None:
            try:
                lon = float(self.longitude)
                if not (-180.0 <= lon <= 180.0):
                    raise EventValidationError(f"longitude {lon} is out of range [-180, 180].")
                self.longitude = lon
            except (ValueError, TypeError):
                raise EventValidationError(f"Invalid longitude value: {self.longitude}")

        # 5. Dates
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        for date_field, date_val in [("before_date", self.before_date), ("after_date", self.after_date)]:
            if not date_val or not isinstance(date_val, str) or not date_pattern.match(date_val):
                raise EventValidationError(f"{date_field} must be a valid date string in YYYY-MM-DD format.")
            try:
                datetime.strptime(date_val, "%Y-%m-%d")
            except ValueError:
                raise EventValidationError(f"{date_field} '{date_val}' is an invalid calendar date.")

        # 6. Images / Paths
        if not self.before_image or (isinstance(self.before_image, str) and not self.before_image.strip()):
            raise EventValidationError("before_image path must be provided.")
        if not self.after_image or (isinstance(self.after_image, str) and not self.after_image.strip()):
            raise EventValidationError("after_image path must be provided.")

        self.before_image = Path(self.before_image)
        self.after_image = Path(self.after_image)

        # 7. Source / Provenance
        if not self.source or not isinstance(self.source, str):
            raise EventValidationError("source provider/provenance must be a non-empty string.")

        # 8. CRS
        if not self.CRS or not isinstance(self.CRS, str):
            raise EventValidationError("CRS (Coordinate Reference System) must be a non-empty string.")

        # 9. Resolution
        try:
            res = float(self.resolution_m)
            if res <= 0:
                raise EventValidationError(f"resolution_m must be positive, got {res}")
            self.resolution_m = res
        except (ValueError, TypeError):
            raise EventValidationError(f"Invalid resolution_m value: {self.resolution_m}")

        # 10. Available Bands
        if not self.available_bands:
            raise EventValidationError("available_bands must be a non-empty list or dict.")

    def to_dict(self) -> Dict[str, Any]:
        """Serializes event to a standard python dictionary."""
        return {
            "event_id": self.event_id,
            "disaster_type": self.disaster_type,
            "location_name": self.location_name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "before_image": str(self.before_image),
            "after_image": str(self.after_image),
            "before_date": self.before_date,
            "after_date": self.after_date,
            "source": self.source,
            "product_id": self.product_id,
            "source_url": self.source_url,
            "provenance_url": self.provenance_url,
            "tile_id": self.tile_id,
            "satellite_platform": self.satellite_platform,
            "processing_level": self.processing_level,
            "CRS": self.CRS,
            "resolution_m": self.resolution_m,
            "available_bands": self.available_bands,
            "spectral_index": self.spectral_index,
            "spectral_formula": self.spectral_formula,
            "aoi": self.aoi,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DisasterEvent":
        """Constructs and validates a DisasterEvent instance from raw dictionary data."""
        if not isinstance(data, dict):
            raise EventValidationError("Event metadata input must be a dictionary.")

        # Map common alias field names
        event_id = data.get("event_id")
        disaster_type = data.get("disaster_type")
        location_name = data.get("location_name") or data.get("event_name")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        
        # Local paths resolution
        local_paths = data.get("local_paths", {})
        before_image = (
            data.get("before_image")
            or local_paths.get("before_dir")
            or local_paths.get("before_path")
        )
        after_image = (
            data.get("after_image")
            or local_paths.get("after_dir")
            or local_paths.get("after_path")
        )
        
        before_date = data.get("before_date")
        after_date = data.get("after_date")
        source = data.get("source") or data.get("source_provider")
        crs = data.get("CRS") or data.get("coordinate_reference_system")
        resolution_m = data.get("resolution_m")
        available_bands = data.get("available_bands") or data.get("required_bands")
        
        product_id = (
            data.get("product_id")
            or data.get("before_product_id")
            or data.get("after_product_id")
        )
        source_url = data.get("source_url")
        provenance_url = data.get("provenance_url")
        tile_id = data.get("tile_id")
        satellite_platform = data.get("satellite_platform")
        processing_level = data.get("processing_level")
        spectral_index = data.get("spectral_index")
        spectral_formula = data.get("spectral_formula")
        aoi = data.get("aoi", {})
        
        # Store unmapped fields in metadata dict
        reserved_keys = {
            "event_id", "disaster_type", "location_name", "event_name", "latitude", "longitude",
            "before_image", "after_image", "local_paths", "before_date", "after_date", "source",
            "source_provider", "CRS", "coordinate_reference_system", "resolution_m",
            "available_bands", "required_bands", "product_id", "before_product_id", "after_product_id",
            "source_url", "provenance_url", "tile_id", "satellite_platform", "processing_level",
            "spectral_index", "spectral_formula", "aoi"
        }
        extra_metadata = {k: v for k, v in data.items() if k not in reserved_keys}

        return cls(
            event_id=event_id,
            disaster_type=disaster_type,
            location_name=location_name,
            latitude=latitude,
            longitude=longitude,
            before_image=before_image,
            after_image=after_image,
            before_date=before_date,
            after_date=after_date,
            source=source,
            CRS=crs,
            resolution_m=resolution_m,
            available_bands=available_bands,
            product_id=product_id,
            source_url=source_url,
            provenance_url=provenance_url,
            tile_id=tile_id,
            satellite_platform=satellite_platform,
            processing_level=processing_level,
            spectral_index=spectral_index,
            spectral_formula=spectral_formula,
            aoi=aoi,
            metadata=extra_metadata,
        )
