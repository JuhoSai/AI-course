from pydantic import BaseModel

class RecipeRequest(BaseModel):
    ingredients: str
    cuisine: str
    diet: str
    time: int