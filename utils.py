
from PIL import Image

def convert_to_grayscale(input_path, output_path):
    try:
        with Image.open(input_path) as img:
            grayscale_img = img.convert('L')
            grayscale_img.save(output_path)
        return True
    except Exception as e:
        print(f"Error converting to grayscale: {e}")
        return False
