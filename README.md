
# Steganography Tool

This repository contains a Python application that implements a steganography method based on the paper "A Novel Steganography Method for Gray-Scale Images Using Pixel Value Differencing and Modulo Operator" by... (Please add the correct citation).

## Features

- Embed a secret message (text file) into a grayscale image.
- Extract the secret message from a stego image.
- Calculate PSNR, MSE, and SSIM metrics to evaluate the quality of the stego image.
- Simple and easy-to-use graphical user interface.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/your-repository.git
   ```
2. Install the required libraries:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python main.py
   ```
2. Use the UI to select the cover image, secret message, and perform embedding and extracting operations.

## File Descriptions

- `main.py`: The main application file with the tkinter UI.
- `steganography.py`: Contains the core logic for embedding and extracting secret messages.
- `utils.py`: Contains utility functions, such as converting images to grayscale.
- `requirements.txt`: Lists all the necessary Python libraries to run the application.

## CodeOcean and Google Colab

This repository includes versions of the application that are compatible with CodeOcean and Google Colab.

- **CodeOcean**: The `CodeOcean` directory contains a `run` script to execute the application in the CodeOcean environment.
- **Google Colab**: The `GoogleColab` directory contains a Jupyter notebook (`.ipynb`) that can be run in Google Colab.
