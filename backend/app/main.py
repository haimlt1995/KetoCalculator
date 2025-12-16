from fastapi import FastAPI, HTTPException

from app.calc import calculate_all
from app.models import CalcOutput, UserInput

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
