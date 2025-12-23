import json
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


# mealplan prompt helpers
def _mealplan_pref_lines(user: UserInput) -> list[str]:
    mp = user.mealplan
    lines: list[str] = [
        f"- Number of days: {mp.days}. Output exactly this many day entries.",
        f"- Meals per day: {mp.meals_per_day} ({'OMAD' if mp.meals_per_day == 1 else 'standard'})",
        "- Each day MUST contain exactly `meals_per_day` meals.",
        "- Use these meal_name values:",
    ]

    if mp.meals_per_day == 1:
        lines.append('  - "meal"')
    else:
        # Simple consistent naming, still flexible
        # (If 2 meals: lunch+dinner; 3: breakfast+lunch+dinner; 4+: add snacks)
        base = ['"breakfast"', '"lunch"', '"dinner"', '"snack"', '"snack2"', '"snack3"']
        lines.append("  - " + ", ".join(base[: mp.meals_per_day]))

    return lines


# dietary preference helpers
def _dietary_lines(user: UserInput) -> list[str]:
    prefs = user.dietary

    rules: list[str] = []
    if prefs.vegan:
        rules.append("- Must be VEGAN (no meat, fish, eggs, dairy, honey).")
    elif prefs.vegetarian:
        rules.append("- Must be VEGETARIAN (no meat or fish).")

    if prefs.kosher:
        rules.append("- Must be KOSHER (no pork/shellfish; do not mix meat and dairy).")

    if prefs.halal:
        rules.append("- Must be HALAL (no pork/alcohol; halal meat only if meat is included).")

    if not rules:
        rules.append("- No special dietary restrictions.")

    return rules


def build_prompt(user: UserInput, calc: CalcOutput) -> str:
    dietary_rules = _dietary_lines(user)
    mealplan_rules = _mealplan_pref_lines(user)

    return "\n".join(
        [
            "You are a nutrition assistant. Create a keto meal plan.",
            "",
            "Rules:",
            f"- Net carbs target: {calc.macros.net_carbs_g:.0f}g/day",
            f"- Protein target: {calc.macros.protein_g:.0f}g/day",
            f"- Fat target: {calc.macros.fat_g:.0f}g/day",
            f"- Calories target: {calc.macros.calories_total:.0f} kcal/day",
            *mealplan_rules,
            "- Output MUST be valid JSON that matches this schema exactly:",
            SCHEMA_EXAMPLE,
            "",
            "Constraints:",
            "- Use common foods; include grams for each item.",
            "- Avoid alcohol.",
            "- Keep it simple and repeatable.",
            "- If user is imperial, you can still output grams (preferred).",
            *dietary_rules,
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
                config=GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=MealPlanResponse.model_json_schema(),
                    # Keep responses bounded to reduce latency/timeouts.
                    max_output_tokens=1400,
                ),
            )
            text = resp.text or ""
            json_text = _extract_json(text)
            try:
                data = json.loads(json_text)
            except json.JSONDecodeError as e:
                repaired = _repair_json(client, text)
                if repaired:
                    try:
                        data = json.loads(repaired)
                    except json.JSONDecodeError:
                        data = None
                else:
                    data = None

                if data is None:
                    preview = (text or "")[:600].replace("\n", "\\n")
                    raise RuntimeError(
                        f"LLM returned non-JSON: {e.msg} at line {e.lineno} col {e.colno}. "
                        f"Preview: {preview}"
                    ) from e
            try:
                return MealPlanResponse.model_validate(data)
            except Exception as e:
                preview = (text or "")[:600].replace("\n", "\\n")
                raise RuntimeError(
                    f"LLM returned JSON that doesn't match schema. Preview: {preview}"
                ) from e

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


def _repair_json(client: genai.Client, raw_text: str) -> str | None:
    prompt = "\n".join(
        [
            "Fix the JSON below so it is valid and matches the schema.",
            "Return JSON only. No markdown, no extra text.",
            "JSON to fix:",
            raw_text,
        ]
    )
    try:
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=MealPlanResponse.model_json_schema(),
                max_output_tokens=1000,
            ),
        )
    except Exception:
        return None

    text = resp.text or ""
    return _extract_json(text) or None
