from navai.user_action_decider.actions import in_place_rotate_to_left
from openai import OpenAI
from pydantic import BaseModel
from navai.user_action_decider.utils import encode_image
import pyautogui as pag
from dotenv import load_dotenv
import os

load_dotenv()
key = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=key)

class TurnResult(BaseModel):
    dur: float
    end: bool


def at_point_alg(region):
    finished = False
    counter = 0
    duration = 0.5

    screenshot = pag.screenshot(region=region)
    screenshot.save(f"temp/at_point/at_point{counter}.png")
    base64_image = encode_image("temp/at_point/at_point0.png")

    message = []

    message.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "You are performing an at-point algorithm to take screenshots of the world around you to capture 360 degree view. "
                            "You will see two images, one is the original picture and one is taken after rotating left for a second."
                            "The goal is for about 50 percent of the original image to be in the next one."
                            "If it is less you want to increase the duration of the turn, and if it is more decrease the duration."
                            "You will be given images followed by the duration they turned. Use this information to output the duration you should turn."
                            "Also you will output a boolean based off of whether the turn is complete. It will be complete after a full 360. "
                            "This means if the original image (the first image) is extremely similar to the recent image, the last image, output true here."
                        }
                        
                    ],
                }
        )
    
    message.append({
        "role": "user",
        "content": [
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
        }
        ]})
    
    while not finished:
        counter += 1
        in_place_rotate_to_left(duration)

        screenshot = pag.screenshot(region=region)
        screenshot.save(f"temp/at_point/at_point{counter}.png")
        base64_image = encode_image(f"temp/at_point/at_point{counter}.png")

        

        message.append({
            "role": "user",
            "content": [
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
            }
            ]})

        message.append(
        {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Duration of previous turn: {duration}"
                        }
                        
                    ],
                }
        )
        

        response = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=message,
            response_format=TurnResult,
            max_tokens=500
        )

        output = response.choices[0].message
        finished = output.parsed.end
        duration = output.parsed.dur
        print(duration)
    
    return counter
  

