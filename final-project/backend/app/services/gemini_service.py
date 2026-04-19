import google.generativeai as genai
import os
from dotenv import load_dotenv
from app.utils.prompt_builder import build_prompt
import json

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API with API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash-lite")

# Generates a recipe using the Gemini API based on input data
def generate_recipe(data):

    prompt = build_prompt(data)

    #Generate content using the Gemini model with the constructed prompt
    response = model.generate_content(prompt)

    try:
        return json.loads(response.text)
    except:
        # Fallback if response is not valid JSON
        return {
            "title": "Parse error",
            "ingredients": [],
            "steps": [response.text]
        }