
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
import cv2
from steganography import embed, extract
from utils import convert_to_grayscale

class SteganographyApp:
    def __init__(self, master):
        self.master = master
        master.title("Steganography Tool")

        self.cover_image_path = None
        self.secret_message_path = None
        self.stego_image_path = None
        self.tra = None
        self.avg_arr = None

        # Create UI elements
        self.create_widgets()

    def create_widgets(self):
        # --- Main Frames ---
        embed_frame = tk.LabelFrame(self.master, text="Embed")
        embed_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        extract_frame = tk.LabelFrame(self.master, text="Extract")
        extract_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        image_frame = tk.LabelFrame(self.master, text="Images")
        image_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10)

        # --- Embed Frame Widgets ---
        self.select_cover_button = tk.Button(embed_frame, text="Select Cover Image", command=self.select_cover_image)
        self.select_cover_button.grid(row=0, column=0, padx=5, pady=5)

        self.select_secret_button = tk.Button(embed_frame, text="Select Secret Message", command=self.select_secret_message)
        self.select_secret_button.grid(row=1, column=0, padx=5, pady=5)

        self.embed_button = tk.Button(embed_frame, text="Embed Message", command=self.embed_message)
        self.embed_button.grid(row=2, column=0, padx=5, pady=5)

        # --- Extract Frame Widgets ---
        self.select_stego_button = tk.Button(extract_frame, text="Select Stego Image", command=self.select_stego_image)
        self.select_stego_button.grid(row=0, column=0, padx=5, pady=5)

        self.extract_button = tk.Button(extract_frame, text="Extract Message", command=self.extract_message)
        self.extract_button.grid(row=1, column=0, padx=5, pady=5)

        # --- Image Frame Widgets ---
        self.original_image_label = tk.Label(image_frame, text="Original Image")
        self.original_image_label.grid(row=0, column=0, padx=5, pady=5)
        self.original_image_canvas = tk.Canvas(image_frame, width=256, height=256)
        self.original_image_canvas.grid(row=1, column=0, padx=5, pady=5)

        self.stego_image_label = tk.Label(image_frame, text="Stego Image")
        self.stego_image_label.grid(row=0, column=1, padx=5, pady=5)
        self.stego_image_canvas = tk.Canvas(image_frame, width=256, height=256)
        self.stego_image_canvas.grid(row=1, column=1, padx=5, pady=5)

        self.extracted_image_label = tk.Label(image_frame, text="Extracted Image")
        self.extracted_image_label.grid(row=0, column=2, padx=5, pady=5)
        self.extracted_image_canvas = tk.Canvas(image_frame, width=256, height=256)
        self.extracted_image_canvas.grid(row=1, column=2, padx=5, pady=5)

        # --- Message and Metrics Widgets ---
        message_frame = tk.LabelFrame(self.master, text="Messages & Metrics")
        message_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        secret_message_label = tk.Label(message_frame, text="Secret Message:")
        secret_message_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.secret_message_text = tk.Text(message_frame, height=4, width=80)
        self.secret_message_text.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        extracted_message_label = tk.Label(message_frame, text="Extracted Message:")
        extracted_message_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.extracted_message_text = tk.Text(message_frame, height=4, width=80)
        self.extracted_message_text.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        metrics_label = tk.Label(message_frame, text="Metrics:")
        metrics_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.metrics_text = tk.Label(message_frame, text="PSNR: -, MSE: -, SSIM: -")
        self.metrics_text.grid(row=5, column=0, padx=5, pady=5, sticky="w")

    def select_cover_image(self):
        self.cover_image_path = filedialog.askopenfilename()
        if self.cover_image_path:
            self.display_image(self.cover_image_path, self.original_image_canvas)

    def select_secret_message(self):
        self.secret_message_path = filedialog.askopenfilename()
        if self.secret_message_path:
            with open(self.secret_message_path, 'r') as f:
                secret_message = f.read()
                self.secret_message_text.delete('1.0', tk.END)
                self.secret_message_text.insert(tk.END, secret_message)

    def embed_message(self):
        if self.cover_image_path and self.secret_message_path:
            self.stego_image_path = filedialog.asksaveasfilename(defaultextension=".tiff",
                                                               filetypes=[("TIFF files", "*.tiff"),
                                                                          ("All files", "*.*")])
            if self.stego_image_path:
                success, self.tra, self.avg_arr = embed(self.cover_image_path, self.secret_message_path, self.stego_image_path)
                if success:
                    self.display_image(self.stego_image_path, self.stego_image_canvas)
                    self.calculate_metrics()

    def select_stego_image(self):
        self.stego_image_path = filedialog.askopenfilename()
        if self.stego_image_path:
            self.display_image(self.stego_image_path, self.stego_image_canvas)

    def extract_message(self):
        if self.stego_image_path and self.tra is not None and self.avg_arr is not None:
            secret_message_length = len(self.secret_message_text.get("1.0", tk.END).strip())
            secret_message, cover_img = extract(self.stego_image_path, self.tra, self.avg_arr, secret_message_length)
            if secret_message and cover_img:
                self.extracted_message_text.delete('1.0', tk.END)
                self.extracted_message_text.insert(tk.END, secret_message)
                self.display_image(cover_img, self.extracted_image_canvas, is_pil_image=True)

    def display_image(self, image_path_or_pil_image, canvas, is_pil_image=False):
        if is_pil_image:
            img = image_path_or_pil_image
        else:
            img = Image.open(image_path_or_pil_image)
        
        img.thumbnail((256, 256))
        photo = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        canvas.image = photo

    def calculate_metrics(self):
        if self.cover_image_path and self.stego_image_path:
            cover_img = np.array(Image.open(self.cover_image_path).convert('L'))
            stego_img = np.array(Image.open(self.stego_image_path).convert('L'))

            mse = np.mean((cover_img - stego_img) ** 2)
            if mse == 0:
                psnr = 100
            else:
                max_pixel = 255.0
                psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
            
            ssim = self.ssim(cover_img, stego_img)

            self.metrics_text.config(text=f"PSNR: {psnr:.2f} dB, MSE: {mse:.2f}, SSIM: {ssim:.4f}")

    def ssim(self, img1, img2):
        C1 = (0.01 * 255)**2
        C2 = (0.03 * 255)**2

        img1 = img1.astype(np.float64)
        img2 = img2.astype(np.float64)
        kernel = cv2.getGaussianKernel(11, 1.5)
        window = np.outer(kernel, kernel.transpose())

        mu1 = cv2.filter2D(img1, -1, window)[5:-5, 5:-5]  # valid
        mu2 = cv2.filter2D(img2, -1, window)[5:-5, 5:-5]
        mu1_sq = mu1**2
        mu2_sq = mu2**2
        mu1_mu2 = mu1 * mu2
        sigma1_sq = cv2.filter2D(img1**2, -1, window)[5:-5, 5:-5] - mu1_sq
        sigma2_sq = cv2.filter2D(img2**2, -1, window)[5:-5, 5:-5] - mu2_sq
        sigma12 = cv2.filter2D(img1 * img2, -1, window)[5:-5, 5:-5] - mu1_mu2

        ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / ((mu1_sq + mu2_sq + C1) *
                                                              (sigma1_sq + sigma2_sq + C2))
        return ssim_map.mean()

if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()
