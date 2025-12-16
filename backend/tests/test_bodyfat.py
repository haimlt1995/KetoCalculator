import pytest

from app.formulas.bodyfat import estimate_body_fat_percent_from_bmi
from app.models import Sex


def test_bodyfat_returns_none_for_minors():
    assert estimate_body_fat_percent_from_bmi(bmi=22.0, age_years=17, sex=Sex.male) is None


def test_bodyfat_adult_known_value_male():
    # Example: BMI 30.367, age 30, male (sex_bit=1)
    # BF% = 1.2*30.367 + 0.23*30 - 10.8*1 - 5.4
    #     = 36.4404 + 6.9 - 10.8 - 5.4 = 27.1404
    bf = estimate_body_fat_percent_from_bmi(bmi=30.367, age_years=30, sex=Sex.male)
    assert bf == pytest.approx(27.1404, abs=1e-4)


def test_bodyfat_rejects_bad_bmi():
    with pytest.raises(ValueError):
        estimate_body_fat_percent_from_bmi(bmi=0, age_years=30, sex=Sex.female)
