import time
from openai import OpenAI
from at_point import at_point_alg
from .user_action_decider.utils import encode_image
from dotenv import load_dotenv
import os

load_dotenv()
key = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=key)

def analysisOriented(goal, region):
    start_time = time.time()
    apstart = time.time()
    
    counter = at_point_alg(region)

    apend = time.time()

    messages = []

    astart = time.time()

    messages.insert(0, {
        "role": "system",
        "content": f"You will see screenshots of the user turning around in a circle to observe what is around them."
                f"Your job is to answer the prompt: {goal}"
                f"Analyze the environment and answer the prompt."
                f"Be very descriptive in the size, distance, appearance, and types of objects around the user."
    })

    for i in range(counter):
        base64_image = encode_image(f"temp/at_point/at_point{counter}.png")

        messages.append({
            "role": "user",
            "content": [
                        {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high",
                                },
                            },
                    ]
        })

    response2 = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=messages,
    max_tokens=300,
    )  
    
    aend = time.time()

    atime = aend - astart

    end_time = time.time()
    print(f"Total Time: {end_time - start_time}")
    print(f"At-Point Algorithm Time: {apend - apstart}")
    print(f"Analysis Time: {aend - astart}")


    print(response2.choices[0].message.content)
