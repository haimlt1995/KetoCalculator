import pytest

from app.formulas.bmi import calculate_bmi


def test_bmi_known_value():
    # BMI = 80 / 1.8^2 = 24.691358...
    bmi = calculate_bmi(weight_kg=80, height_cm=180)
    assert bmi == pytest.approx(24.6914, abs=1e-4)


def test_height_cm_is_converted_to_meters():
    bmi = calculate_bmi(weight_kg=50, height_cm=100)
    assert bmi == pytest.approx(50.0, abs=1e-9)


def test_bmi_rejects_zero_or_negative():
    with pytest.raises(ValueError):
        calculate_bmi(0, 180)
    with pytest.raises(ValueError):
        calculate_bmi(80, 0)
