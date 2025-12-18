import openai
from pydantic import BaseModel
from navai.models import ResponseCategory
from dotenv import load_dotenv
import os

load_dotenv()
key = os.environ.get("OPENAI_API_KEY")

CATEGORIZATION_PROMPT = """You are NavAI, an assistant controlling navigation in a virtual 3D environment.

Classify the user's goal into exactly one category.

CATEGORIES:

0 - ACTION_ORIENTED
Direct movement commands. No specific target, no questions.
Examples: "Move forward", "Turn left", "Walk around this object", "Stop"

1 - GENERAL_INQUIRY  
Questions or requests for information about the scene.
Examples: "What do you see?", "What's the biggest object?", "Where am I?"

2 - TASK_ORIENTED
Movement toward a specific target or goal-driven navigation.
Examples: "Go to the yellow bus", "Find the red car", "Enter the building"

DECISION RULES:
- If it's a question → 1
- If it mentions a specific target/destination → 2
- If it's pure movement with no target → 0

USER GOAL: {goal}

Respond with ONLY: 0, 1, or 2"""

client = openai.OpenAI(api_key=key)

class outputStructure(BaseModel):
    requestCategory: int

def build_categorization_prompt(goal: str) -> str:
    return CATEGORIZATION_PROMPT.format(goal=goal)

def categorizeQuery(goal) ->  ResponseCategory:
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": build_categorization_prompt(goal)
                },
            ]
        }
    ]
    #TODO:  schema for above message
    #TODO: Make 'text' more structured
    #TODO: future more prompt engineering()
    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=messages,
        response_format=outputStructure,
        max_completion_tokens=100
        )

    return ResponseCategory(response.choices[0].message.parsed.requestCategory)