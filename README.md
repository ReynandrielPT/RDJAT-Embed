# RDJAT-Embed (Embedding & Extraction)

A Tkinter GUI for single-run image embedding and non-blind extraction using the RDJAT average-bin method, aligned with the reference MATLAB workflow (TRA + modulo, reconstructed cover).

## Overview

RDJAT-Embed provides a complete Tkinter-based GUI for embedding and extracting secret data from images. It implements the RDJAT average-bin steganography method with MATLAB-compatible algorithms and includes comprehensive quality metrics.

## Features

- **Embedding**: Hide secret bits in images using per-5-bin averages (bins 0:5:260) with PSNR/MSE/SSIM
- **Extraction**: Non-blind extraction using TRA-style modulo method; shows the reconstructed cover
- **Auto-fills**: Extraction inputs from the last embed run
- **Three previews**: Original, Stego, and Recovered Cover
- **Bits comparison**: Embedded vs. recovered (capped preview)
- **Histograms**: For Original, Stego, and Recovered Cover
- **Quality Metrics**: PSNR, MSE, and SSIM calculations

- **Visualization**: Side-by-side image previews and histogram analysis## Installation

- **Bits Comparison**: View embedded vs. recovered bits

- **MATLAB Compatibility**: Algorithms aligned with reference MATLAB implementationWindows PowerShell:

## Installation```

py -3.12 -m venv .venv

### Prerequisites.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip

- Python 3.8 or higherpip install -r rdjat\requirements.txt

- pip package manager```

### Install from Source## Run

````bash- Direct script:

# Clone or download the project

cd rdjat```

py -3.12 .\rdjat\rdjat.py

# Create virtual environment (recommended)```

python -m venv .venv

- As a module (if `__main__.py` is present):

# Activate virtual environment

# Windows:```

.venv\Scripts\activatepy -3.12 -m rdjat

# Linux/Mac:```

source .venv/bin/activate

## Usage Notes

# Install the package

pip install -e .- Images are converted to grayscale (MATLAB-equivalent weights and round-half-up) before processing.

```- Extraction requires the original cover (non-blind). The app reconstructs the cover using the Proposed method.

- The actual embedded length (counter) is used for extraction when available; otherwise limited by GT bits or capacity.

### Install Dependencies Only- For large bitstreams, the UI trims the visible bits to keep the interface responsive.



```bash## Cite

pip install -r requirements.txt

```If you use this tool in a paper (e.g., Software Impacts), please cite the repository. A `CITATION.cff` will be added at the repo root.


## Usage

### Command Line

After installation, you can run RDJAT from anywhere:

```bash
rdjat
````

### As a Python Module

```bash
# From the project directory
python -m rdjat

# Or using the src path
python -m src.rdjat
```

### Programmatic Usage

```python
from rdjat import EmbeddingApp, embed_once, extract_with_TRA
from rdjat.utils import load_matlab_image, load_bits_dlmread_like

# Launch GUI
app = EmbeddingApp()
app.mainloop()

# Or use core functions directly
cover_img = load_matlab_image("cover.tiff")
secret_bits = load_bits_dlmread_like("secret.txt")
result = embed_once(cover_img, secret_bits)
```

## Project Structure

```
rdjat/
├── src/rdjat/              # Main package source
│   ├── __init__.py         # Package initialization
│   ├── __main__.py         # Module entry point
│   ├── core/               # Core algorithms
│   │   ├── embedding.py    # Embedding functions
│   │   └── extraction.py   # Extraction functions
│   ├── gui/                # User interface
│   │   └── interface.py    # Main GUI application
│   └── utils/              # Utility functions
│       └── image_processing.py
├── assets/                 # Test data and resources
│   ├── images/             # Sample images
│   └── test_data/          # Test bit files
├── examples/               # Example scripts and MATLAB code
├── tests/                  # Unit tests
├── docs/                   # Documentation
├── requirements.txt        # Dependencies
├── setup.py               # Package setup
└── pyproject.toml         # Modern Python packaging config
```

## Development

### Setting up Development Environment

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Format code
black src/

# Type checking
mypy src/
```

### Key Components

- **Core Module**: Contains the main steganography algorithms

  - `embedding.py`: RDJAT embedding algorithm implementation
  - `extraction.py`: TRA-based extraction methods

- **GUI Module**: Tkinter-based user interface

  - `interface.py`: Complete GUI application with file dialogs, previews, and metrics

- **Utils Module**: Image processing and utility functions
  - `image_processing.py`: MATLAB-compatible image operations, PSNR/SSIM calculations

## Algorithm Details

The RDJAT method uses:

- **Histogram binning**: Groups pixels into bins of 5 intensity levels (0-4, 5-9, ..., 250-254)
- **Average calculation**: Computes average intensity per bin using MATLAB-equivalent rounding
- **Adaptive embedding**: Only embeds in pixels with intensity 5-249 (excludes extremes)
- **TRA extraction**: Uses Textural Region Adaptive masks for deterministic bit recovery

## File Formats

- **Images**: TIFF, PNG, JPEG (converted to grayscale)
- **Bits**: Plain text files with '0' and '1' characters
- **Metrics**: CSV export for PSNR, MSE, SSIM values

## Citation

If you use RDJAT in academic work, please cite the repository and reference the original research paper.

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure code passes linting and tests
5. Submit a pull request

## Support

For issues, questions, or contributions, please use the project's issue tracker.
