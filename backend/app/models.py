from enum import Enum

from pydantic import BaseModel, Field


# contains all user basic inputs and output models
class UnitSystem(str, Enum):
    metric = "metric"
    imperial = "imperial"


class Sex(str, Enum):
    male = "male"
    female = "female"


class Goal(str, Enum):
    lose = "lose"
    maintain = "maintain"
    gain = "gain"


class ActivityLevel(str, Enum):
    sedentary = "sedentary"
    light = "light"
    moderate = "moderate"
    very = "very"
    athlete = "athlete"


class Macros(BaseModel):
    calories_total: float
    protein_g: float
    fat_g: float
    net_carbs_g: float


class ForecastPoint(BaseModel):
    week: int
    weight_kg: float


class DietaryPreferences(BaseModel):
    kosher: bool = False
    halal: bool = False
    vegan: bool = False
    vegetarian: bool = False


class MealPlanPreferences(BaseModel):
    # 1 = OMAD, 2-6 = meals/day
    meals_per_day: int = Field(default=3, ge=1, le=6)
    # 1-7 days
    days: int = Field(default=1, ge=1, le=7)


class UserInput(BaseModel):
    unit_system: UnitSystem = UnitSystem.metric
    sex: Sex
    age_years: int = Field(ge=10, le=100)
    goal: Goal = Goal.maintain

    # Metric
    height_cm: float | None = Field(default=None, gt=0)
    weight_kg: float | None = Field(default=None, gt=0)

    # Imperial
    height_in: float | None = Field(default=None, gt=0)
    weight_lb: float | None = Field(default=None, gt=0)

    activity_level: ActivityLevel

    # Keto config
    net_carbs_g: float = Field(default=25, ge=0, le=100)
    protein_g_per_kg: float = Field(default=1.8, ge=0.5, le=4.0)

    # Dietary preferences
    dietary: DietaryPreferences = Field(default_factory=DietaryPreferences)

    # Meal plan preferences
    mealplan: MealPlanPreferences = Field(default_factory=MealPlanPreferences)


class CalcOutput(BaseModel):
    bmi: float
    bmr: float
    tdee: float
    body_fat_percent_estimate: float | None
    ffmi: float | None
    macros: Macros
    forecast: list[ForecastPoint]
