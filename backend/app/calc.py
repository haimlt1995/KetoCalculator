from app.formulas.bmi import calculate_bmi
from app.formulas.bmr import calculate_bmr_mifflin_st_jeor
from app.formulas.bodyfat import estimate_body_fat_percent_from_bmi
from app.formulas.ffmi import calculate_ffmi
from app.formulas.forecast import forecast_weight_kg
from app.formulas.macros import calculate_keto_macros
from app.formulas.tdee import calculate_tdee
from app.models import CalcOutput, ForecastPoint, UserInput
from app.units import normalize_inputs


def calculate_all(user: UserInput, *, forecast_weeks: int = 24) -> CalcOutput:
    norm = normalize_inputs(user)

    bmi = calculate_bmi(weight_kg=norm.weight_kg, height_cm=norm.height_cm)

    bmr = calculate_bmr_mifflin_st_jeor(
        sex=user.sex,
        age_years=norm.age_years,
        height_cm=norm.height_cm,
        weight_kg=norm.weight_kg,
    )

    tdee = calculate_tdee(bmr=bmr, activity_level=user.activity_level)

    bf = estimate_body_fat_percent_from_bmi(bmi=bmi, age_years=norm.age_years, sex=user.sex)
    ffmi = calculate_ffmi(weight_kg=norm.weight_kg, height_cm=norm.height_cm, body_fat_percent=bf)

    # For now calories_target = tdee (we'll add lose/gain surplus/deficit next milestone)
    calories_target = tdee

    cal, protein_g, fat_g, net_carbs_g = calculate_keto_macros(
        calories_total=calories_target,
        weight_kg=norm.weight_kg,
        goal=user.goal,
    )

    forecast_pts = forecast_weight_kg(
        start_weight_kg=norm.weight_kg,
        tdee=tdee,
        calories_target=calories_target,
        weeks=forecast_weeks,
    )
    forecast = [ForecastPoint(week=w, weight_kg=kg) for (w, kg) in forecast_pts]

    return CalcOutput(
        bmi=bmi,
        bmr=bmr,
        tdee=tdee,
        body_fat_percent_estimate=bf,
        ffmi=ffmi,
        macros={
            "calories_total": cal,
            "protein_g": protein_g,
            "fat_g": fat_g,
            "net_carbs_g": net_carbs_g,
        },
        forecast=forecast,
    )
