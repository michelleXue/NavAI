import google.generativeai as genai
from dotenv import load_dotenv
from pydantic import BaseModel
from PIL import Image
import json
import os

load_dotenv()
key = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=key)


class end(BaseModel):
    accomplished: bool


def gemini_vote(goal, path, s):
    image = Image.open(path)

    prompt = (
        f"Your goal was: {goal}. "
        "This was a task oriented goal where an AI had to perform actions to achieve it. "
        f"Distance metrics over time: {s}. "
        "Have you accomplished the goal based on this image? "
        "Respond ONLY with valid JSON in this exact format: {\"accomplished\": true} or {\"accomplished\": false}"
    )

    # Use one of the available models - gemini-2.5-flash is fast and good
    model = genai.GenerativeModel(
        'models/gemini-2.5-flash',
        generation_config={
            "response_mime_type": "application/json",
        }
    )

    response = model.generate_content([prompt, image])

    # Parse the JSON response and return boolean
    try:
        result = json.loads(response.text)
        return result.get('accomplished', False)
    except json.JSONDecodeError:
        # Fallback: check if response contains "true"
        print(f"Warning: Could not parse JSON response: {response.text}")
        return 'true' in response.text.lower()