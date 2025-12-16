import pytest

from app.formulas.bmi import calculate_bmi


def test_bmi_known_value():
    # 93kg, 175cm -> BMI ≈ 30.367
    bmi = calculate_bmi(weight_kg=93, height_cm=175)
    assert bmi == pytest.approx(30.367, abs=1e-3)


def test_height_cm_is_converted_to_meters():
    # 100cm = 1.0m => BMI should equal weight_kg
    bmi = calculate_bmi(weight_kg=50, height_cm=100)
    assert bmi == pytest.approx(50.0, abs=1e-9)


def test_bmi_rejects_zero_or_negative():
    with pytest.raises(ValueError):
        calculate_bmi(0, 175)
    with pytest.raises(ValueError):
        calculate_bmi(93, 0)
