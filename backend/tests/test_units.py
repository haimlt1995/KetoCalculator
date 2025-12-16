import pytest

from app.models import ActivityLevel, Sex, UnitSystem, UserInput
from app.units import normalize_inputs


def test_normalize_metric_ok():
    user = UserInput(
        unit_system=UnitSystem.metric,
        sex=Sex.male,
        age_years=25,
        height_cm=180,
        weight_kg=80,
        activity_level=ActivityLevel.moderate,
    )
    norm = normalize_inputs(user)
    assert norm.height_cm == 180
    assert norm.weight_kg == 80


def test_normalize_imperial_ok():
    # 180 cm ≈ 70.866 in, 80 kg ≈ 176.370 lb
    user = UserInput(
        unit_system=UnitSystem.imperial,
        sex=Sex.male,
        age_years=25,
        height_in=70.8661,
        weight_lb=176.3698,
        activity_level=ActivityLevel.moderate,
    )
    norm = normalize_inputs(user)
    assert norm.height_cm == pytest.approx(180.0, abs=1e-3)
    assert norm.weight_kg == pytest.approx(80.0, abs=1e-3)


def test_normalize_metric_missing_fields_raises():
    user = UserInput(
        unit_system=UnitSystem.metric,
        sex=Sex.male,
        age_years=25,
        activity_level=ActivityLevel.moderate,
    )
    with pytest.raises(ValueError):
        normalize_inputs(user)
