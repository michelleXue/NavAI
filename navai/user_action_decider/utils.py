import cv2
import base64
import os
import numpy as np
import json
from openai import OpenAI
from dotenv import load_dotenv
import os

def call_api(messages, response_model):
    """Make API call to OpenAI"""
    load_dotenv()
    key = os.environ.get("OPENAI_API_KEY")

    client = OpenAI(api_key=key)

    return (
        client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06", messages=messages, response_format=response_model
        )
        .choices[0]
        .message.content
    )


def encode_image(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at path: {image_path}")

    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"cv2.imread failed to load image: {image_path}")

    success, buffer = cv2.imencode(".jpg", image)
    if not success:
        raise ValueError("Image encoding failed.")

    return base64.b64encode(buffer).decode("utf-8")


def compress_images_in_folder(input_folder, output_folder, target_size=512):
    """
    Compress all images in a folder to specified size while maintaining aspect ratio with white borders

    Args:
        input_folder: Input folder path
        output_folder: Output folder path
        target_size: Target size (default 512x512)
    """
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Supported image formats
    image_extensions = [".jpg", ".jpeg", ".png", ".bmp"]

    for filename in os.listdir(input_folder):
        # Check if file is an image
        if any(filename.lower().endswith(ext) for ext in image_extensions):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            # Read image
            img = cv2.imread(input_path)
            if img is None:
                continue

            # Calculate scaling ratio
            h, w = img.shape[:2]
            ratio = min(target_size / w, target_size / h)

            # Calculate new dimensions
            new_w = int(w * ratio)
            new_h = int(h * ratio)

            # Resize image
            resized = cv2.resize(img, (new_w, new_h))

            # Create white background
            white_bg = np.full((target_size, target_size, 3), 255, dtype=np.uint8)

            # Calculate center position
            x_offset = (target_size - new_w) // 2
            y_offset = (target_size - new_h) // 2

            # Place resized image on white background
            white_bg[y_offset : y_offset + new_h, x_offset : x_offset + new_w] = resized

            # Save image
            cv2.imwrite(output_path, white_bg)


def draw_boxes_from_json(image_folder, json_folder, output_folder=None):
    """
    Draw bounding boxes on images based on coordinates from JSON files

    Args:
        image_folder: Folder containing original images
        json_folder: Folder containing JSON files with bounding box coordinates
        output_folder: Folder to save annotated images (defaults to json_folder)
    """
    # Use json_folder as output_folder if none specified
    if output_folder is None:
        output_folder = json_folder

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Supported image formats
    image_extensions = [".jpg", ".jpeg", ".png", ".bmp"]

    for filename in os.listdir(image_folder):
        # Check if file is an image
        if any(filename.lower().endswith(ext) for ext in image_extensions):
            # Get corresponding JSON file name (assuming same name, different extension)
            json_filename = os.path.splitext(filename)[0] + ".json"
            json_path = os.path.join(json_folder, json_filename)

            if not os.path.exists(json_path):
                continue

            # Read image
            image_path = os.path.join(image_folder, filename)
            img = cv2.imread(image_path)
            if img is None:
                continue

            # Read JSON file
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.loads(f.read())
                scene = data  # Assuming the JSON structure matches what you need

            # Draw boxes for each object
            for obj in scene["objects"]:  # Adjust according to your JSON structure
                # Convert coordinates to integers
                x1 = int(obj["left_top_coordinate_x"])
                y1 = int(obj["left_top_coordinate_y"])
                x2 = int(obj["right_bottom_coordinate_x"])
                y2 = int(obj["right_bottom_coordinate_y"])

                # Draw rectangle
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Add label
                cv2.putText(
                    img,
                    obj["object_name"],
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 255, 0),
                    2,
                )

            # Save annotated image
            output_path = os.path.join(output_folder, filename)
            cv2.imwrite(output_path, img)


if __name__ == "__main__":
    # compress_images_in_folder("temp/screenshot_original", "temp/screenshot_compressed")
    draw_boxes_from_json("temp/screenshot_original", "temp/screenshot_compressed")
