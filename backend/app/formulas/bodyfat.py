from app.models import Sex


def estimate_body_fat_percent_from_bmi(*, bmi: float, age_years: int, sex: Sex) -> float | None:
    """
    Approximate body fat % estimate using BMI, age, and sex.

    IMPORTANT:
    - This is a rough estimate and not a medical measurement.
    - For minors (<18), returns None (we do not estimate in this milestone).

    Uses a commonly-cited BMI-based estimation model (adult-oriented).
    """
    if age_years < 18:
        return None
    if bmi <= 0:
        raise ValueError("bmi must be > 0")

    sex_bit = 1 if sex == Sex.male else 0
    # Adult rough estimate:
    # BF% = 1.20*BMI + 0.23*Age - 10.8*Sex - 5.4
    bf = 1.20 * bmi + 0.23 * age_years - 10.8 * sex_bit - 5.4

    # Clamp to realistic-ish bounds so we don't return nonsense for edge inputs
    return max(0.0, min(75.0, bf))
