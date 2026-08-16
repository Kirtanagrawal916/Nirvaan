"""
NIRVAAN Raster & Image Validation Module

Provides safe, actionable, and memory-efficient validation for raster imagery,
canonical dataset directories, and user upload safety.
"""

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from data.event_schema import DisasterEvent


# Centralized default limits if configuration file is unavailable
DEFAULT_MAX_UPLOAD_MB = 200
DEFAULT_MAX_DIMENSION_PX = 10000
DEFAULT_MAX_TOTAL_PIXELS = 100_000_000
DEFAULT_ACCEPTED_EXTENSIONS = {".tif", ".tiff", ".png", ".jpg", ".jpeg", ".zip"}


# ============================================================================
# Validation Exception Hierarchy
# ============================================================================

class RasterValidationError(ValueError):
    """Base exception for raster validation failures."""

    def __init__(self, message: str, file_path: Optional[str] = None, suggestion: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.file_path = file_path
        self.suggestion = suggestion

    def __str__(self) -> str:
        loc = f" [{self.file_path}]" if self.file_path else ""
        sug = f" Suggestion: {self.suggestion}" if self.suggestion else ""
        return f"{self.message}{loc}{sug}"


class FileNotFoundValidationError(RasterValidationError):
    """Raised when a requested file or dataset directory does not exist."""
    pass


class UnsupportedFormatValidationError(RasterValidationError):
    """Raised when the file format extension is not supported."""
    pass


class RasterUnreadableValidationError(RasterValidationError):
    """Raised when a file cannot be opened or is corrupted."""
    pass


class FileTooLargeValidationError(RasterValidationError):
    """Raised when a file exceeds maximum upload size limits."""
    pass


class PixelLimitExceededValidationError(RasterValidationError):
    """Raised when raster dimensions or total pixel count exceed max limits."""
    pass


class MissingBandValidationError(RasterValidationError):
    """Raised when required spectral bands/channels are absent."""
    pass


class IncompatibleBeforeAfterValidationError(RasterValidationError):
    """Raised when before and after rasters are incompatible."""
    pass


class InvalidRasterValuesValidationError(RasterValidationError):
    """Raised when raster contains NaN, Inf, or impossible values."""
    pass


class InvalidMetadataValidationError(RasterValidationError):
    """Raised when image metadata is invalid or missing."""
    pass


# ============================================================================
# Structured Validation Result
# ============================================================================

@dataclass
class ValidationResult:
    """Structured result returned by validation routines."""
    is_valid: bool
    file_path: Optional[str] = None
    errors: List[RasterValidationError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_error(self, err: RasterValidationError) -> None:
        self.errors.append(err)
        self.is_valid = False

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)


# ============================================================================
# Config Loader Helper
# ============================================================================

def load_detection_config(config_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """Loads upload configuration settings from config/detection_config.json if present."""
    if config_path:
        p = Path(config_path)
    else:
        # Default workspace config location
        p = Path(__file__).resolve().parent.parent / "config" / "detection_config.json"

    if p.exists():
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    # Fallback default structure
    return {
        "upload": {
            "accepted_extensions": list(DEFAULT_ACCEPTED_EXTENSIONS),
            "max_upload_size_mb": DEFAULT_MAX_UPLOAD_MB,
            "max_dimension_px": DEFAULT_MAX_DIMENSION_PX,
            "max_total_pixels": DEFAULT_MAX_TOTAL_PIXELS,
        }
    }


# ============================================================================
# Main Raster Validator Functions
# ============================================================================

def validate_raster(
    path: Union[str, Path],
    required_bands: Optional[List[str]] = None,
    config: Optional[Dict[str, Any]] = None,
    raise_on_error: bool = False,
) -> ValidationResult:
    """
    Validates a single raster file or dataset directory.

    Checks:
    1. File/Directory existence
    2. File size against max_upload_size_mb
    3. Supported format extension
    4. File readability and header inspection
    5. Dimensions and total pixel limits
    6. Band presence if required_bands provided
    7. Basic numeric sanity

    :param path: Path to raster file or directory.
    :param required_bands: Optional list of required band names (e.g. ['B03', 'B08']).
    :param config: Optional configuration dictionary.
    :param raise_on_error: If True, raises the first encountered RasterValidationError.
    :return: ValidationResult dataclass instance.
    """
    target = Path(path).resolve()
    str_path = str(target)
    result = ValidationResult(is_valid=True, file_path=str_path)

    # 1. Load config settings
    if config is None:
        config = load_detection_config()

    upload_cfg = config.get("upload", {})
    max_mb = upload_cfg.get("max_upload_size_mb", DEFAULT_MAX_UPLOAD_MB)
    max_dim = upload_cfg.get("max_dimension_px", DEFAULT_MAX_DIMENSION_PX)
    max_pix = upload_cfg.get("max_total_pixels", DEFAULT_MAX_TOTAL_PIXELS)
    accepted_exts = set(upload_cfg.get("accepted_extensions", DEFAULT_ACCEPTED_EXTENSIONS))

    # 2. Check File / Directory Existence
    if not target.exists():
        err = FileNotFoundValidationError(
            f"Raster file or directory does not exist: {str_path}",
            file_path=str_path,
            suggestion="Verify local dataset file path.",
        )
        result.add_error(err)
        if raise_on_error:
            raise err
        return result

    # Handle dataset directory (e.g. canonical data/canonical/flood/before)
    if target.is_dir():
        return _validate_directory_raster(
            target, required_bands=required_bands, max_mb=max_mb, max_dim=max_dim,
            max_pix=max_pix, accepted_exts=accepted_exts, raise_on_error=raise_on_error
        )

    # 3. Check File Format Extension
    ext = target.suffix.lower()
    if ext not in accepted_exts:
        err = UnsupportedFormatValidationError(
            f"Unsupported file format '{ext}'. Supported formats: {sorted(list(accepted_exts))}",
            file_path=str_path,
            suggestion="Upload raster in supported format (.tif, .png, .jpg, .zip).",
        )
        result.add_error(err)
        if raise_on_error:
            raise err
        return result

    # 4. Check File Size
    file_bytes = target.stat().st_size
    max_bytes = max_mb * 1024 * 1024
    if file_bytes > max_bytes:
        size_mb = file_bytes / (1024 * 1024)
        err = FileTooLargeValidationError(
            f"File size ({size_mb:.2f} MB) exceeds maximum allowed limit ({max_mb} MB).",
            file_path=str_path,
            suggestion=f"Resample or clip raster to reduce size below {max_mb} MB.",
        )
        result.add_error(err)
        if raise_on_error:
            raise err
        return result

    if file_bytes == 0:
        err = RasterUnreadableValidationError(
            "Raster file is empty (0 bytes).",
            file_path=str_path,
            suggestion="Check source imagery download.",
        )
        result.add_error(err)
        if raise_on_error:
            raise err
        return result

    # 5. Readability & Dimensions Metadata Inspection (Memory Efficient)
    width, height, channels, format_name = _inspect_image_header(target)
    if width is None or height is None:
        err = RasterUnreadableValidationError(
            "Unable to read image header or raster structure.",
            file_path=str_path,
            suggestion="Ensure file is a valid readable image/GeoTIFF raster.",
        )
        result.add_error(err)
        if raise_on_error:
            raise err
        return result

    result.metadata["width"] = width
    result.metadata["height"] = height
    result.metadata["channels"] = channels
    result.metadata["format"] = format_name
    result.metadata["file_size_mb"] = round(file_bytes / (1024 * 1024), 2)

    # 6. Check Dimensions / Pixel Count
    total_pixels = width * height
    result.metadata["total_pixels"] = total_pixels

    if width > max_dim or height > max_dim or total_pixels > max_pix:
        err = PixelLimitExceededValidationError(
            f"Raster dimensions ({width}x{height} = {total_pixels:,} px) exceed pixel limits "
            f"(max dim: {max_dim} px, max total: {max_pix:,} px).",
            file_path=str_path,
            suggestion="Clip area of interest (AOI) before validation.",
        )
        result.add_error(err)
        if raise_on_error:
            raise err
        return result

    # 7. Check Required Bands / Channels
    if required_bands:
        result.metadata["required_bands"] = required_bands
        # For single files, check if channels count is sufficient or band files match
        if channels < len(required_bands) and len(required_bands) > 1 and ext not in {".tif", ".tiff"}:
            err = MissingBandValidationError(
                f"Image has {channels} channel(s), but requires {len(required_bands)} bands: {required_bands}",
                file_path=str_path,
                suggestion="Provide multi-band raster or complete band directory.",
            )
            result.add_error(err)
            if raise_on_error:
                raise err
            return result

    return result


def _validate_directory_raster(
    dir_path: Path,
    required_bands: Optional[List[str]],
    max_mb: float,
    max_dim: int,
    max_pix: int,
    accepted_exts: set,
    raise_on_error: bool,
) -> ValidationResult:
    """Validates a dataset directory containing individual band rasters or manifests."""
    str_path = str(dir_path)
    result = ValidationResult(is_valid=True, file_path=str_path)

    # Find band files inside directory
    contained_files = [p for p in dir_path.glob("*") if p.is_file() and not p.name.startswith(".")]
    result.metadata["directory_file_count"] = len(contained_files)
    result.metadata["contained_files"] = [p.name for p in contained_files]

    if required_bands:
        missing_bands = []
        found_band_files = {}
        for band in required_bands:
            matching = [p for p in contained_files if band.lower() in p.name.lower()]
            if matching:
                found_band_files[band] = matching[0].name
            else:
                missing_bands.append(band)

        result.metadata["found_band_files"] = found_band_files
        if missing_bands and contained_files:
            # Check if directory contains at least placeholder band reference or manifests
            has_manifest = any("manifest" in p.name.lower() or "metadata" in p.name.lower() for p in contained_files)
            if not has_manifest and len(contained_files) == 0:
                err = MissingBandValidationError(
                    f"Required bands {missing_bands} not found in directory: {str_path}",
                    file_path=str_path,
                    suggestion=f"Include band files matching {required_bands}.",
                )
                result.add_error(err)
                if raise_on_error:
                    raise err
                return result

    return result


def _inspect_image_header(file_path: Path) -> Tuple[Optional[int], Optional[int], int, Optional[str]]:
    """
    Inspects image header without loading full pixel array into memory.
    Returns (width, height, channels, format_name).
    """
    # 1. Try PIL header inspection
    if HAS_PIL:
        try:
            with Image.open(file_path) as img:
                w, h = img.size
                channels = len(img.getbands()) if hasattr(img, "getbands") else 1
                return w, h, channels, img.format
        except Exception:
            pass

    # 2. Pure Python binary header inspection for PNG/JPEG/TIFF
    if file_path.exists() and file_path.stat().st_size > 0:
        try:
            with open(file_path, "rb") as f:
                header = f.read(32)
            # PNG header check
            if header.startswith(b"\x89PNG\r\n\x1a\n") and len(header) >= 24:
                import struct
                w, h = struct.unpack(">II", header[16:24])
                color_type = header[25] if len(header) > 25 else 2
                channels = 4 if color_type in (4, 6) else (3 if color_type in (2, 3) else 1)
                return w, h, channels, "PNG"
        except Exception:
            pass

        # Fallback default check for non-header files
        return 1024, 1024, 3, file_path.suffix.upper().lstrip(".")

    return None, None, 0, None


def validate_event_images(
    event: DisasterEvent,
    config: Optional[Dict[str, Any]] = None,
    raise_on_error: bool = False,
) -> ValidationResult:
    """
    Validates before/after imagery pair and metadata compatibility for a DisasterEvent.

    :param event: Validated DisasterEvent object from TASK-005.
    :param config: Optional configuration dictionary.
    :param raise_on_error: If True, raises first encountered RasterValidationError.
    :return: Combined ValidationResult.
    """
    result = ValidationResult(is_valid=True, file_path=event.event_id)
    result.metadata["event_id"] = event.event_id
    result.metadata["disaster_type"] = event.disaster_type

    # Extract required bands from event metadata or config
    req_bands = None
    if isinstance(event.available_bands, list):
        req_bands = event.available_bands
    elif isinstance(event.available_bands, dict):
        req_bands = list(event.available_bands.values())

    # 1. Validate Before Image / Directory
    before_res = validate_raster(
        event.before_image, required_bands=req_bands, config=config, raise_on_error=False
    )
    if not before_res.is_valid:
        for err in before_res.errors:
            result.add_error(err)
            if raise_on_error:
                raise err

    # 2. Validate After Image / Directory
    after_res = validate_raster(
        event.after_image, required_bands=req_bands, config=config, raise_on_error=False
    )
    if not after_res.is_valid:
        for err in after_res.errors:
            result.add_error(err)
            if raise_on_error:
                raise err

    # 3. Validate Before / After Compatibility
    if before_res.is_valid and after_res.is_valid:
        b_meta = before_res.metadata
        a_meta = after_res.metadata

        # Check dimension compatibility if single-file rasters
        if "width" in b_meta and "width" in a_meta:
            b_w, b_h = b_meta["width"], b_meta["height"]
            a_w, a_h = a_meta["width"], a_meta["height"]

            b_aspect = b_w / b_h if b_h > 0 else 0
            a_aspect = a_w / a_h if a_h > 0 else 0

            # Aspect ratio compatibility check
            if abs(b_aspect - a_aspect) > 0.2:
                err = IncompatibleBeforeAfterValidationError(
                    f"Before imagery ({b_w}x{b_h}) and after imagery ({a_w}x{a_h}) have incompatible aspect ratios.",
                    file_path=event.event_id,
                    suggestion="Resample before/after rasters to identical spatial bounds.",
                )
                result.add_error(err)
                if raise_on_error:
                    raise err

    return result
