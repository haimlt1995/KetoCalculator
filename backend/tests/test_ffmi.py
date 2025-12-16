import pytest

from app.formulas.ffmi import calculate_ffmi


def test_ffmi_none_when_bodyfat_none():
    assert calculate_ffmi(weight_kg=80, height_cm=180, body_fat_percent=None) is None


def test_ffmi_known_value():
    # Subject: 80kg, 180cm, BF ≈ 19.18%
    # Fat-free mass = 80 * (1 - 0.1918) ≈ 64.66 kg
    # Height^2 = 1.8^2 = 3.24
    # FFMI ≈ 64.66 / 3.24 ≈ 19.95
    ffmi = calculate_ffmi(weight_kg=80, height_cm=180, body_fat_percent=19.18)

    assert ffmi == pytest.approx(19.95, abs=0.05)


def test_ffmi_rejects_invalid_bodyfat():
    with pytest.raises(ValueError):
        calculate_ffmi(weight_kg=80, height_cm=180, body_fat_percent=120)
