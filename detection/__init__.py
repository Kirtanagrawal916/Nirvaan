"""
NIRVAAN Detection Package
Provides spectral processing, change detection algorithms, evidence mask post-processing, and polygon geometry extraction.
"""

from detection.mask import (
    clean_binary_mask,
    extract_contours_from_mask,
    transform_pixel_to_geo,
    validate_polygon_ring,
    mask_to_polygons,
)

__all__ = [
    "clean_binary_mask",
    "extract_contours_from_mask",
    "transform_pixel_to_geo",
    "validate_polygon_ring",
    "mask_to_polygons",
]
