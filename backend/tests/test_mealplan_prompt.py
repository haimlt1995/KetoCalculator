from app.calc import calculate_all
from app.models import ActivityLevel, Goal, Sex, UnitSystem, UserInput
from app.services.llm_mealplan import build_prompt


def test_build_prompt_contains_targets():
    user = UserInput(
        unit_system=UnitSystem.metric,
        sex=Sex.male,
        age_years=25,
        height_cm=180,
        weight_kg=80,
        activity_level=ActivityLevel.moderate,
        goal=Goal.maintain,
    )
    calc = calculate_all(user)

    prompt = build_prompt(user, calc)
    assert "Net carbs target" in prompt
    assert "Output MUST be valid JSON" in prompt
