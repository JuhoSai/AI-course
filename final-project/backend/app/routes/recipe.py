from fastapi import APIRouter
from app.models.recipe_model import RecipeRequest
from app.services.gemini_service import generate_recipe

# Router for recipe-related endpoints
router = APIRouter()

# Endpoint for generating a recipe based on user input
@router.post("/generate-recipe")
def create_recipe(data: RecipeRequest):
    return generate_recipe(data)