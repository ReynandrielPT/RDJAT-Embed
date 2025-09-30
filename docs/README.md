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

Windows PowerShell:

```
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r rdjat\requirements.txt
```

## Run

- Direct script:

```
py -3.12 .\rdjat\rdjat.py
```

- As a module (if `__main__.py` is present):

```
py -3.12 -m rdjat
```

## Usage Notes

- Images are converted to grayscale (MATLAB-equivalent weights and round-half-up) before processing.
- Extraction requires the original cover (non-blind). The app reconstructs the cover using the Proposed method.
- The actual embedded length (counter) is used for extraction when available; otherwise limited by GT bits or capacity.
- For large bitstreams, the UI trims the visible bits to keep the interface responsive.

## Cite

If you use this tool in a paper (e.g., Software Impacts), please cite the repository. A `CITATION.cff` will be added at the repo root.
