def calculate_ffmi(
    *, weight_kg: float, height_cm: float, body_fat_percent: float | None
) -> float | None:
    """
    FFMI (Fat-Free Mass Index)

    fat_free_mass_kg = weight_kg * (1 - bf%/100)
    FFMI = fat_free_mass_kg / (height_m^2)

    If body_fat_percent is None, returns None.
    """
    if body_fat_percent is None:
        return None
    if not (0.0 <= body_fat_percent <= 100.0):
        raise ValueError("body_fat_percent must be between 0 and 100")
    if weight_kg <= 0:
        raise ValueError("weight_kg must be > 0")
    if height_cm <= 0:
        raise ValueError("height_cm must be > 0")

    height_m = height_cm / 100.0
    fat_free_mass_kg = weight_kg * (1.0 - body_fat_percent / 100.0)
    return fat_free_mass_kg / (height_m * height_m)
