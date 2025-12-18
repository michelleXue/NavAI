import os
from PIL import Image
import matplotlib.pyplot as plt

IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg')

def grid(input_dir, output_dir):
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(IMAGE_EXTENSIONS):
            input_path = os.path.join(input_dir, filename)
            image = Image.open(input_path)

            plt.figure(figsize=(12, 6))
            plt.imshow(image)
            plt.grid(True, linestyle='--', color='white', alpha=0.5)
            plt.axis('on')
            plt.title(f'Grid View: {filename}')

            output_filename = os.path.splitext(filename)[0] + f'.png'
            output_path = os.path.join(output_dir, output_filename)
            plt.savefig(output_path, bbox_inches='tight')
            plt.close()

            # print(f"Processed and saved: {output_path}")
