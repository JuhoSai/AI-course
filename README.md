# AI RECIPE GENERATOR
## Project overview
    This is a full-stack AI-powered web application that generates cooking recipes based on user input.
    The user enters ingredients, cuisine type, dietary prefences and cooking time.

## Architecture overview
    Follows a simple full-stack architecture
        React(Frontend) -> FastAPI(backend) -> Gemini API(LLM)
            React(Vite) = Handles user interface and send requests to the backend.
            FastAPI = Processes requests, builds prompts and communicates with the AI model
            Google Gemini = Generates the recipe based on user input

## Technical choices
    React(Vite) - Fast and simple to use.
    FastAPI - Used to build a fast and simple backend API.
    Google Gemini API - Selected due to prior familiarity.
    Axios - Used in the frontend to simplify HTTP requests to backend.
    Python-dotenv - Used to securely manage API keys.

## Setup and running instructions
    ### Prequisities
        -Python 3.10+
        -Node.js 20.19+

    1. Clone repository
    2. Backend setup
        - Open project folder in terminal

        - cd backend

        - python -m venv venv

        - Activate virtual environment:
            **Linux/macOS**:
            source venv/bin/activate
            ```
            Windows (Command Prompt)**:
            venv\Scripts\activate.bat
            ```
            Windows (PowerShell)**:
            venv\Scripts\Activate.ps1

        - pip install -r requirements.txt

        - Create .env file inside backend folder:
            GEMINI_API_KEY=your_api_key_here

        -Start the backend:
            uvicorn app.main:app --reload

        -Backend runs at:
            http://127.0.0.1:8000

    3. Frontend setup
        - Open a new terminal
        - cd Frontend
        - Use commands:
            npm install
            npm install axios
            npm run dev

        - Frontend runs at:
            http://localhost:5173

## Known limitations
    - No database — recipes are not saved
    - AI output is not always perfectly formatted JSON — responses may include extra text or formatting errors, which can cause parsing issues
    - Input validation is minimal — the application does not enforce strict validation on user inputs (e.g. empty fields, negative values), which may lead to poor AI-generated results

## AI tools used
    -ChatGPT
        -Used for project structure, debuggin and frontend/backend implementation.
    -Google Gemini API
        - Used as the main model for generating recipes.