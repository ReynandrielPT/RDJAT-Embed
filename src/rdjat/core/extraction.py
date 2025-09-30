"""Extraction algorithms for RDJAT steganography."""

import math
from typing import Optional, Tuple

import numpy as np

from .embedding import compute_avgArr_per_pixel
from ..utils.image_processing import matlab_length


def build_TRA_mask(p_flat: np.ndarray, bits_len: int) -> np.ndarray:
    """Build TRA (Textural Region Adaptive) mask for extraction.
    
    Args:
        p_flat: Flattened cover image pixels
        bits_len: Number of bits to extract
    
    Returns:
        TRA mask array indicating which pixels were used for embedding
    """
    tra = np.zeros_like(p_flat, dtype=np.uint8)
    cnt = 0
    for i in range(p_flat.size):
        if (p_flat[i] > 4) and (p_flat[i] <= 249) and (cnt < bits_len):
            tra[i] = 1
            cnt += 1
    return tra


def extract_with_TRA(cover_img: np.ndarray, stego_img: np.ndarray, bits_len: int,
                     avgArr_flat: Optional[np.ndarray] = None,
                     tra_flat: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
    """Extract bits from stego image using TRA method.
    
    Args:
        cover_img: Original cover image
        stego_img: Stego image containing embedded bits
        bits_len: Number of bits to extract
        avgArr_flat: Pre-computed average array (optional)
        tra_flat: Pre-computed TRA mask (optional)
    
    Returns:
        Tuple of (extracted_bits, reconstructed_cover_image)
    """
    h, w = cover_img.shape[:2]
    s = stego_img.reshape(-1, order="F").astype(np.float64)
    
    # Compute average array if not provided
    if avgArr_flat is None:
        p_flat, avg_flat = compute_avgArr_per_pixel(cover_img)
    else:
        p_flat = cover_img.reshape(-1, order="F").astype(np.float64)
        avg_flat = avgArr_flat
    
    # Check capacity
    eligible = ((p_flat > 4) & (p_flat <= 249))
    capacity = int(np.count_nonzero(eligible))
    used_len = min(bits_len, capacity)
    
    # Build TRA mask if not provided
    tra = tra_flat if tra_flat is not None else build_TRA_mask(p_flat, used_len)
    
    # Extract bits and reconstruct cover
    secret = np.zeros(used_len, dtype=np.float64)
    cover_rec = np.zeros_like(s, dtype=np.float64)
    
    h_idx = 0
    for i in range(s.size):
        if tra[i] == 1 and h_idx < used_len:
            # Extract bit using modulo method
            bit = (s[i] - avg_flat[i]) % 2
            bit = 1.0 if int(bit) % 2 == 1 else 0.0
            secret[h_idx] = bit
            
            # Reconstruct cover pixel
            cover_rec[i] = math.floor((s[i] + avg_flat[i] - bit) / 2.0)
            h_idx += 1
        else:
            cover_rec[i] = s[i]
    
    # Reshape reconstructed cover to original image shape
    cover_rec_img = cover_rec.reshape((h, w), order="F")
    cover_rec_img = np.clip(cover_rec_img, 0, 255).astype(np.uint8)
    
    return secret, cover_rec_img


def build_TRA_mask(p_flat: np.ndarray, bits_len: int) -> np.ndarray:
    """Build TRA (Textural Region Adaptive) mask for extraction."""
    tra = np.zeros_like(p_flat, dtype=np.uint8)
    cnt = 0
    for i in range(p_flat.size):
        if (p_flat[i] > 4) and (p_flat[i] <= 249) and (cnt < bits_len):
            tra[i] = 1
            cnt += 1
    return tra


def extract_with_TRA(cover_img: np.ndarray, stego_img: np.ndarray, bits_len: int,
                     avgArr_flat: Optional[np.ndarray] = None,
                     tra_flat: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
    """Extract bits from stego image using TRA method."""
    h, w = cover_img.shape[:2]
    s = stego_img.reshape(-1, order="F").astype(np.float64)
    p_flat, avg_flat = compute_avgArr_per_pixel(cover_img) if avgArr_flat is None else (None, avgArr_flat)
    if avgArr_flat is None:
        pass
    else:
        p_flat = cover_img.reshape(-1, order="F").astype(np.float64)
    
    eligible = ((p_flat > 4) & (p_flat <= 249))
    capacity = int(np.count_nonzero(eligible))
    used_len = min(bits_len, capacity)
    tra = tra_flat if tra_flat is not None else build_TRA_mask(p_flat, used_len)
    
    secret = np.zeros(used_len, dtype=np.float64)
    cover_rec = np.zeros_like(s, dtype=np.float64)
    h_idx = 0
    
    for i in range(s.size):
        if tra[i] == 1 and h_idx < used_len:
            bit = (s[i] - avg_flat[i]) % 2
            bit = 1.0 if int(bit) % 2 == 1 else 0.0
            secret[h_idx] = bit
            cover_rec[i] = math.floor((s[i] + avg_flat[i] - bit) / 2.0)
            h_idx += 1
        else:
            cover_rec[i] = s[i]
    
    cover_rec_img = cover_rec.reshape((h, w), order="F")
    cover_rec_img = np.clip(cover_rec_img, 0, 255).astype(np.uint8)
    return secret, cover_rec_img