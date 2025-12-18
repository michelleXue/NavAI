from .user_action_decider.actions import *
from openai import OpenAI

from .user_action_decider.orbit import go_around
from .user_action_decider.utils import encode_image
from dotenv import load_dotenv
import os

load_dotenv()
key = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=key)

def actionOriented(goal, region):

    start_time = time.time()

    response = client.beta.chat.completions.parse(
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
                        "text": f"You were given the prompt: {goal}, and determined that this is an action oriented request."
                        "In action oriented requests, you simply perform an action, for example you may be requested to move forward then turn left." 
                        "Turn the given prompt into a list of action and durations. With the previous example you would return 'move_forward 2 turn_left 2'" 
                        "You can assume the duration if it is not given. The unit for duration is seconds. Return only the string of actions and durations separated by spaces. "
                        "An integer duration MUST follow an action, if the user does not give one add one. Output should be: action duration action duration etc." 
                        "The actins you can choose from are : move_forward, move_backward, move_left, move_right, in_place_rotate_to_left, in_place_rotate_to_right, go_around_left, and go_around_right"
                        "(as in orbit the object in front of you). If the goal is to go around something you can use those last two. Turn the prompt into some combination of these."
                    },
                ],
            },
        ],
        max_tokens=500,
    )

    output = response.choices[0].message.content
    print(output)

    action_list = output.split()

    for i in range(0, len(action_list), 2):
        dur = int(action_list[i+1])
        match action_list[i]:
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

    end_time = time.time()
    screenshot("HighwayRotateLeft", region)
    print(end_time - start_time)
