# RDJAT-Embed (Embedding & Extraction)

A Tkinter GUI for single-run image embedding and non-blind extraction using the RDJAT average-bin method, aligned with the reference MATLAB workflow (TRA + modulo, reconstructed cover).

## Features

- Embedding with per-5-bin averages (bins 0:5:260), with PSNR/MSE/SSIM
- Extraction via TRA-style modulo method; shows the reconstructed cover
- Auto-fills extraction inputs from the last embed run
- Three previews: Original, Stego, and Recovered Cover
- Bits panes: embedded vs. recovered (capped preview)
- Histograms for Original, Stego, and Recovered Cover

## Installation

**Windows PowerShell:**

```
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Linux/Mac:**

```
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run

**Direct script:**

```
python -m src.rdjat
```

**As a module (after installation):**

```
pip install -e .
rdjat-embed
```

## Usage Notes

- Images are converted to grayscale (MATLAB-equivalent weights and round-half-up) before processing.
- Extraction requires the original cover (non-blind). The app reconstructs the cover using the Proposed method.
- The actual embedded length (counter) is used for extraction when available; otherwise limited by GT bits or capacity.
- For large bitstreams, the UI trims the visible bits to keep the interface responsive.

## Project Structure

```
rdjat/
├── src/rdjat/              # Main package source
│   ├── __init__.py         # Package initialization
│   ├── __main__.py         # Module entry point
│   ├── core/               # Core algorithms
│   │   ├── embedding.py    # RDJAT embedding functions
│   │   └── extraction.py   # TRA extraction methods
│   ├── gui/                # User interface
│   │   └── interface.py    # Complete Tkinter GUI
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

## Development

### Setting up Development Environment

```
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Format code
black src/

# Type checking
mypy src/
```

## Citation

If you use this tool in a paper (e.g., Software Impacts), please cite the repository. A `CITATION.cff` will be added at the repo root.

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure code passes linting and tests
5. Submit a pull request
