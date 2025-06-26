from edc_constants.constants import FEMALE, MALE
from edc_reportable import (
    GRAMS_PER_DECILITER,
    IU_LITER,
    MICROMOLES_PER_LITER,
    MILLIGRAMS_PER_DECILITER,
    MILLIMOLES_PER_LITER,
    TEN_X_9_PER_LITER,
    Formula,
)

collection_name = "egfr_app"
age_opts = dict(age_lower=18, age_upper=None, age_units="years", age_lower_inclusive=True)
reportable_grades = [3, 4]
reportable_grades_exceptions = {}

normal_data = {
    "haemoglobin": [
        Formula("13.5<=x<=17.5", units=GRAMS_PER_DECILITER, gender=[MALE], **age_opts),
        Formula("12.0<=x<=15.5", units=GRAMS_PER_DECILITER, gender=[FEMALE], **age_opts),
    ],
    "platelets": [
        Formula("150<=x<=450", units=TEN_X_9_PER_LITER, gender=[MALE, FEMALE], **age_opts)
    ],
    "neutrophil": [
        Formula("2.5<=x<=7.5", units=TEN_X_9_PER_LITER, gender=[MALE, FEMALE], **age_opts)
    ],
    "sodium": [
        Formula("135<=x<=145", units=MILLIMOLES_PER_LITER, gender=[MALE, FEMALE], **age_opts)
    ],
    "potassium": [
        Formula("3.6<=x<=5.2", units=MILLIMOLES_PER_LITER, gender=[MALE, FEMALE], **age_opts)
    ],
    "magnesium": [
        Formula("0.75<=x<=1.2", units=MILLIMOLES_PER_LITER, gender=[MALE, FEMALE], **age_opts)
    ],
    "alt": [Formula("10<=x<=40", units=IU_LITER, gender=[MALE, FEMALE], **age_opts)],
    "creatinine": [
        Formula(
            "0.6<=x<=1.3", units=MILLIGRAMS_PER_DECILITER, gender=[MALE, FEMALE], **age_opts
        ),
        Formula("53<=x<=115", units=MICROMOLES_PER_LITER, gender=[MALE, FEMALE], **age_opts),
    ],
}

grading_data = {
    "haemoglobin": [
        Formula("7.0<=x<9.0", grade=3, units=GRAMS_PER_DECILITER, gender=[MALE], **age_opts),
        Formula("6.5<=x<8.5", grade=3, units=GRAMS_PER_DECILITER, gender=[FEMALE], **age_opts),
        Formula("x<7.0", grade=4, units=GRAMS_PER_DECILITER, gender=[MALE], **age_opts),
        Formula("x<6.5", grade=4, units=GRAMS_PER_DECILITER, gender=[FEMALE], **age_opts),
    ],
    "platelets": [
        Formula(
            "25<=x<=50",
            grade=3,
            units=TEN_X_9_PER_LITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
        Formula("x<25", grade=4, units=TEN_X_9_PER_LITER, gender=[MALE, FEMALE], **age_opts),
    ],
    "neutrophil": [
        Formula(
            "0.4<=x<=0.59",
            grade=3,
            units=TEN_X_9_PER_LITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
        Formula("x<0.4", grade=4, units=TEN_X_9_PER_LITER, gender=[MALE, FEMALE], **age_opts),
    ],
    "sodium": [
        Formula(
            "121<=x<=124",
            grade=3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
        Formula(
            "154<=x<=159",
            grade=3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
        Formula(
            "160<=x",
            grade=4,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
        Formula(
            "x<=120",
            grade=4,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
    ],
    "potassium": [
        Formula(
            "2.0<=x<=2.4",
            grade=3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
        Formula(
            "6.5<=x<=7.0",
            grade=3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
        Formula(
            "x<2.0",
            grade=4,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
        Formula(
            "7.0<x",
            grade=4,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
    ],
    "magnesium": [
        Formula(
            "0.3<=x<=0.44",
            grade=3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
        Formula(
            "x<0.3",
            grade=4,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
    ],
    "alt": [
        Formula("200<=x<=400", grade=3, units=IU_LITER, gender=[MALE, FEMALE], **age_opts),
        Formula("400<x", grade=4, units=IU_LITER, gender=[MALE, FEMALE], **age_opts),
    ],
    "creatinine": [
        Formula(
            "2.47<=x<=4.42",
            grade=3,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
        Formula(
            "216<=x<=400",
            grade=3,
            units=MICROMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
        Formula(
            "4.55<x",
            grade=4,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
        Formula(
            "400<x",
            grade=4,
            units=MICROMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
    ],
}

reference_range_options = dict(
    collection_name=collection_name,
    normal_data=normal_data,
    grading_data=grading_data,
    reportable_grades=reportable_grades,
    reportable_grades_exceptions=reportable_grades_exceptions,
)
