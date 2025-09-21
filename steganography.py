
import numpy as np
from PIL import Image

def embed(cover_image_path, secret_message_path, stego_image_path):
    try:
        # Import image and secret message
        img = Image.open(cover_image_path).convert('L')
        img_arr = np.array(img, dtype=np.float64)
        
        with open(secret_message_path, 'r') as f:
            secret_message = f.read().strip()
        
        b = np.array([int(bit) for bit in secret_message], dtype=np.int8)

        if len(b) > 90000:
            b = b.flatten()

        # Flatten image
        p = img_arr.flatten()

        # Range
        n = 5
        max_val = 256
        max_range = 260
        edges = np.arange(0, max_range + n, n)

        # Histogram Count
        count, _ = np.histogram(p, bins=edges)

        # Sum of Values each Group
        sum_each = np.histogram(img_arr, bins=np.arange(max_val + 1))[0]
        sum_group = np.zeros(len(count))
        for i in range(max_val):
            index = int(np.floor(i / n))
            sum_group[index] += sum_each[i] * i

        # DE
        avg_arr = np.zeros_like(p)
        ec = 0
        counter = 0
        tra = np.zeros_like(p)
        pp = np.zeros_like(p)

        for i in range(len(p)):
            index = int(np.floor(p[i] / n))
            if count[index] > 0:
                avg_arr[i] = np.ceil(sum_group[index] / count[index])
            else:
                avg_arr[i] = 0


            if 4 < p[i] <= 249:
                ec += 1

            if 4 < p[i] <= 249 and counter < len(b):
                d = p[i] - avg_arr[i]
                dp = d + b[counter]
                pp[i] = p[i] + dp
                tra[i] = 1
                counter += 1
            else:
                pp[i] = p[i]

        stego_img_arr = pp.reshape(img_arr.shape)
        stego_img = Image.fromarray(np.uint8(stego_img_arr))
        stego_img.save(stego_image_path)

        return True, tra, avg_arr

    except Exception as e:
        print(f"Error embedding: {e}")
        return False, None, None

def extract(stego_image_path, tra, avg_arr, secret_message_length):
    try:
        stego_img = Image.open(stego_image_path)
        stego_arr = np.array(stego_img, dtype=np.float64)
        steg_arr_flat = stego_arr.flatten()

        secret = np.zeros(secret_message_length, dtype=np.int8)
        cover_arr = np.zeros_like(steg_arr_flat)
        h = 0

        for i in range(len(steg_arr_flat)):
            if h < secret_message_length and tra[i] == 1:
                secret[h] = int(np.mod(steg_arr_flat[i] - avg_arr[i], 2))
                cover_arr[i] = np.floor((steg_arr_flat[i] + avg_arr[i] - secret[h]) / 2)
                h += 1
            else:
                cover_arr[i] = steg_arr_flat[i]

        cover_img_arr = cover_arr.reshape(stego_arr.shape)
        cover_img = Image.fromarray(np.uint8(cover_img_arr))
        
        secret_message = "".join(map(str, secret))

        return secret_message, cover_img

    except Exception as e:
        print(f"Error extracting: {e}")
        return None, None
