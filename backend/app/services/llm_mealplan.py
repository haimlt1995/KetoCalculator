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
        base = ['"breakfast"', '"lunch"', '"dinner"', '"snack"', '"snack2"', '"snack3"']
        lines.append("  - " + ", ".join(base[: mp.meals_per_day]))

    return lines


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
            "- Do not include raw newlines inside string values; use \\n if needed.",
            "- Ensure all strings are double-quoted and properly escaped.",
            "- Use common foods; include grams for each item.",
            "- Avoid alcohol.",
            "- Keep it simple and repeatable.",
            "- If user is imperial, you can still output grams (preferred).",
            *dietary_rules,
            "- Return JSON only. No markdown, no extra text.",
        ]
    )


def _estimate_max_output_tokens(user: UserInput) -> int:
    mp = user.mealplan
    base = 500
    per_meal = 220
    est = base + (mp.days * mp.meals_per_day * per_meal)
    return max(1200, min(est, 4000))


def _expected_meal_names(user: UserInput) -> list[str]:
    if user.mealplan.meals_per_day == 1:
        return ["meal"]
    base = ["breakfast", "lunch", "dinner", "snack", "snack2", "snack3"]
    return base[: user.mealplan.meals_per_day]


def _empty_meal(name: str) -> dict:
    return {
        "meal_name": name,
        "items": [],
        "protein_g": 0,
        "fat_g": 0,
        "net_carbs_g": 0,
        "calories": 0,
    }


def _meal_to_dict(meal: object, name: str) -> dict:
    data = meal.model_dump() if hasattr(meal, "model_dump") else dict(meal)
    data["meal_name"] = name
    return data


def _normalize_day_meals(meals: list, expected_names: list[str]) -> list[dict]:
    normalized: list[dict] = []
    used_idx: set[int] = set()
    by_name_idx: dict[str, int] = {getattr(m, "meal_name", None): i for i, m in enumerate(meals)}
    for name in expected_names:
        idx = by_name_idx.get(name)
        if idx is not None and idx not in used_idx:
            used_idx.add(idx)
            normalized.append(_meal_to_dict(meals[idx], name))
            continue
        fallback_idx = next((i for i in range(len(meals)) if i not in used_idx), None)
        if fallback_idx is not None:
            used_idx.add(fallback_idx)
            normalized.append(_meal_to_dict(meals[fallback_idx], name))
        else:
            normalized.append(_empty_meal(name))
    return normalized


def _normalize_mealplan(plan: MealPlanResponse, user: UserInput) -> MealPlanResponse:
    expected_days = user.mealplan.days
    expected_names = _expected_meal_names(user)
    source_days = plan.days or []
    normalized_days: list[dict] = []

    for i in range(expected_days):
        src = source_days[i % len(source_days)] if source_days else None
        src_meals = src.meals if src else []
        meals = _normalize_day_meals(src_meals, expected_names)
        totals = (
            src.totals.model_dump()
            if src and getattr(src, "totals", None) is not None
            else _empty_meal("totals")
        )
        normalized_days.append({"day": i + 1, "meals": meals, "totals": totals})

    payload = {
        "days": normalized_days,
        "shopping_list": plan.shopping_list or [],
        "assumptions": plan.assumptions or [],
    }
    return MealPlanResponse.model_validate(payload)


def _validate_mealplan_shape(plan: MealPlanResponse, user: UserInput) -> tuple[bool, str]:
    expected_days = user.mealplan.days
    expected_meals = user.mealplan.meals_per_day
    errors: list[str] = []

    if len(plan.days) != expected_days:
        errors.append(f"days={len(plan.days)} expected={expected_days}")

    allowed_names = set(_expected_meal_names(user))
    for day in plan.days:
        if len(day.meals) != expected_meals:
            errors.append(f"day {day.day} meals={len(day.meals)} expected={expected_meals}")
        for meal in day.meals:
            if meal.meal_name not in allowed_names:
                errors.append(
                    f"day {day.day} meal_name='{meal.meal_name}' not in {sorted(allowed_names)}"
                )

    if errors:
        return False, "; ".join(errors)
    return True, ""


def generate_meal_plan(user: UserInput, calc: CalcOutput) -> MealPlanResponse:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set")

    client = genai.Client()
    prompt = build_prompt(user, calc)
    max_output_tokens = _estimate_max_output_tokens(user)

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
                    max_output_tokens=max_output_tokens,
                ),
            )
            parsed = _get_parsed_response(resp)
            data = None
            if parsed is not None:
                data = parsed
            text = resp.text or ""
            if data is None:
                json_text = _extract_json(text)
                try:
                    data = json.loads(json_text)
                except json.JSONDecodeError as e:
                    sanitized = _sanitize_json_text(json_text)
                    if sanitized != json_text:
                        try:
                            data = json.loads(sanitized)
                        except json.JSONDecodeError:
                            data = None
                    else:
                        data = None

                    if data is None:
                        repaired = _repair_json(client, text, max_output_tokens=max_output_tokens)
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
                plan = MealPlanResponse.model_validate(data)
            except Exception as e:
                preview = (text or "")[:600].replace("\n", "\\n")
                raise RuntimeError(
                    f"LLM returned JSON that doesn't match schema. Preview: {preview}"
                ) from e

            ok, reason = _validate_mealplan_shape(plan, user)
            if ok:
                return plan

            normalized = _normalize_mealplan(plan, user)
            ok, _ = _validate_mealplan_shape(normalized, user)
            if ok:
                return normalized

            repaired = _repair_json_with_constraints(
                client,
                json.dumps(plan.model_dump()),
                user,
                max_output_tokens=max_output_tokens,
                reason=reason,
            )
            if repaired:
                try:
                    repaired_data = json.loads(repaired)
                    repaired_plan = MealPlanResponse.model_validate(repaired_data)
                except Exception:
                    repaired_plan = None
                if repaired_plan:
                    ok, _ = _validate_mealplan_shape(repaired_plan, user)
                    if ok:
                        return repaired_plan

            raise RuntimeError(
                "LLM returned a meal plan that does not match the requested days/meals."
            )

        except errors.ServerError as e:
            last_err = e
            if i == attempts - 1:
                break

            sleep_s = base_sleep * (2**i) + random.uniform(0, 0.5)
            time.sleep(sleep_s)

        except errors.APIError as e:
            if getattr(e, "status_code", None) == 429:
                raise RuntimeError(f"RATE_LIMIT:{e}") from e
            raise RuntimeError(f"Gemini API error: {e}") from e

    raise RuntimeError(
        "Gemini is temporarily unavailable (model overloaded). Please try again in a minute."
    ) from last_err


def _extract_json(text: str) -> str:
    t = text.strip()

    if t.startswith("```"):
        t = t.strip("`").strip()
        if t.lower().startswith("json"):
            t = t[4:].strip()

    start = t.find("{")
    end = t.rfind("}")
    if start != -1 and end != -1 and end > start:
        return t[start : end + 1]

    return t


def _repair_json_with_constraints(
    client: genai.Client,
    raw_text: str,
    user: UserInput,
    max_output_tokens: int,
    reason: str,
) -> str | None:
    meal_names = _expected_meal_names(user)
    prompt = "\n".join(
        [
            "Fix the JSON below so it is valid and matches the schema.",
            "Return JSON only. No markdown, no extra text.",
            f"- Number of days: {user.mealplan.days}. Output exactly this many day entries.",
            f"- Meals per day: {user.mealplan.meals_per_day}.",
            f"- Use meal_name values: {', '.join(meal_names)}.",
            f"- Each day MUST contain exactly {user.mealplan.meals_per_day} meals.",
            "- Ensure a totals object exists for each day.",
            f"- Repair reason: {reason}",
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
                max_output_tokens=max(1200, max_output_tokens),
            ),
        )
    except Exception:
        return None

    text = resp.text or ""
    return _extract_json(text) or None


def _get_parsed_response(resp: object) -> object | None:
    parsed = getattr(resp, "parsed", None)
    if parsed is not None:
        return parsed

    try:
        candidates = getattr(resp, "candidates", None) or []
        if candidates:
            content = getattr(candidates[0], "content", None)
            parts = getattr(content, "parts", None) or []
            for part in parts:
                part_parsed = getattr(part, "parsed", None)
                if part_parsed is not None:
                    return part_parsed
    except Exception:
        return None

    return None


def _sanitize_json_text(text: str) -> str:
    out: list[str] = []
    in_string = False
    escape = False
    for ch in text:
        if in_string:
            if escape:
                escape = False
                out.append(ch)
                continue
            if ch == "\\":
                escape = True
                out.append(ch)
                continue
            if ch == '"':
                in_string = False
                out.append(ch)
                continue
            if ch == "\n":
                out.append("\\n")
                continue
            if ch == "\r":
                out.append("\\r")
                continue
        else:
            if ch == '"':
                in_string = True
                out.append(ch)
                continue
        out.append(ch)
    return "".join(out)


def _repair_json(client: genai.Client, raw_text: str, max_output_tokens: int) -> str | None:
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
                max_output_tokens=max(1200, max_output_tokens),
            ),
        )
    except Exception:
        return None

    text = resp.text or ""
    return _extract_json(text) or None
