from fastapi import FastAPI
from app.routes.recipe import router as recipe_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS (Reactille)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes käyttöön
app.include_router(recipe_router)

@app.get("/")
def root():
    return {"message": "API running"}