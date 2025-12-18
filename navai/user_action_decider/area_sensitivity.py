import numpy as np
import base64
import openai
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()
key = os.environ.get("OPENAI_API_KEY")

client = openai.OpenAI(api_key=key)

class coordinateStructure(BaseModel):
    topleftxlefteye: float
    topleftylefteye: float
    bottomrightxlefteye: float
    bottomrightylefteye: float
    topleftxrighteye: float
    topleftyrighteye: float
    bottomrightxrighteye: float
    bottomrightyrighteye: float

"""
Determines the coordinates of the bounding box of the left and right eye of a specified target
Image path and initial prompt are paramters
Returns the averaged area between the two eyes
"""
def getArea(imagePath, prompt):
    with open(imagePath, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode("utf-8")

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"You are seeing through virtual reality lenses, including a left and right eye. Identify the bounding box in each eye of the object described: '{prompt}'. "
                            f"Return only the top-left and bottom-right coordinates for each eye."
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                }
            ]
        }
    ]

    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=messages,
        # reasoning_effort="high",
        response_format=coordinateStructure,
        max_completion_tokens=100
        )

    parsed = response.choices[0].message.parsed

    leftA = (int(parsed.bottomrightxlefteye) - int(parsed.topleftxlefteye)) * (int(parsed.bottomrightylefteye) - int(parsed.topleftylefteye)) 

    rightA = (int(parsed.bottomrightxrighteye) - int(parsed.topleftxrighteye)) * (int(parsed.bottomrightyrighteye) - int(parsed.topleftyrighteye)) 

    return (float(leftA) + float(rightA)) / 2

"""
Determines the sensitivity of the action based on the area change
Current area, previous area, and log base are parameters
Returns a value between 0.1 and 2
"""
def sens(currA, prevA, base=5):
    if(prevA == 0): prevA = 0.1
    ratio = np.log(currA / prevA) / np.log(base)
    s = 1 / (1 + ratio)

    if ratio >= 0:
        s = 1 / (1 + ratio)
    else:
        s = 1 + abs(ratio)

    return np.clip(s, 0.1, 2)


