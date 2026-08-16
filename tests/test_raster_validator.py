"""
Unit tests for NIRVAAN Raster & Image Validator (preprocessing/raster_validator.py)
"""

import os
import tempfile
import unittest
from pathlib import Path

from data.loader import load_event
from preprocessing.raster_validator import (
    FileNotFoundValidationError,
    FileTooLargeValidationError,
    IncompatibleBeforeAfterValidationError,
    MissingBandValidationError,
    PixelLimitExceededValidationError,
    RasterUnreadableValidationError,
    UnsupportedFormatValidationError,
    ValidationResult,
    validate_event_images,
    validate_raster,
)


class TestRasterValidator(unittest.TestCase):
    """Test suite for raster validation rules, upload safety, and canonical checks."""

    def setUp(self):
        # Create a small temporary valid PNG image file for testing
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.valid_png_path = Path(self.tmp_dir.name) / "test_valid.png"
        self.create_dummy_image(self.valid_png_path, size=(100, 100))

    def tearDown(self):
        self.tmp_dir.cleanup()

    def create_dummy_image(self, path: Path, size=(100, 100)):
        """Creates a dummy valid PNG file."""
        try:
            from PIL import Image
            img = Image.new("RGB", size, color="green")
            img.save(path)
        except ImportError:
            import struct
            w, h = size
            # Valid PNG header with IHDR chunk containing width and height
            png_header = (
                b"\x89PNG\r\n\x1a\n"
                + b"\x00\x00\x00\rIHDR"
                + struct.pack(">II", w, h)
                + b"\x08\x02\x00\x00\x00"
                + b"\x00" * 30
            )
            with open(path, "wb") as f:
                f.write(png_header)

    def test_valid_raster_passes(self):
        """Verify valid image file passes validation cleanly."""
        res = validate_raster(self.valid_png_path)
        self.assertTrue(res.is_valid)
        self.assertEqual(len(res.errors), 0)

    def test_missing_file_fails(self):
        """Verify non-existent file path fails with FileNotFoundValidationError."""
        res = validate_raster("data/non_existent_file_xyz.png")
        self.assertFalse(res.is_valid)
        self.assertIsInstance(res.errors[0], FileNotFoundValidationError)

    def test_unreadable_corrupt_raster_fails(self):
        """Verify 0-byte corrupt file fails with RasterUnreadableValidationError."""
        corrupt_path = Path(self.tmp_dir.name) / "corrupt.png"
        corrupt_path.touch()  # 0 bytes
        res = validate_raster(corrupt_path)
        self.assertFalse(res.is_valid)
        self.assertIsInstance(res.errors[0], RasterUnreadableValidationError)

    def test_unsupported_format_fails(self):
        """Verify unsupported file extension fails with UnsupportedFormatValidationError."""
        bad_ext_path = Path(self.tmp_dir.name) / "test.exe"
        bad_ext_path.write_text("dummy")
        res = validate_raster(bad_ext_path)
        self.assertFalse(res.is_valid)
        self.assertIsInstance(res.errors[0], UnsupportedFormatValidationError)

    def test_oversized_file_fails(self):
        """Verify file exceeding max_upload_size_mb fails with FileTooLargeValidationError."""
        # Custom config setting max limit to 0 MB to trigger error
        config = {"upload": {"max_upload_size_mb": 0.00001, "accepted_extensions": [".png"]}}
        res = validate_raster(self.valid_png_path, config=config)
        self.assertFalse(res.is_valid)
        self.assertIsInstance(res.errors[0], FileTooLargeValidationError)

    def test_excessive_pixel_count_fails(self):
        """Verify image exceeding max dimension/pixel limit fails."""
        large_img_path = Path(self.tmp_dir.name) / "large.png"
        self.create_dummy_image(large_img_path, size=(500, 500))

        config = {
            "upload": {
                "max_dimension_px": 200,
                "max_total_pixels": 40000,
                "max_upload_size_mb": 200,
                "accepted_extensions": [".png"],
            }
        }
        res = validate_raster(large_img_path, config=config)
        self.assertFalse(res.is_valid)
        self.assertIsInstance(res.errors[0], PixelLimitExceededValidationError)

    def test_incompatible_before_after_images_fail(self):
        """Verify before/after pair with incompatible aspect ratio fails."""
        before_path = Path(self.tmp_dir.name) / "before.png"
        after_path = Path(self.tmp_dir.name) / "after.png"
        self.create_dummy_image(before_path, size=(100, 100))
        self.create_dummy_image(after_path, size=(400, 100))  # 4:1 aspect vs 1:1 aspect

        # Mock DisasterEvent
        from data.event_schema import DisasterEvent
        mock_event = DisasterEvent.from_dict({
            "event_id": "test-mock-event",
            "disaster_type": "flood",
            "location_name": "Test Location",
            "before_image": str(before_path),
            "after_image": str(after_path),
            "before_date": "2023-05-04",
            "after_date": "2023-05-19",
            "source": "Test Source",
            "CRS": "EPSG:32632",
            "resolution_m": 10.0,
            "available_bands": ["B03", "B08"],
        })

        res = validate_event_images(mock_event)
        self.assertFalse(res.is_valid)
        self.assertIsInstance(res.errors[0], IncompatibleBeforeAfterValidationError)

    def test_canonical_flood_event_passes_validation(self):
        """Verify canonical flood event (flood-emilia-romagna-2023) passes validation."""
        flood_event = load_event("flood-emilia-romagna-2023")
        res = validate_event_images(flood_event)
        self.assertTrue(res.is_valid, f"Flood event validation failed: {res.errors}")

    def test_canonical_wildfire_event_passes_validation(self):
        """Verify canonical wildfire event (wildfire-rhodes-2023) passes validation."""
        wildfire_event = load_event("wildfire-rhodes-2023")
        res = validate_event_images(wildfire_event)
        self.assertTrue(res.is_valid, f"Wildfire event validation failed: {res.errors}")


if __name__ == "__main__":
    unittest.main()
