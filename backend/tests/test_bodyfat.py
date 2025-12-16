import pytest

from app.formulas.bodyfat import estimate_body_fat_percent_from_bmi
from app.models import Sex


def test_bodyfat_returns_none_for_minors():
    assert estimate_body_fat_percent_from_bmi(bmi=22.0, age_years=17, sex=Sex.male) is None


def test_bodyfat_adult_known_value_male():
    # Subject: male, 25y, 80kg, 180cm
    # BMI = 80 / (1.8^2) = 24.691358
    bmi = 80 / (1.8 * 1.8)

    # BF% = 1.2*BMI + 0.23*Age - 10.8*Sex - 5.4
    # Sex bit = 1 (male)
    # BF% = 1.2*24.691358 + 0.23*25 - 10.8 - 5.4
    #     ≈ 29.6296 + 5.75 - 10.8 - 5.4 = 19.1796
    bf = estimate_body_fat_percent_from_bmi(bmi=bmi, age_years=25, sex=Sex.male)

    assert bf == pytest.approx(19.18, abs=0.02)


def test_bodyfat_rejects_bad_bmi():
    with pytest.raises(ValueError):
        estimate_body_fat_percent_from_bmi(bmi=0, age_years=25, sex=Sex.male)
