import google.generativeai as genai
import os
from dotenv import load_dotenv
from app.utils.prompt_builder import build_prompt
import json

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash-lite")


def generate_recipe(data):

    prompt = build_prompt(data)

    response = model.generate_content(prompt)

    try:
        return json.loads(response.text)
    except:
        return {
            "title": "Parse error",
            "ingredients": [],
            "steps": [response.text]
        }