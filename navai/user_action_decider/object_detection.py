import os
from openai import OpenAI
from pydantic import BaseModel
from typing import List
from navai.user_action_decider.utils import encode_image, call_api
from dotenv import load_dotenv
import os

load_dotenv()
key = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=key)


class DetectedObject(BaseModel):
    object_name: str
    relationship_with_user_horizontal: str
    relationship_with_user_vertical: str
    relationship_with_user_distance: str


class SceneAnalysis(BaseModel):
    objects: List[DetectedObject]
    scene_type: str


class TargetAnalysis(BaseModel):
    target_object_name: str
    target_area: float


class DetectedSpatialRelationshipObject(BaseModel):
    object_name: str
    spatial_relationship_with_user: str


class SceneSpatialRelationshipAnalysis(BaseModel):
    objects: List[DetectedSpatialRelationshipObject]


DETECTION_PROMPT = """
Your task is to analyze the provided image and return structured data. Follow these rules strictly:

1. Scene:
   - List every object individually. 

2. For each object, provide:
   - Name: The object name with a unique identifier (e.g., 'Chair A', 'Chair B').
   - Spatial Relationship:
     - Horizontal: Specify left, middle, or right.
     - Vertical: Specify up, down, or center.
     - Distance: Specify near, mid-range, or far.
"""


VERIFICATION_PROMPT = """
Examine the image carefully to see if there are any missing items. If there are, add them and return the complete JSON.
"""

TARGET_PROMPT = """
Specify which object is the target based on the goal which is: 
"""


def detect_objects(
    image_path, goal, prompts=[DETECTION_PROMPT, VERIFICATION_PROMPT, TARGET_PROMPT]
):
    """Detect and analyze objects in the image"""
    base64_image = encode_image(image_path)
    messages = []
    result = None
    result_target = None

    class_type = SceneAnalysis

    for i, current_prompt in enumerate(prompts):
        if i == 0:
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high",
                            },
                        },
                        {"type": "text", "text": current_prompt},
                    ],
                }
            )
            result = call_api(messages, SceneAnalysis)
        if i == 1:
            messages.extend(
                [
                    {
                        "role": "assistant",
                        "content": [{"type": "text", "text": result}],
                    },
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": current_prompt}],
                    },
                ]
            )
            result = call_api(messages, SceneAnalysis)
        else:
            messages.extend(
                [
                    {
                        "role": "assistant",
                        "content": [{"type": "text", "text": result}],
                    },
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": current_prompt + goal}],
                    },
                ]
            )

            result_target = call_api(messages, TargetAnalysis)

    # Save result
    image_filename = os.path.splitext(os.path.basename(image_path))[0]
    json_path = os.path.join("screenshotjson", f"{image_filename}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(result)

    return result_target


if __name__ == "__main__":
    prompts = [DETECTION_PROMPT, VERIFICATION_PROMPT]
    detect_objects("temp/screenshot_compressed/screenshot4.png", prompts)
