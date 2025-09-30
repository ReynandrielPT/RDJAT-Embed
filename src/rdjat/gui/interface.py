"""RDJAT-Embed GUI interface for steganography embedding and extraction."""

import csv
import math
import threading
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk

from ..core.embedding import embed_once, compute_avgArr_per_pixel
from ..core.extraction import extract_with_TRA, build_TRA_mask
from ..utils.image_processing import (
    load_matlab_image,
    load_bits_dlmread_like,
    matlab_length,
)


class EmbeddingApp(tk.Tk):
    """Main GUI application for RDJAT-Embed steganography."""
    
    def __init__(self) -> None:
        super().__init__()
        self.title("RDJAT-Embed - Embedding & Extraction GUI")
        self.geometry("1100x750")

        # Image and data paths
        self.img_path: Optional[Path] = None
        self.bits_path: Optional[Path] = None
        
        # Image arrays
        self.orig_img_arr: Optional[np.ndarray] = None
        self.stego_img_arr: Optional[np.ndarray] = None
        self.recovered_cover_arr: Optional[np.ndarray] = None
        
        # Cached data for extraction
        self.last_bits_arr: Optional[np.ndarray] = None
        self.last_bits_path: Optional[Path] = None
        self.last_bits_used: Optional[int] = None
        
        # Extraction paths and arrays
        self.extract_cover_path: Optional[Path] = None
        self.extract_stego_path: Optional[Path] = None
        self.extract_gt_bits_path: Optional[Path] = None
        self.extract_cover_arr: Optional[np.ndarray] = None
        self.extract_stego_arr: Optional[np.ndarray] = None
        self.extracted_bits: Optional[np.ndarray] = None

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the complete user interface."""
        # Top section - file selection and embedding
        top = tk.Frame(self)
        top.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(top, text="Cover image (.tiff/.png/.jpg)").grid(row=0, column=0, sticky="w")
        self.img_entry = tk.Entry(top, width=80)
        self.img_entry.grid(row=0, column=1, padx=6)
        tk.Button(top, text="Browse", command=self._choose_image).grid(row=0, column=2)

        tk.Label(top, text="Bits file (txt)").grid(row=1, column=0, sticky="w")
        self.bits_entry = tk.Entry(top, width=80)
        self.bits_entry.grid(row=1, column=1, padx=6)
        tk.Button(top, text="Browse", command=self._choose_bits).grid(row=1, column=2)

        self.run_btn = tk.Button(top, text="Run Embedding", command=self._run_embedding)
        self.run_btn.grid(row=2, column=0, pady=8, sticky="w")

        self.save_btn = tk.Button(top, text="Save Stego…", command=self._save_stego, state=tk.DISABLED)
        self.save_btn.grid(row=2, column=1, pady=8, sticky="w")
        self.save_metrics_btn = tk.Button(top, text="Save Metrics…", command=self._save_metrics, state=tk.DISABLED)
        self.save_metrics_btn.grid(row=2, column=2, pady=8, sticky="w")

        # Metrics section
        metrics = tk.LabelFrame(self, text="Metrics")
        metrics.pack(fill=tk.X, padx=10, pady=5)
        self.psnr_var = tk.StringVar(value="PSNR: -")
        self.mse_var = tk.StringVar(value="MSE: -")
        self.ssim_var = tk.StringVar(value="SSIM: -")
        self.bits_var = tk.StringVar(value="Bits used: -")
        tk.Label(metrics, textvariable=self.psnr_var).grid(row=0, column=0, padx=10, pady=4, sticky="w")
        tk.Label(metrics, textvariable=self.mse_var).grid(row=0, column=1, padx=10, pady=4, sticky="w")
        tk.Label(metrics, textvariable=self.ssim_var).grid(row=0, column=2, padx=10, pady=4, sticky="w")
        tk.Label(metrics, textvariable=self.bits_var).grid(row=0, column=3, padx=10, pady=4, sticky="w")

        # Image preview section
        previews = tk.Frame(self)
        previews.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.left_panel = tk.LabelFrame(previews, text="Original")
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.left_canvas = tk.Canvas(self.left_panel, bg="#222222")
        self.left_canvas.pack(fill=tk.BOTH, expand=True)
        
        self.right_panel = tk.LabelFrame(previews, text="Stego")
        self.right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 5))
        self.right_canvas = tk.Canvas(self.right_panel, bg="#222222")
        self.right_canvas.pack(fill=tk.BOTH, expand=True)
        
        self.extract_panel = tk.LabelFrame(previews, text="Recovered Cover")
        self.extract_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 0))
        self.extract_canvas = tk.Canvas(self.extract_panel, bg="#222222")
        self.extract_canvas.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_var = tk.StringVar(value="Select an image and a bits file, then click Run.")
        status = tk.Label(self, textvariable=self.status_var, anchor="w")
        status.pack(fill=tk.X, padx=10, pady=4)

        # Bind canvas events
        self.left_canvas.bind("<Configure>", lambda e: self._refresh_canvases())
        self.right_canvas.bind("<Configure>", lambda e: self._refresh_canvases())

        # Extraction section
        self._build_extraction_ui()
        
        # Bits comparison section
        self._build_bits_ui()
        
        # Histograms section
        self._build_histograms_ui()

    def _build_extraction_ui(self) -> None:
        """Build the extraction section of the UI."""
        extract = tk.LabelFrame(self, text="Extraction (non-blind: requires original cover)")
        extract.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(extract, text="Original cover image").grid(row=0, column=0, sticky="w")
        self.extract_cover_entry = tk.Entry(extract, width=80)
        self.extract_cover_entry.grid(row=0, column=1, padx=6)
        tk.Button(extract, text="Browse", command=self._choose_extract_cover).grid(row=0, column=2)
        
        tk.Label(extract, text="Stego image").grid(row=1, column=0, sticky="w")
        self.extract_stego_entry = tk.Entry(extract, width=80)
        self.extract_stego_entry.grid(row=1, column=1, padx=6)
        tk.Button(extract, text="Browse", command=self._choose_extract_stego).grid(row=1, column=2)
        
        tk.Label(extract, text="Ground-truth bits file (txt)").grid(row=2, column=0, sticky="w")
        self.extract_gt_bits_entry = tk.Entry(extract, width=80)
        self.extract_gt_bits_entry.grid(row=2, column=1, padx=6)
        tk.Button(extract, text="Browse", command=self._choose_extract_gt_bits).grid(row=2, column=2)
        
        self.extract_btn = tk.Button(extract, text="Extract && Compare", command=self._run_extract_compare)
        self.extract_btn.grid(row=3, column=0, pady=8, sticky="w")
        
        self.save_extracted_btn = tk.Button(extract, text="Save Extracted…", command=self._save_extracted_bits, state=tk.DISABLED)
        self.save_extracted_btn.grid(row=3, column=1, pady=8, sticky="w")
        
        self.extract_summary_var = tk.StringVar(value="Extracted: -, GT: -, Mismatches: -, BER: -")
        tk.Label(extract, textvariable=self.extract_summary_var).grid(row=3, column=2, padx=10, sticky="w")

    def _build_bits_ui(self) -> None:
        """Build the bits comparison section of the UI."""
        bits_frame = tk.LabelFrame(self, text="Bits (embedded vs recovered)")
        bits_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=5)
        
        left_bits = tk.Frame(bits_frame)
        left_bits.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        right_bits = tk.Frame(bits_frame)
        right_bits.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(left_bits, text="Embedded bits").pack(anchor="w")
        self.embedded_bits_text = scrolledtext.ScrolledText(left_bits, height=5, wrap=tk.NONE)
        self.embedded_bits_text.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(right_bits, text="Recovered bits").pack(anchor="w")
        self.recovered_bits_text = scrolledtext.ScrolledText(right_bits, height=5, wrap=tk.NONE)
        self.recovered_bits_text.pack(fill=tk.BOTH, expand=True)

    def _build_histograms_ui(self) -> None:
        """Build the histograms section of the UI."""
        hists = tk.LabelFrame(self, text="Histograms")
        hists.pack(fill=tk.BOTH, expand=False, padx=10, pady=5)
        
        self.hist_left_canvas = tk.Canvas(hists, height=120, bg="#222222")
        self.hist_left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.hist_right_canvas = tk.Canvas(hists, height=120, bg="#222222")
        self.hist_right_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.hist_extract_canvas = tk.Canvas(hists, height=120, bg="#222222")
        self.hist_extract_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Bind histogram canvas events
        self.hist_left_canvas.bind("<Configure>", lambda e: self._update_histograms())
        self.hist_right_canvas.bind("<Configure>", lambda e: self._update_histograms())
        self.hist_extract_canvas.bind("<Configure>", lambda e: self._update_histograms())

    # File selection methods
    def _choose_image(self) -> None:
        """Choose cover image file."""
        filetypes = [
            ("Image files", "*.tif *.tiff *.png *.jpg *.jpeg"),
            ("All files", "*.*"),
        ]
        path = filedialog.askopenfilename(title="Choose cover image", filetypes=filetypes)
        if path:
            self.img_path = Path(path)
            self.img_entry.delete(0, tk.END)
            self.img_entry.insert(0, str(self.img_path))
            try:
                self.orig_img_arr = load_matlab_image(self.img_path)
                self._set_canvas_image(self.left_canvas, self.orig_img_arr)
                self.status_var.set(f"Loaded image: {self.img_path.name} ({self.orig_img_arr.shape})")
                self._update_histograms()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")

    def _choose_bits(self) -> None:
        """Choose bits file."""
        path = filedialog.askopenfilename(title="Choose bits file", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            self.bits_path = Path(path)
            self.bits_entry.delete(0, tk.END)
            self.bits_entry.insert(0, str(self.bits_path))

    def _choose_extract_cover(self) -> None:
        """Choose original cover image for extraction."""
        filetypes = [
            ("Image files", "*.tif *.tiff *.png *.jpg *.jpeg"),
            ("All files", "*.*"),
        ]
        path = filedialog.askopenfilename(title="Choose ORIGINAL cover image", filetypes=filetypes)
        if path:
            self.extract_cover_path = Path(path)
            self.extract_cover_entry.delete(0, tk.END)
            self.extract_cover_entry.insert(0, str(self.extract_cover_path))
            try:
                self.extract_cover_arr = load_matlab_image(self.extract_cover_path)
                self._set_canvas_image(self.left_canvas, self.extract_cover_arr)
                self.status_var.set(f"Loaded original cover for extraction: {self.extract_cover_path.name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load original cover: {e}")

    def _choose_extract_stego(self) -> None:
        """Choose stego image for extraction."""
        filetypes = [
            ("Image files", "*.tif *.tiff *.png *.jpg *.jpeg"),
            ("All files", "*.*"),
        ]
        path = filedialog.askopenfilename(title="Choose STEGO image", filetypes=filetypes)
        if path:
            self.extract_stego_path = Path(path)
            self.extract_stego_entry.delete(0, tk.END)
            self.extract_stego_entry.insert(0, str(self.extract_stego_path))
            try:
                self.extract_stego_arr = load_matlab_image(self.extract_stego_path)
                self._set_canvas_image(self.right_canvas, self.extract_stego_arr)
                self.status_var.set(f"Loaded stego image: {self.extract_stego_path.name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load stego image: {e}")

    def _choose_extract_gt_bits(self) -> None:
        """Choose ground-truth bits file for extraction."""
        path = filedialog.askopenfilename(title="Choose ground-truth bits file", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            self.extract_gt_bits_path = Path(path)
            self.extract_gt_bits_entry.delete(0, tk.END)
            self.extract_gt_bits_entry.insert(0, str(self.extract_gt_bits_path))

    # Main operations
    def _run_embedding(self) -> None:
        """Run the embedding operation in a separate thread."""
        if not self.img_path:
            messagebox.showwarning("Missing image", "Please choose a cover image first.")
            return
        if not self.bits_path:
            messagebox.showwarning("Missing bits", "Please choose a bits file first.")
            return

        def worker():
            try:
                self._set_running(True)
                # Clear recovered cover preview
                self.recovered_cover_arr = None
                try:
                    self.extract_canvas.delete("all")
                except Exception:
                    pass
                
                img = self.orig_img_arr if self.orig_img_arr is not None else load_matlab_image(self.img_path)
                bits = load_bits_dlmread_like(self.bits_path)
                res = embed_once(img, bits)
                
                self.stego_img_arr = res.stego
                self._set_canvas_image(self.right_canvas, self.stego_img_arr)
                
                # Update metrics
                self.psnr_var.set(f"PSNR: {res.psnr:.6f}")
                self.mse_var.set(f"MSE: {res.mse:.6f}")
                self.ssim_var.set(f"SSIM: {res.ssim:.6f}")
                self.bits_var.set(f"Bits used: {res.bits_used}")
                
                # Enable save buttons
                self.save_btn.config(state=tk.NORMAL)
                self.save_metrics_btn.config(state=tk.NORMAL)
                self.status_var.set("Embedding complete.")
                
                # Cache for extraction auto-fill
                self.last_bits_arr = bits.copy()
                self.last_bits_path = self.bits_path
                self.extract_cover_arr = img.copy()
                self.extract_stego_arr = self.stego_img_arr.copy()
                self.last_bits_used = int(res.bits_used)
                
                # Auto-fill extraction entries
                if self.img_path:
                    self.extract_cover_path = self.img_path
                    self.extract_cover_entry.delete(0, tk.END)
                    self.extract_cover_entry.insert(0, str(self.extract_cover_path))
                if self.bits_path:
                    self.extract_gt_bits_path = self.bits_path
                    self.extract_gt_bits_entry.delete(0, tk.END)
                    self.extract_gt_bits_entry.insert(0, str(self.extract_gt_bits_path))
                
                self._update_histograms()
                self._show_embedded_bits(bits, res.bits_used)
                
            except Exception as e:
                messagebox.showerror("Error", f"Embedding failed: {e}")
                self.status_var.set("Embedding failed. See error.")
            finally:
                self._set_running(False)

        threading.Thread(target=worker, daemon=True).start()

    def _run_extract_compare(self) -> None:
        """Run extraction and comparison in a separate thread."""
        # Auto-use last embedded inputs if user hasn't selected files
        if self.extract_cover_arr is None and self.orig_img_arr is not None:
            self.extract_cover_arr = self.orig_img_arr.copy()
        if self.extract_stego_arr is None and self.stego_img_arr is not None:
            self.extract_stego_arr = self.stego_img_arr.copy()
        if self.extract_gt_bits_path is None and self.last_bits_path is not None:
            self.extract_gt_bits_path = self.last_bits_path

        if self.extract_cover_path is None and self.extract_cover_arr is None:
            messagebox.showwarning("Missing original cover", "Please choose the ORIGINAL cover image used for embedding.")
            return
        if self.extract_stego_path is None and self.extract_stego_arr is None:
            messagebox.showwarning("Missing stego image", "Please choose the STEGO image.")
            return
        if self.extract_gt_bits_path is None and self.last_bits_arr is None:
            messagebox.showwarning("Missing ground-truth bits", "Please choose the ground-truth bits file to compare.")
            return

        def worker():
            try:
                self._set_running(True)
                cover = self.extract_cover_arr if self.extract_cover_arr is not None else load_matlab_image(self.extract_cover_path)
                stego = self.extract_stego_arr if self.extract_stego_arr is not None else load_matlab_image(self.extract_stego_path)
                if self.extract_gt_bits_path is not None:
                    gt_bits = load_bits_dlmread_like(self.extract_gt_bits_path)
                else:
                    gt_bits = self.last_bits_arr if self.last_bits_arr is not None else np.array([], dtype=np.float64)

                # Determine extraction length
                req_len = int(matlab_length(gt_bits))
                p_flat, avg_flat_cover = compute_avgArr_per_pixel(cover)
                eligible = ((p_flat > 4) & (p_flat <= 249))
                capacity = int(np.count_nonzero(eligible))
                
                if self.last_bits_used is not None:
                    used_len = min(self.last_bits_used, capacity)
                else:
                    used_len = min(req_len, capacity)

                # Rebuild TRA deterministically
                tra_src = build_TRA_mask(p_flat, used_len)

                extracted, recovered_cover = extract_with_TRA(cover, stego, used_len, avgArr_flat=avg_flat_cover, tra_flat=tra_src)
                self.extracted_bits = extracted.copy()

                # Compare with ground truth
                n = min(len(extracted), len(gt_bits))
                if n == 0:
                    mismatches = 0
                    ber = 0.0
                else:
                    mismatches = int(np.sum(np.abs(np.round(extracted[:n]) - np.round(gt_bits[:n]))))
                    ber = mismatches / n
                
                self.extract_summary_var.set(
                    f"Extracted: {len(extracted)} | GT: {len(gt_bits)} | Mismatches: {mismatches} | BER: {ber:.6f}"
                )
                
                # Show reconstructed cover
                self.recovered_cover_arr = recovered_cover
                self._set_canvas_image(self.extract_canvas, self.recovered_cover_arr)
                self._update_histograms()
                self._show_recovered_bits(extracted)
                
                self.status_var.set("Extraction complete.")
                self.save_extracted_btn.config(state=tk.NORMAL)
                
            except Exception as e:
                messagebox.showerror("Error", f"Extraction failed: {e}")
                self.status_var.set("Extraction failed. See error.")
            finally:
                self._set_running(False)

        threading.Thread(target=worker, daemon=True).start()

    # UI state management
    def _set_running(self, running: bool) -> None:
        """Set UI state based on whether operations are running."""
        self.run_btn.config(state=tk.DISABLED if running else tk.NORMAL)
        can_save = (not running) and (self.stego_img_arr is not None)
        self.save_btn.config(state=(tk.NORMAL if can_save else tk.DISABLED))
        self.save_metrics_btn.config(state=(tk.NORMAL if can_save else tk.DISABLED))
        can_save_bits = (not running) and (self.extracted_bits is not None)
        self.save_extracted_btn.config(state=(tk.NORMAL if can_save_bits else tk.DISABLED))

    # Display methods
    def _set_canvas_image(self, canvas: tk.Canvas, arr: np.ndarray) -> None:
        """Display image array on canvas."""
        if arr.ndim == 2:
            pil = Image.fromarray(arr)
        elif arr.ndim == 3 and arr.shape[2] in (3, 4):
            pil = Image.fromarray(arr[:, :, :3])
        else:
            pil = Image.fromarray(arr[..., 0] if arr.ndim == 3 else arr)

        # Fit to canvas while keeping aspect ratio
        c_w = max(1, int(canvas.winfo_width()))
        c_h = max(1, int(canvas.winfo_height()))
        if c_w < 2 or c_h < 2:
            c_w, c_h = 512, 512
        pil_disp = self._fit_image(pil, (c_w, c_h))
        tk_img = ImageTk.PhotoImage(pil_disp)
        canvas.delete("all")
        canvas.image = tk_img  # keep reference
        canvas.create_image(c_w // 2, c_h // 2, image=tk_img)

    def _fit_image(self, img: Image.Image, target: Tuple[int, int]) -> Image.Image:
        """Fit image to target size while maintaining aspect ratio."""
        t_w, t_h = target
        img = img.copy()
        img.thumbnail((t_w, t_h), Image.LANCZOS)
        # Optional: letterbox
        bg = Image.new("RGB", (t_w, t_h), (34, 34, 34))
        x = (t_w - img.width) // 2
        y = (t_h - img.height) // 2
        bg.paste(img, (x, y))
        return bg

    def _refresh_canvases(self) -> None:
        """Refresh all image canvases."""
        # Prefer extraction selections for display if available
        if self.extract_cover_arr is not None:
            self._set_canvas_image(self.left_canvas, self.extract_cover_arr)
        elif self.orig_img_arr is not None:
            self._set_canvas_image(self.left_canvas, self.orig_img_arr)

        if self.extract_stego_arr is not None:
            self._set_canvas_image(self.right_canvas, self.extract_stego_arr)
        elif self.stego_img_arr is not None:
            self._set_canvas_image(self.right_canvas, self.stego_img_arr)

        if self.recovered_cover_arr is not None:
            self._set_canvas_image(self.extract_canvas, self.recovered_cover_arr)
        
        self._update_histograms()

    def _show_embedded_bits(self, bits: np.ndarray, bits_used: int) -> None:
        """Display embedded bits in the text widget."""
        try:
            used_bits = bits.reshape(-1, order="F")[:bits_used]
            bit_chars = ["1" if round(v) == 1 else "0" for v in used_bits]
            s = "".join(bit_chars)
            max_chars = 5000
            s_view = s[:max_chars] + ("..." if len(s) > max_chars else "")
            self.embedded_bits_text.config(state=tk.NORMAL)
            self.embedded_bits_text.delete("1.0", tk.END)
            self.embedded_bits_text.insert(tk.END, s_view)
            self.embedded_bits_text.config(state=tk.DISABLED)
        except Exception:
            pass

    def _show_recovered_bits(self, extracted: np.ndarray) -> None:
        """Display recovered bits in the text widget."""
        try:
            bit_chars = ["1" if round(v) == 1 else "0" for v in extracted]
            s = "".join(bit_chars)
            max_chars = 5000
            s_view = s[:max_chars] + ("..." if len(s) > max_chars else "")
            self.recovered_bits_text.config(state=tk.NORMAL)
            self.recovered_bits_text.delete("1.0", tk.END)
            self.recovered_bits_text.insert(tk.END, s_view)
            self.recovered_bits_text.config(state=tk.DISABLED)
        except Exception:
            pass

    def _update_histograms(self) -> None:
        """Update all histogram displays."""
        def compute_hist_uint8(img: np.ndarray) -> Optional[np.ndarray]:
            if img is None:
                return None
            if img.ndim == 3:
                img_use = img[:, :, 0]
            else:
                img_use = img
            arr = img_use.astype(np.uint8).reshape(-1)
            return np.bincount(arr, minlength=256)

        def draw_hist_on_canvas(canvas: tk.Canvas, hist: Optional[np.ndarray], title: str = "") -> None:
            canvas.delete("all")
            w = max(256, int(canvas.winfo_width()) or 256)
            h = max(100, int(canvas.winfo_height()) or 100)
            canvas.create_rectangle(0, 0, w, h, fill="#222222", outline="")
            if hist is None or len(hist) == 0:
                return
            hist = hist.astype(np.float64)
            m = np.max(hist) if np.max(hist) > 0 else 1.0
            bin_w = w / 256.0
            for i in range(256):
                v = hist[i] / m
                x0 = int(i * bin_w)
                x1 = int((i + 1) * bin_w)
                y0 = int(h - v * (h - 18))
                canvas.create_rectangle(x0, y0, x1, h - 2, fill="#4caf50", outline="")
            if title:
                canvas.create_text(8, 10, text=title, anchor="w", fill="#ffffff")

        try:
            src = self.extract_cover_arr if self.extract_cover_arr is not None else self.orig_img_arr
            if src is not None:
                h = compute_hist_uint8(src)
                draw_hist_on_canvas(self.hist_left_canvas, h, title="Original")
        except Exception:
            pass
        
        try:
            src = self.extract_stego_arr if self.extract_stego_arr is not None else self.stego_img_arr
            if src is not None:
                h = compute_hist_uint8(src)
                draw_hist_on_canvas(self.hist_right_canvas, h, title="Stego")
        except Exception:
            pass
        
        try:
            if self.recovered_cover_arr is not None:
                h = compute_hist_uint8(self.recovered_cover_arr)
                draw_hist_on_canvas(self.hist_extract_canvas, h, title="Recovered Cover")
            else:
                self.hist_extract_canvas.delete("all")
        except Exception:
            pass

    # Save methods
    def _save_stego(self) -> None:
        """Save the stego image."""
        if self.stego_img_arr is None:
            messagebox.showinfo("Nothing to save", "Please run an embedding first.")
            return
        def_suffix = "_stego.tiff"
        init_name = (self.img_path.stem + def_suffix) if self.img_path else "stego.tiff"
        path = filedialog.asksaveasfilename(defaultextension=".tiff", initialfile=init_name,
                                            filetypes=[("TIFF", "*.tif *.tiff"), ("PNG", "*.png"), ("All", "*.*")])
        if not path:
            return
        try:
            out = Image.fromarray(self.stego_img_arr)
            out.save(path)
            self.status_var.set(f"Saved stego image: {Path(path).name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save stego image: {e}")

    def _save_metrics(self) -> None:
        """Save embedding metrics to CSV file."""
        if self.stego_img_arr is None:
            messagebox.showinfo("Nothing to save", "Please run an embedding first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="metrics.csv",
                                            filetypes=[("CSV", "*.csv"), ("All", "*.*")])
        if not path:
            return
        try:
            # Extract current metrics text
            psnr = self.psnr_var.get().split(":", 1)[-1].strip()
            mse = self.mse_var.get().split(":", 1)[-1].strip()
            ssim_v = self.ssim_var.get().split(":", 1)[-1].strip()
            bits = self.bits_var.get().split(":", 1)[-1].strip()
            img_name = self.img_path.name if self.img_path else ""
            bits_name = self.bits_path.name if self.bits_path else ""
            
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["Image", "Bits File", "PSNR", "MSE", "SSIM", "BitsUsed"])
                w.writerow([img_name, bits_name, psnr, mse, ssim_v, bits])
            self.status_var.set(f"Saved metrics: {Path(path).name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save metrics: {e}")

    def _save_extracted_bits(self) -> None:
        """Save extracted bits to file."""
        if self.extracted_bits is None:
            messagebox.showinfo("Nothing to save", "Please run extraction first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="extracted_bits.txt",
                                            filetypes=[("Text", "*.txt"), ("All", "*.*")])
        if not path:
            return
        try:
            bits_rounded = (np.round(self.extracted_bits).astype(int)).tolist()
            with open(path, "w", encoding="utf-8") as f:
                f.write("".join("1" if b == 1 else "0" for b in bits_rounded))
            self.status_var.set(f"Saved extracted bits: {Path(path).name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save extracted bits: {e}")


def main() -> None:
    """Main entry point for the RDJAT-Embed application."""
    app = EmbeddingApp()
    app.mainloop()


if __name__ == "__main__":
    main()