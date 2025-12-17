import os
import random
import time

from google import genai
from google.genai import errors
from google.genai.types import GenerateContentConfig

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

    client = genai.Client()
    prompt = build_prompt(user, calc)

    # Small retry loop for transient overload (503)
    attempts = 3
    base_sleep = 1.0

    last_err: Exception | None = None
    for i in range(attempts):
        try:
            resp = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=GenerateContentConfig(response_mime_type="application/json"),
            )
            text = resp.text or ""
            json_text = _extract_json(text)
            try:
                return MealPlanResponse.model_validate_json(json_text)
            except Exception as e:
                preview = (text or "")[:600].replace("\n", "\\n")
                raise RuntimeError(f"LLM returned invalid JSON. Preview: {preview}") from e

        except errors.ServerError as e:
            # Typical cause: "model is overloaded" (503)
            last_err = e
            if i == attempts - 1:
                break

            # exponential backoff with jitter
            sleep_s = base_sleep * (2**i) + random.uniform(0, 0.5)
            time.sleep(sleep_s)

        except errors.APIError as e:
            # 429 quota/rate limit
            if getattr(e, "status_code", None) == 429:
                raise RuntimeError(f"RATE_LIMIT:{e}") from e
            raise RuntimeError(f"Gemini API error: {e}") from e

    raise RuntimeError(
        "Gemini is temporarily unavailable (model overloaded). Please try again in a minute."
    ) from last_err


def _extract_json(text: str) -> str:
    t = text.strip()

    # Remove markdown code fences if present
    if t.startswith("```"):
        t = t.strip("`").strip()
        # Sometimes it starts with "json\n"
        if t.lower().startswith("json"):
            t = t[4:].strip()

    # If there's extra text before/after JSON, try to slice the first {...} block
    start = t.find("{")
    end = t.rfind("}")
    if start != -1 and end != -1 and end > start:
        return t[start : end + 1]

    return t
