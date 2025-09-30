# API Reference

## Core Functions

### Embedding

```python
from rdjat.core.embedding import embed_once, EmbedResult

def embed_once(img: np.ndarray, bits: np.ndarray) -> EmbedResult:
    """Embed bits into image using RDJAT average-bin method."""
```

### Extraction

```python
from rdjat.core.extraction import extract_with_TRA

def extract_with_TRA(cover_img: np.ndarray, stego_img: np.ndarray,
                     bits_len: int) -> Tuple[np.ndarray, np.ndarray]:
    """Extract bits from stego image using TRA method."""
```

### Utilities

```python
from rdjat.utils.image_processing import (
    load_matlab_image,
    load_bits_dlmread_like,
    psnr_uint8,
    ssim_matlab
)
```

## GUI Components

The main GUI application is available through:

```python
from rdjat.gui.interface import EmbeddingApp

app = EmbeddingApp()
app.mainloop()
```
