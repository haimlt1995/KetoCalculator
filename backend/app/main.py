from fastapi import FastAPI, HTTPException

from app.calc import calculate_all
from app.models import CalcOutput, UserInput
from app.models_mealplan import MealPlanResponse
from app.services.llm_mealplan import generate_meal_plan

app = FastAPI(title="Keto Calculator API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/calc", response_model=CalcOutput)
def calc(user: UserInput) -> CalcOutput:
    try:
        return calculate_all(user)
    except ValueError as e:
        # Our core raises ValueError for validation/unsupported cases (e.g., minors for BMR)
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/mealplan", response_model=MealPlanResponse)
def mealplan(user: UserInput) -> MealPlanResponse:
    try:
        calc = calculate_all(user)
        return generate_meal_plan(user, calc)

    except ValueError as e:
        # Input / validation errors
        raise HTTPException(status_code=400, detail=str(e)) from e

    except RuntimeError as e:
        msg = str(e)

        # Quota / rate-limit from Gemini
        if "RESOURCE_EXHAUSTED" in msg or "RATE_LIMIT" in msg:
            raise HTTPException(status_code=429, detail=msg) from e

        # Temporary overload / retry later
        raise HTTPException(status_code=503, detail=msg) from e
