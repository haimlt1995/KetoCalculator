# :avocado: Keto Calculator

A full-stack keto nutrition calculator that estimates calories, macros, and a weekly weight projection from user inputs - with optional AI-generated keto meal plans.

> Educational / academic project focused on clean architecture, testability, and scientifically grounded formulas.

## :sparkles: Features

### :abacus: Core calculations

- Metric and imperial inputs (normalized internally)
- BMI (Body Mass Index)
- BMR (Basal Metabolic Rate - Mifflin-St Jeor)
- TDEE (Total Daily Energy Expenditure)
- Approximate body fat %
- FFMI (Fat-Free Mass Index)
- Goal-based calorie adjustment
  - Lose: ~20% deficit
  - Maintain
  - Gain: ~20% surplus
- Keto macros (protein / fat / net carbs)
- Weekly weight forecast chart (frontend)

### :robot: LLM meal plan generation (optional)

- AI-generated keto meal plans based on your calculated macros
- Structured JSON output (`days` -> `meals` -> `items` with grams, plus totals)
- Shopping list + assumptions included
- Uses Google Gemini API (free tier)

**Notes**
- LLM output is non-deterministic and may be rate-limited (free tier).
- Intended as a planning aid, not strict guidance.

## :toolbox: Tech stack

**Backend**
- Python 3.12, FastAPI
- `uv` dependency management
- Pytest + Ruff
- Docker

**Frontend**
- React + Vite

**Infrastructure**
- Docker Compose
- Environment-based secrets

## :open_file_folder: Project structure

```text
KetoCalculator/
  backend/
    app/
      formulas/          # Calculation logic
      units.py           # Metric / imperial normalization
      calc.py            # Calculation orchestration
      services/          # LLM integration
      main.py            # FastAPI entry point
    tests/               # Pytest test suite
    Dockerfile
    pyproject.toml
  frontend/
    src/                 # React UI
    vite.config.js       # Dev proxy to backend
    package.json
  docker-compose.yml
  README.md
```

## :rocket: Run locally (recommended)

### Backend (FastAPI)

**Requirements:** Python 3.12, `uv`

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

### Frontend (Vite + React)

**Requirements:** Node.js (LTS), npm

```bash
cd frontend
npm install
npm run dev -- --host
```

- Frontend: `http://localhost:5173`
- API requests are proxied to the backend via Vite config.

## :whale: Run with Docker

### Backend only

```bash
docker build -t keto-api ./backend
docker run --rm -p 8000:8000 keto-api
```

### Full setup (recommended)

```bash
docker compose up --build
```

## :lock: Environment variables

Create a `.env` file in the repo root (do not commit it):

```bash
GEMINI_API_KEY=your_google_api_key_here
```

Docker Compose automatically loads `.env`.

## :white_check_mark: Tests & code quality

From `backend/`:

```bash
uv run pytest
uv run ruff format .
uv run ruff check .
```

- Core formulas are unit-tested
- LLM prompt logic is tested without calling the API

## :test_tube: Meal plan JSON shape (example)

```json
{
  "days": [
    {
      "day": 1,
      "meals": [
        {
          "meal_name": "lunch",
          "items": [{ "name": "chicken breast", "grams": 200, "notes": "grilled" }],
          "protein_g": 60,
          "fat_g": 8,
          "net_carbs_g": 0,
          "calories": 320
        }
      ],
      "totals": {
        "meal_name": "totals",
        "items": [],
        "protein_g": 120,
        "fat_g": 120,
        "net_carbs_g": 20,
        "calories": 2000
      }
    }
  ],
  "shopping_list": ["..."],
  "assumptions": ["..."]
}
```

## :brain: Scientific basis (high level)

All core calculations are based on commonly accepted scientific models:

- BMI - World Health Organization definition
- BMR - Mifflin-St Jeor equation
- TDEE - activity multiplier method
- Weight change - ~7,700 kcal per 1 kg fat mass (simplified heuristic)
- Body fat % (estimate) - BMI-based approximation
- FFMI - fat-free mass normalized by height

## :books: References

- WHO - Body Mass Index: https://www.who.int/data/gho/data/themes/theme-details/GHO/body-mass-index
- Hall et al., 2011 - energy balance & weight change: https://doi.org/10.1016/j.metabol.2010.11.012

## :warning: Disclaimer

This application provides estimates only for educational and demonstration purposes.
It is not medical advice. Consult qualified professionals for personalized nutrition or health decisions.
