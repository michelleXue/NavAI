import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
key = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=key)

print("Available models that support generateContent:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"  - {model.name}")