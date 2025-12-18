from navai.user_action_decider.actions import *
from navai.user_action_decider.utils import encode_image
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()
key = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=key)


class durFormat(BaseModel):
    duration: float

def go_around(dur, key, region):
    for i in range(3):
        hold_key(key, dur)

        screenshot(i, region, True)
        base64_image = encode_image(f"temp/orbit_screenshots/screenshot{i}.png")

        response = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[{
            "role": "user",
            "content": [
                        {"type": "text", "text": "You have just moved in order to orbit the object in front of you. Now you must center the object in your view before you move again. How many seconds should you rotate to recenter this object. Respond with how many seconds. 1 is a lot, 0.1 is a little."},
                        {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high",
                                },
                            },
                    ]
        }],
        response_format=durFormat,
        max_tokens=300,
        )  

        output = response.choices[0].message.parsed.duration

        if key == 'a':
            hold_key("right", output)
        else:
            hold_key("left", output)




