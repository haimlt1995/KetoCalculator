from app.calc import calculate_all
from app.models import ActivityLevel, Goal, Sex, UnitSystem, UserInput


def test_calculate_all_happy_path_metric():
    user = UserInput(
        unit_system=UnitSystem.metric,
        sex=Sex.male,
        age_years=25,
        height_cm=180,
        weight_kg=80,
        activity_level=ActivityLevel.moderate,
        goal=Goal.maintain,
    )
    out = calculate_all(user, forecast_weeks=4)

    assert out.bmi > 0
    assert out.bmr > 0
    assert out.tdee > 0
    assert out.macros.calories_total > 0
    assert len(out.forecast) == 5  # week 0..4
