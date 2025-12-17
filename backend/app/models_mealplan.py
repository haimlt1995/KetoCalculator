from pydantic import BaseModel, Field


class MealItem(BaseModel):
    name: str
    grams: float = Field(gt=0)
    notes: str | None = None


class Meal(BaseModel):
    meal_name: str  # e.g., breakfast/lunch/dinner/snack
    items: list[MealItem]
    protein_g: float = Field(ge=0)
    fat_g: float = Field(ge=0)
    net_carbs_g: float = Field(ge=0)
    calories: float = Field(ge=0)


class DayPlan(BaseModel):
    day: int  # 1..N
    meals: list[Meal]
    totals: Meal


class MealPlanResponse(BaseModel):
    days: list[DayPlan]
    shopping_list: list[str]
    assumptions: list[str]
