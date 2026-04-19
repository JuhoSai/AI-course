from fastapi import FastAPI
from app.routes.recipe import router as recipe_router
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI application
app = FastAPI()

# Configure CORS to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register application routes
app.include_router(recipe_router)

@app.get("/")
def root():
    return {"message": "API running"}