from fastapi import APIRouter, FastAPI, HTTPException

from app.calc import calculate_all
from app.models import CalcOutput, UserInput
from app.models_mealplan import MealPlanResponse
from app.services.llm_mealplan import generate_meal_plan

app = FastAPI(title="Keto Calculator API", version="0.1.0")
api = APIRouter(prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}


# --- shared handlers (one source of truth) ---
def do_calc(user: UserInput) -> CalcOutput:
    try:
        return calculate_all(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


def do_mealplan(user: UserInput) -> MealPlanResponse:
    try:
        calc = calculate_all(user)
        return generate_meal_plan(user, calc)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        msg = str(e)
        if "RESOURCE_EXHAUSTED" in msg or "RATE_LIMIT" in msg:
            raise HTTPException(status_code=429, detail=msg) from e
        raise HTTPException(status_code=503, detail=msg) from e


# --- old routes (tests + local dev) ---
@app.post("/calc", response_model=CalcOutput)
def calc(user: UserInput) -> CalcOutput:
    return do_calc(user)


@app.post("/mealplan", response_model=MealPlanResponse)
def mealplan(user: UserInput) -> MealPlanResponse:
    return do_mealplan(user)


# --- new routes (CloudFront /api/*) ---
@api.get("/health")
def api_health():
    return {"status": "ok"}


@api.post("/calc", response_model=CalcOutput)
def api_calc(user: UserInput) -> CalcOutput:
    return do_calc(user)


@api.post("/mealplan", response_model=MealPlanResponse)
def api_mealplan(user: UserInput) -> MealPlanResponse:
    return do_mealplan(user)


app.include_router(api)
