def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """
    Body Mass Index (BMI)

    Formula:
        BMI = weight_kg / (height_m ** 2)

    Assumes metric inputs.
    """
    if weight_kg <= 0:
        raise ValueError("weight_kg must be > 0")
    if height_cm <= 0:
        raise ValueError("height_cm must be > 0")

    height_m = height_cm / 100.0
    return weight_kg / (height_m * height_m)
