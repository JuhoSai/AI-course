from pydantic import BaseModel

# Defines the expected structure and types for incoming request data
class RecipeRequest(BaseModel):
    ingredients: str
    cuisine: str
    diet: str
    time: int