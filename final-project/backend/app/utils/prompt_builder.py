def build_prompt(data):

    return f"""
Return ONLY valid JSON.

Format:
{{
  "title": "",
  "ingredients": [],
  "steps": []
}}

Create recipe using:
{data.ingredients}

Cuisine: {data.cuisine}
Diet: {data.diet}
Time: {data.time} minutes
"""