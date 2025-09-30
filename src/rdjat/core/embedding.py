"""Embedding algorithms for RDJAT steganography."""

import math
from dataclasses import dataclass
from typing import Tuple

import numpy as np

from ..utils.image_processing import (
    matlab_histcounts_0_5_260,
    matlab_imhist_uint8,
    matlab_length,
    psnr_uint8,
    ssim_matlab,
)


@dataclass
class EmbedResult:
    """Result of embedding operation."""
    stego: np.ndarray
    psnr: float
    mse: float
    ssim: float
    bits_used: int


def compute_avg_by_bin(img: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute average values for each histogram bin."""
    p = img.reshape(-1, order="F").astype(np.float64)
    count = matlab_histcounts_0_5_260(p)
    sumEach = matlab_imhist_uint8(img.reshape(-1, order="F").astype(np.uint8))
    sum_group = np.zeros(52, dtype=np.float64)
    for k in range(256):
        idx = k // 5
        sum_group[idx] += sumEach[k] * k
    avg_by_bin = np.zeros(52, dtype=np.float64)
    nz = count > 0
    avg_by_bin[nz] = np.ceil(sum_group[nz] / count[nz])
    return p, avg_by_bin, count


def compute_avgArr_per_pixel(img: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Compute average array for each pixel based on its bin."""
    p, avg_by_bin, _ = compute_avg_by_bin(img)
    bin_idx = np.floor_divide(p.astype(np.int64), 5)
    avgArr = avg_by_bin[bin_idx]
    return p, avgArr


def embed_once(img: np.ndarray, bits: np.ndarray) -> EmbedResult:
    """Embed bits into image using RDJAT average-bin method."""
    p, avg_by_bin, _ = compute_avg_by_bin(img)
    b = bits
    b_len = matlab_length(b)
    b_lin = b.reshape(-1, order="F")

    pp = np.empty_like(p, dtype=np.float64)
    cnt = 0
    bin_idx = np.floor_divide(p.astype(np.int64), 5)
    avgArr = avg_by_bin[bin_idx]

    for t in range(p.size):
        if (p[t] > 4) and (p[t] <= 249) and (cnt < b_len):
            d = p[t] - avgArr[t]
            dp = d + b_lin[cnt]
            pp[t] = p[t] + dp
            cnt += 1
        else:
            pp[t] = p[t]

    stego = pp.reshape(img.shape, order="F")
    stego = np.clip(stego, 0, 255).astype(np.uint8)

    the_psnr = psnr_uint8(stego, img)
    mse_val = float(np.mean((stego.astype(np.float64) - img.astype(np.float64)) ** 2))
    the_ssim = ssim_matlab(stego, img)

    return EmbedResult(stego=stego, psnr=the_psnr, mse=mse_val, ssim=the_ssim, bits_used=cnt)