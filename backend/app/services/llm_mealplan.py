import os

from google import genai

from app.models import CalcOutput, UserInput
from app.models_mealplan import MealPlanResponse

SCHEMA_EXAMPLE = """
{
  "days": [
    {
      "day": 1,
      "meals": [
        {
          "meal_name": "lunch",
          "items": [
            {"name": "chicken breast", "grams": 200, "notes": "grilled"}
          ],
          "protein_g": 0,
          "fat_g": 0,
          "net_carbs_g": 0,
          "calories": 0
        }
      ],
      "totals": {
        "meal_name": "totals",
        "items": [],
        "protein_g": 0,
        "fat_g": 0,
        "net_carbs_g": 0,
        "calories": 0
      }
    }
  ],
  "shopping_list": ["..."],
  "assumptions": ["..."]
}
""".strip()


def build_prompt(user: UserInput, calc: CalcOutput) -> str:
    # user isn't used yet, but keep it for future personalization (preferences/allergies/etc.)
    _ = user

    return "\n".join(
        [
            "You are a nutrition assistant. Create a keto meal plan.",
            "",
            "Rules:",
            f"- Net carbs target: {calc.macros.net_carbs_g:.0f}g/day",
            f"- Protein target: {calc.macros.protein_g:.0f}g/day",
            f"- Fat target: {calc.macros.fat_g:.0f}g/day",
            f"- Calories target: {calc.macros.calories_total:.0f} kcal/day",
            "- Output MUST be valid JSON that matches this schema exactly:",
            SCHEMA_EXAMPLE,
            "",
            "Constraints:",
            "- Use common foods; include grams for each item.",
            "- Avoid alcohol.",
            "- Keep it simple and repeatable.",
            "- If user is imperial, you can still output grams (preferred).",
            "- Return JSON only. No markdown, no extra text.",
        ]
    )


def generate_meal_plan(user: UserInput, calc: CalcOutput) -> MealPlanResponse:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set")

    client = genai.Client(api_key=api_key)

    prompt = build_prompt(user, calc)

    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    text = resp.text or ""
    return MealPlanResponse.model_validate_json(text)
