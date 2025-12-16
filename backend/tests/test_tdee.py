import pytest

from app.formulas.tdee import calculate_tdee
from app.models import ActivityLevel


def test_tdee_known_value():
    tdee = calculate_tdee(bmr=1805.0, activity_level=ActivityLevel.moderate)
    assert tdee == pytest.approx(2797.75, abs=1e-9)


def test_tdee_rejects_non_positive_bmr():
    with pytest.raises(ValueError):
        calculate_tdee(bmr=0, activity_level=ActivityLevel.sedentary)
