"""
Confidence & Uncertainty Estimation Engine for NIRVAAN

Calculates evidence strength metrics, signal-to-noise ratios, and uncertainty ranges from spectral evidence.
Strictly prohibits claiming operational confidence standards. Labels all outputs as ESTIMATE / PROTOTYPE.
"""

import math
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np


def calculate_evidence_confidence(
    spectral_index_diff: Union[np.ndarray, List[List[float]]],
    binary_mask: Optional[Union[np.ndarray, List[List[bool]]]] = None
) -> Dict[str, Any]:
    """
    Calculate evidence confidence score (0.0 to 1.0) and uncertainty bands.
    
    Returns structured confidence dictionary with explicit ESTIMATE / PROTOTYPE labels.
    """
    if spectral_index_diff is None:
        return {
            "confidence_score": 0.0,
            "uncertainty_band": [0.0, 0.1],
            "quality_tier": "UNASSESSED",
            "provenance_label": "ESTIMATE",
            "is_prototype": True,
            "disclaimer": "Unassessed confidence score — prototype estimation only."
        }

    diff_arr = np.asarray(spectral_index_diff, dtype=float)
    if diff_arr.size == 0 or np.isnan(diff_arr).all():
        return {
            "confidence_score": 0.0,
            "uncertainty_band": [0.0, 0.1],
            "quality_tier": "INVALID_DATA",
            "provenance_label": "ESTIMATE",
            "is_prototype": True,
            "disclaimer": "Invalid spectral data array — prototype estimation only."
        }

    if binary_mask is not None:
        mask_arr = np.asarray(binary_mask, dtype=bool)
    else:
        mask_arr = np.abs(diff_arr) > 0.1

    active_pixels = diff_arr[mask_arr]
    bg_pixels = diff_arr[~mask_arr]

    if active_pixels.size == 0:
        return {
            "confidence_score": 0.0,
            "uncertainty_band": [0.0, 0.1],
            "quality_tier": "NO_ANOMALY_DETECTED",
            "provenance_label": "ESTIMATE",
            "is_prototype": True,
            "disclaimer": "No positive spectral anomaly detected — prototype estimation only."
        }

    # Calculate signal to noise ratio
    mean_signal = float(np.nanmean(np.abs(active_pixels)))
    std_bg = float(np.nanstd(bg_pixels)) if bg_pixels.size > 0 else 0.05
    snr = mean_signal / max(std_bg, 0.01)

    # Sigmoid mapping of SNR to 0.0-1.0 confidence score
    confidence_score = 1.0 / (1.0 + math.exp(-0.5 * (snr - 3.0)))
    confidence_score = round(min(max(confidence_score, 0.05), 0.95), 2)

    # Margin of uncertainty (e.g. +/- 10% based on background variance)
    margin = round(min(max(0.05 + 0.1 * (std_bg / max(mean_signal, 0.1)), 0.03), 0.15), 2)
    lower_bound = round(max(confidence_score - margin, 0.0), 2)
    upper_bound = round(min(confidence_score + margin, 1.0), 2)

    # Categorize Quality Tier
    if confidence_score >= 0.75:
        quality_tier = "HIGH_CONFIDENCE"
    elif confidence_score >= 0.50:
        quality_tier = "MODERATE_CONFIDENCE"
    else:
        quality_tier = "LOW_CONFIDENCE"

    return {
        "confidence_score": confidence_score,
        "uncertainty_band": [lower_bound, upper_bound],
        "quality_tier": quality_tier,
        "signal_to_noise_ratio": round(snr, 2),
        "active_pixel_count": int(active_pixels.size),
        "provenance_label": "ESTIMATE",
        "is_prototype": True,
        "disclaimer": "Prototype confidence score — not an operational emergency standard. Field verification required."
    }
