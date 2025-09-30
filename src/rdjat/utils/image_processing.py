"""Image processing utilities for RDJAT steganography."""

import math
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim


def rgb2gray_uint8_matlab(rgb_uint8: np.ndarray) -> np.ndarray:
    """Convert RGB image to grayscale using MATLAB-equivalent weights."""
    rgb = rgb_uint8.astype(np.float64)
    y = (
        0.298936021293776 * rgb[..., 0]
        + 0.587043074451121 * rgb[..., 1]
        + 0.114020904255103 * rgb[..., 2]
    )
    y = np.floor(y + 0.5)
    y = np.clip(y, 0, 255).astype(np.uint8)
    return y


def load_matlab_image(path: Path) -> np.ndarray:
    """Load image and convert to grayscale if necessary."""
    img = Image.open(path)
    arr = np.array(img)
    if arr.ndim == 3 and arr.shape[2] == 3:
        return rgb2gray_uint8_matlab(arr)
    if arr.dtype != np.uint8:
        arr = arr.astype(np.uint8)
    return arr


def matlab_histcounts_0_5_260(p: np.ndarray) -> np.ndarray:
    """Compute histogram with bins from 0 to 260 in steps of 5."""
    edges = np.arange(0, 261, 5, dtype=np.int64)
    count, _ = np.histogram(p, bins=edges)
    return count


def matlab_imhist_uint8(p_uint8: np.ndarray) -> np.ndarray:
    """Compute histogram for uint8 image."""
    return np.bincount(p_uint8, minlength=256)


def load_bits_dlmread_like(path: Path) -> np.ndarray:
    """Load bits from file, compatible with MATLAB dlmread."""
    try:
        arr = np.loadtxt(path, dtype=np.float64, ndmin=1)
        if arr.ndim == 0:
            arr = arr.reshape(1)
        return arr.reshape(-1, order="F")
    except Exception:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            text = ""
        bits = [1.0 if ch == "1" else 0.0 for ch in text if ch in ("0", "1")]
        return np.asarray(bits, dtype=np.float64)


def psnr_uint8(a: np.ndarray, b: np.ndarray) -> float:
    """Calculate Peak Signal-to-Noise Ratio between two uint8 images."""
    diff = a.astype(np.float64) - b.astype(np.float64)
    mse = np.mean(diff * diff)
    if mse == 0:
        return float("inf")
    return 10.0 * math.log10((255.0 * 255.0) / mse)


def ssim_matlab(a: np.ndarray, b: np.ndarray) -> float:
    """Calculate Structural Similarity Index using MATLAB-equivalent parameters."""
    channel_axis = -1 if a.ndim == 3 else None
    return float(
        ssim(
            a,
            b,
            data_range=255,
            gaussian_weights=True,
            sigma=1.5,
            win_size=11,
            channel_axis=channel_axis,
            use_sample_covariance=False,
        )
    )


def matlab_length(arr: np.ndarray) -> int:
    """Get MATLAB-equivalent length of array."""
    if arr.ndim == 0:
        return 1
    return int(max(arr.shape))