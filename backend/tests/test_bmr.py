import pytest

from app.formulas.bmr import calculate_bmr_mifflin_st_jeor
from app.models import Sex


def test_bmr_male_known_value():
    bmr = calculate_bmr_mifflin_st_jeor(sex=Sex.male, age_years=25, height_cm=180, weight_kg=80)
    assert bmr == pytest.approx(1805.0, abs=1e-9)


def test_bmr_female_known_value():
    bmr = calculate_bmr_mifflin_st_jeor(sex=Sex.female, age_years=25, height_cm=180, weight_kg=80)
    assert bmr == pytest.approx(1639.0, abs=1e-9)


def test_bmr_rejects_minors_for_now():
    with pytest.raises(ValueError):
        calculate_bmr_mifflin_st_jeor(sex=Sex.male, age_years=17, height_cm=180, weight_kg=80)


def test_bmr_rejects_bad_inputs():
    with pytest.raises(ValueError):
        calculate_bmr_mifflin_st_jeor(sex=Sex.male, age_years=25, height_cm=0, weight_kg=80)
    with pytest.raises(ValueError):
        calculate_bmr_mifflin_st_jeor(sex=Sex.male, age_years=25, height_cm=180, weight_kg=0)
