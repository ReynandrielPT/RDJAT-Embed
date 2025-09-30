"""RDJAT-Embed - A GUI application for image steganography using the RDJAT average-bin method.

This package provides tools for:
- Embedding secret bits into images using the RDJAT algorithm
- Extracting bits from stego images (non-blind extraction)
- GUI interface for interactive embedding and extraction
- Image quality metrics (PSNR, MSE, SSIM)
- Histogram analysis and visualization

Main components:
- core: Core embedding and extraction algorithms
- gui: Tkinter-based graphical user interface
- utils: Image processing and utility functions
"""

__version__ = "1.0.0"
__author__ = "RDJAT-Embed Project"

from .gui.interface import EmbeddingApp
from .core.embedding import embed_once, EmbedResult
from .core.extraction import extract_with_TRA
from .utils.image_processing import (
    load_matlab_image,
    load_bits_dlmread_like,
    psnr_uint8,
    ssim_matlab,
)

__all__ = [
    "EmbeddingApp",
    "embed_once",
    "EmbedResult", 
    "extract_with_TRA",
    "load_matlab_image",
    "load_bits_dlmread_like",
    "psnr_uint8",
    "ssim_matlab",
]


def main():
    """Main entry point for the RDJAT-Embed GUI application."""
    from .gui.interface import main as gui_main
    gui_main()