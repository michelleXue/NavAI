import base64
import cv2
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()
key = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=key)


class end(BaseModel):
    accomplished: bool

def gpt_vote(goal, path, s):
    img = cv2.imread(path)
    success, buffer = cv2.imencode(".jpg", img)
    base64_image = base64.b64encode(buffer).decode("utf-8")

    end_condition = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are using a virtual reality assistant and this image is what you are seeing.",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Your goal was: {goal}"
                        "This was a task oriented goal where you had to perform actions to achieve it"
                        "For example, if you were told to walk up to an object, are you reasonably close to the object?"
                        "I also will give you a list of numbers. For each action, the number is smaller than 1 if the user gets closer to the target object and larger than one if the user gets further."
                        "The smaller the number the closer the user got and the larger the further. Each number is relative to the last position.  If the number is 1 the user did not move."
                        "You can use this to tell if the user has been getting closer or cannot get any closer in order to better inform you decision. However, mostly use the image to decide."
                        f"Here is the list: {s}"
                        "Have you accomplished the goal based on this image of what you are seeing?",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            },
        ],
        response_format=end,
        max_tokens=500,
    )

    output = end_condition.choices[0].message
    return output.parsed.accomplished