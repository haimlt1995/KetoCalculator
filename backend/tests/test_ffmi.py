import pytest

from app.formulas.ffmi import calculate_ffmi


def test_ffmi_none_when_bodyfat_none():
    assert calculate_ffmi(weight_kg=93, height_cm=175, body_fat_percent=None) is None


def test_ffmi_known_value():
    # weight 93kg, height 1.75m, BF 27.1404%
    # FFM = 93*(1-0.271404)=67.759? kg
    # FFMI = FFM / 1.75^2 = FFM / 3.0625
    ffmi = calculate_ffmi(weight_kg=93, height_cm=175, body_fat_percent=27.1404)
    assert ffmi == pytest.approx(22.12, abs=0.05)  # allow small rounding wiggle


def test_ffmi_rejects_invalid_bodyfat():
    with pytest.raises(ValueError):
        calculate_ffmi(weight_kg=93, height_cm=175, body_fat_percent=120)
