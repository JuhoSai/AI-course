from fastapi import APIRouter
from app.models.recipe_model import RecipeRequest
from app.services.gemini_service import generate_recipe

router = APIRouter()

@router.post("/generate-recipe")
def create_recipe(data: RecipeRequest):
    return generate_recipe(data)