from edc_constants.constants import FEMALE, MALE
from edc_reportable import (
    GRADE3,
    GRADE4,
    GRAMS_PER_DECILITER,
    IU_LITER,
    MICROMOLES_PER_LITER,
    MILLIGRAMS_PER_DECILITER,
    MILLIMOLES_PER_LITER,
    TEN_X_9_PER_LITER,
)
from edc_reportable import parse as p

age_opts = dict(age_lower=18, age_upper=None, age_units="years", age_lower_inclusive=True)

normal_data = {
    "haemoglobin": [
        p("13.5<=x<=17.5", units=GRAMS_PER_DECILITER, gender=[MALE], **age_opts),
        p("12.0<=x<=15.5", units=GRAMS_PER_DECILITER, gender=[FEMALE], **age_opts),
    ],
    "platelets": [
        p("150<=x<=450", units=TEN_X_9_PER_LITER, gender=[MALE, FEMALE], **age_opts)
    ],
    "neutrophil": [
        p("2.5<=x<=7.5", units=TEN_X_9_PER_LITER, gender=[MALE, FEMALE], **age_opts)
    ],
    "sodium": [
        p("135<=x<=145", units=MILLIMOLES_PER_LITER, gender=[MALE, FEMALE], **age_opts)
    ],
    "potassium": [
        p("3.6<=x<=5.2", units=MILLIMOLES_PER_LITER, gender=[MALE, FEMALE], **age_opts)
    ],
    "magnesium": [
        p("0.75<=x<=1.2", units=MILLIMOLES_PER_LITER, gender=[MALE, FEMALE], **age_opts)
    ],
    "alt": [p("10<=x<=40", units=IU_LITER, gender=[MALE, FEMALE], **age_opts)],
    "creatinine": [
        p("0.6<=x<=1.3", units=MILLIGRAMS_PER_DECILITER, gender=[MALE, FEMALE], **age_opts),
        p("53<=x<=115", units=MICROMOLES_PER_LITER, gender=[MALE, FEMALE], **age_opts),
    ],
}

grading_data = {
    "haemoglobin": [
        p("7.0<=x<9.0", grade=GRADE3, units=GRAMS_PER_DECILITER, gender=[MALE], **age_opts),
        p("6.5<=x<8.5", grade=GRADE3, units=GRAMS_PER_DECILITER, gender=[FEMALE], **age_opts),
        p("x<7.0", grade=GRADE4, units=GRAMS_PER_DECILITER, gender=[MALE], **age_opts),
        p("x<6.5", grade=GRADE4, units=GRAMS_PER_DECILITER, gender=[FEMALE], **age_opts),
    ],
    "platelets": [
        p(
            "25<=x<=50",
            grade=GRADE3,
            units=TEN_X_9_PER_LITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
        p("x<25", grade=GRADE4, units=TEN_X_9_PER_LITER, gender=[MALE, FEMALE], **age_opts),
    ],
    "neutrophil": [
        p(
            "0.4<=x<=0.59",
            grade=GRADE3,
            units=TEN_X_9_PER_LITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
        p("x<0.4", grade=GRADE4, units=TEN_X_9_PER_LITER, gender=[MALE, FEMALE], **age_opts),
    ],
    "sodium": [
        p(
            "121<=x<=124",
            grade=GRADE3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
        p(
            "154<=x<=159",
            grade=GRADE3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
        p(
            "160<=x",
            grade=GRADE4,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
        p(
            "x<=120",
            grade=GRADE4,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
    ],
    "potassium": [
        p(
            "2.0<=x<=2.4",
            grade=GRADE3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
        p(
            "6.5<=x<=7.0",
            grade=GRADE3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
        p(
            "x<2.0",
            grade=GRADE4,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
        p(
            "7.0<x",
            grade=GRADE4,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
    ],
    "magnesium": [
        p(
            "0.3<=x<=0.44",
            grade=GRADE3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
        p(
            "x<0.3",
            grade=GRADE4,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
    ],
    "alt": [
        p("200<=x<=400", grade=GRADE3, units=IU_LITER, gender=[MALE, FEMALE], **age_opts),
        p("400<x", grade=GRADE4, units=IU_LITER, gender=[MALE, FEMALE], **age_opts),
    ],
    "creatinine": [
        p(
            "2.47<=x<=4.42",
            grade=GRADE3,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
        p(
            "216<=x<=400",
            grade=GRADE3,
            units=MICROMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
        p(
            "4.55<x",
            grade=GRADE4,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
        p(
            "400<x",
            grade=GRADE4,
            units=MICROMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **age_opts,
        ),
    ],
}
