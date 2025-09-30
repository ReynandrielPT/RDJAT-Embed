# RDJAT-Embed Quick Start Guide

## Installation & Setup

### Option 1: Direct Usage (Recommended for Research)

```bash
# Navigate to project directory
cd rdjat

# Install required dependencies
pip install numpy Pillow scikit-image

# Run the GUI application
python -m src.rdjat
```

### Option 2: Package Installation

```bash
# Install as a package (development mode)
pip install -e .

# Run the application
rdjat-embed
```

## How to Use RDJAT-Embed

### 1. Embedding Process

1. **Select Cover Image**: Click "Browse" next to "Cover image" and choose a TIFF/PNG/JPG file
2. **Select Bits File**: Click "Browse" next to "Bits file" and choose a text file with 0s and 1s
3. **Run Embedding**: Click "Run Embedding" to embed the secret bits
4. **View Results**: Check the metrics (PSNR, MSE, SSIM) and compare Original vs Stego images
5. **Save Results**: Use "Save Stego..." to save the stego image

### 2. Extraction Process

1. **Auto-filled Fields**: After embedding, extraction fields are automatically filled
2. **Or Manual Selection**:
   - Original cover image (the same image used for embedding)
   - Stego image (the result from embedding)
   - Ground-truth bits file (for comparison)
3. **Extract & Compare**: Click "Extract & Compare" to recover the hidden bits
4. **View Results**: Check the BER (Bit Error Rate) and compare embedded vs recovered bits
5. **View Recovered Cover**: See the reconstructed cover image

### 3. Visual Analysis

- **Three Panels**: Original, Stego, and Recovered Cover images
- **Histograms**: Real-time histogram display for all three images
- **Bits Comparison**: Side-by-side view of embedded vs recovered bits

## Sample Files

Use the provided sample files for testing:

- **Images**: `assets/images/` (Aerial.tiff, Baboon.tiff, etc.)
- **Test Bits**: `assets/test_data/` (random-binary_1Kb.txt, etc.)

## For Research Papers

The tool provides all metrics needed for steganography research:

- **PSNR** (Peak Signal-to-Noise Ratio)
- **MSE** (Mean Squared Error)
- **SSIM** (Structural Similarity Index)
- **BER** (Bit Error Rate)
- **Capacity** (Number of bits embedded)

Export metrics using "Save Metrics..." for inclusion in your research results.
