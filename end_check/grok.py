import base64
import logging
import cv2
import grpc
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
from xai_sdk import Client
from xai_sdk.chat import user, image
import os
import re

load_dotenv()
key = os.environ.get("GROK_API_KEY")

client = Client(api_key=key)

class end(BaseModel):
    accomplished: bool

def extract_json_from_code_block(text):
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    return text 

def grok_vote(goal, path, s):
    chat = client.chat.create(model="grok-2-vision")

    img = cv2.imread(path)
    success, buffer = cv2.imencode(".jpg", img)
    base64_image = base64.b64encode(buffer).decode("utf-8")

    chat.append(
        user(
        f"Your goal was: {goal}"
        "This was a task oriented goal where you had to perform actions to achieve it"
        "For example, if you were told to walk up to an object, are you reasonably close to the object?"
        "Have you accomplished the goal based on this image of what you are seeing?"
        "I also will give you a list of numbers. For each action, the number is smaller than 1 if the user gets closer to the target object and larger than one if the user gets further."
        "The smaller the number the closer the user got and the larger the further. Each number is relative to the last position.  If the number is 1 the user did not move."
        "You can use this to tell if the user has been getting closer or cannot get any closer in order to better inform you decision. However, mostly use the image to decide."
        f"Here is the list: {s}",
        "Please respond ONLY in the following JSON format: {\"accomplished\": true} or {\"accomplished\": false}.",
        image(image_url=f"data:image/jpeg;base64,{base64_image}", detail="high"),
    )
    )

    try:
        response = chat.sample()
        raw = extract_json_from_code_block(response.content)
        result = end.model_validate_json(raw)
        return result.accomplished

    except grpc.RpcError as e:
        logging.error(f"[gRPC ERROR] {e.code()}: {e.details()}")
        return False 

    except ValidationError as ve:
        logging.error(f"[Validation ERROR] Invalid response format: {ve}")
        logging.debug(f"Raw response: {response.content}")
        return False 

    except Exception as ex:
        logging.error(f"[UNEXPECTED ERROR] {type(ex).__name__}: {ex}")
        return False