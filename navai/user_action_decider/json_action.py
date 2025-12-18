from openai import OpenAI
from pydantic import BaseModel
from navai.user_action_decider.actions import *
from navai.user_action_decider.orbit import go_around
from navai.user_action_decider.utils import encode_image
from dotenv import load_dotenv
import os

load_dotenv()
key = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=key)


class actionFormat(BaseModel):
    action: str
    duration: float

# Determines and performs the next action based off of previous and current steps
# Json description, target object, image path, sensitivity, previous steps, and counter are parameters
# Returns action and duration performed
def determine_action(desc, target, image_path, s, context, counter, region):
    messages = []

    for i in range(counter + 1):
        history = (
            f"Action: {context[0][i]}\n"
            f"Area of Target: {context[2][i]}\n"
            f"Sensitivity: {context[3][i]}\n"
            f"Object data: {context[4][i]}"
        )  

        base64_image = encode_image(context[1][i])

        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": history},
                {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high",
                            },
                        },
            ]
        })

    messages.insert(0, {
        "role": "system",
        "content": f"The target you must reach is: {target}. "
                f"You can choose actions: move_forward, move_backward, move_left, move_right, in_place_rotate_to_left, "
                f"in_place_rotate_to_right, go_around_left, and go_around_right (as in orbit the object in front of you). If the goal is to go around something you can use those last two."
                f"Format response as: 'move_left 2.5'. "
                f"Use your past actions and image history to choose the next step wisely."
    })

    base64_image = encode_image(image_path)

    messages.append({
        "role": "user",
        "content": [
                    {"type": "text", "text": desc},
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
    response_format=actionFormat,
    max_tokens=300,
    )  

    output = response2.choices[0].message

    if not output.refusal:
        print(output.parsed)

        dur = output.parsed.duration * s
        match output.parsed.action:
            case "move_forward":
                move_forward(dur)
            case "move_backward":
                move_backward(dur)
            case "move_left":
                move_left(dur)
            case "move_right":
                move_right(dur)
            case "in_place_rotate_to_left":
                in_place_rotate_to_left(dur)
            case "in_place_rotate_to_right":
                in_place_rotate_to_right(dur)
            case "look_down":
                look_down(dur)
            case "look_up":
                look_up(dur)
            case "go_around_left":
                go_around(dur, 'a', region)
            case "go_around_right":
                go_around(dur, 'd', region)
            
    else:
        print(output.refusal)

    return output.parsed.action + str(dur)
