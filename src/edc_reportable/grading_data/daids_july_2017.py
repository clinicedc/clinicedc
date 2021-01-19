"""
Based on Corrected Version 2.1 July 2017
"""

from edc_constants.constants import FEMALE, MALE
from edc_reportable import (
    parse as p,
    GRADE0,
    GRADE3,
    GRADE4,
    GRAMS_PER_DECILITER,
    GRAMS_PER_LITER,
    IU_LITER,
    MICROMOLES_PER_LITER,
    MILLIGRAMS_PER_DECILITER,
    MILLIMOLES_PER_LITER,
    PERCENT,
    TEN_X_9_PER_LITER,
    CELLS_PER_MILLIMETER_CUBED,
)

from ..adult_age_options import adult_age_options

dummies = {
    "hba1c": [
        p(
            "x<0",
            grade=GRADE0,
            units=PERCENT,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
    "hct": [
        p(
            "x<0",
            grade=GRADE0,
            units=PERCENT,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
    "hdl": [
        p(
            "x<0",
            grade=GRADE0,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
    "ggt": [
        p(
            "x<0",
            grade=GRADE0,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
    "rbc": [
        p(
            "x<0",
            grade=GRADE0,
            units=TEN_X_9_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "x<0",
            grade=GRADE0,
            units=CELLS_PER_MILLIMETER_CUBED,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "urea": [
        p(
            "x<0",
            grade=GRADE0,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
}


chemistries = {
    "albumin": [
        p(
            "x<2.0",
            grade=GRADE3,
            units=GRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "x<20",
            grade=GRADE3,
            units=GRAMS_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "alp": [
        p(
            "200<=x<=400",
            grade=GRADE3,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "400<x",
            grade=GRADE4,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "alt": [
        p(
            "200<=x<=400",
            grade=GRADE3,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "400<x",
            grade=GRADE4,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    # TODO: confirm amylase grading in IU_LITER
    "amylase": [
        p(
            "200<=x<=400",
            grade=GRADE3,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "400<x",
            grade=GRADE4,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "ast": [
        p(
            "200<=x<=400",
            grade=GRADE3,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "400<x",
            grade=GRADE4,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "creatinine": [
        p(
            "2.47<=x<=4.42",
            grade=GRADE3,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "216<=x<=400",
            grade=GRADE3,
            units=MICROMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "4.42<x",
            grade=GRADE4,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "400<x",
            grade=GRADE4,
            units=MICROMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "glucose": [  # G3/G4 same for fasting / non-fasting
        p(
            "13.89<=x<27.75",
            grade=GRADE3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
            fasting=True,
        ),
        p(
            "27.75<=x",
            grade=GRADE4,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
            fasting=True,
        ),
        p(
            "13.89<=x<27.75",
            grade=GRADE3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
            fasting=False,
        ),
        p(
            "27.75<=x",
            grade=GRADE4,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
            fasting=False,
        ),
    ],
    "ldl": [
        p(
            "4.90<=x",
            grade=GRADE3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
            fasting=True,
        ),
    ],
    "magnesium": [
        p(
            "0.3<=x<=0.44",
            grade=GRADE3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "x<0.3",
            grade=GRADE4,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "0.7<=x<=1.1",
            grade=GRADE3,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "x<0.7",
            grade=GRADE4,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "potassium": [
        p(
            "2.0<=x<=2.4",
            grade=GRADE3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "6.5<=x<7.0",
            grade=GRADE3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "x<2.0",
            grade=GRADE4,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "7.0<=x",
            grade=GRADE4,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "sodium": [
        p(
            "121<=x<=124",
            grade=GRADE3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "154<=x<=159",
            grade=GRADE3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "160<=x",
            grade=GRADE4,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "x<=120",
            grade=GRADE4,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "trig": [
        p(
            "5.7<=x<=11.4",
            grade=GRADE3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
            fasting=True,
        ),
        p(
            "11.4<x",
            grade=GRADE3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
            fasting=True,
        ),
    ],
    "uric_acid": [
        p(
            "12<=x<15.0",
            grade=GRADE3,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "15.0<=x",
            grade=GRADE4,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "0.71<=x<0.89",
            grade=GRADE3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "0.89<=x",
            grade=GRADE4,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
}

hematology = {
    "haemoglobin": [
        p(
            "7.0<=x<9.0",
            grade=GRADE3,
            units=GRAMS_PER_DECILITER,
            gender=[MALE],
            **adult_age_options,
        ),
        p(
            "6.5<=x<8.5",
            grade=GRADE3,
            units=GRAMS_PER_DECILITER,
            gender=[FEMALE],
            **adult_age_options,
        ),
        p(
            "x<7.0",
            grade=GRADE4,
            units=GRAMS_PER_DECILITER,
            gender=[MALE],
            **adult_age_options,
        ),
        p(
            "x<6.5",
            grade=GRADE4,
            units=GRAMS_PER_DECILITER,
            gender=[FEMALE],
            **adult_age_options,
        ),
    ],
    "platelets": [
        p(
            "25<=x<=50",
            grade=GRADE3,
            units=TEN_X_9_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "x<25",
            grade=GRADE4,
            units=TEN_X_9_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "25000<=x<=50000",
            grade=GRADE3,
            units=CELLS_PER_MILLIMETER_CUBED,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "x<25000",
            grade=GRADE4,
            units=CELLS_PER_MILLIMETER_CUBED,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "neutrophil": [
        p(
            "0.4<=x<=0.59",
            grade=GRADE3,
            units=TEN_X_9_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "x<0.4",
            grade=GRADE4,
            units=TEN_X_9_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "wbc": [
        p(
            "1.00<=x<=1.49",
            grade=GRADE3,
            units=TEN_X_9_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "x<1.00",
            grade=GRADE4,
            units=TEN_X_9_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
}


hba1c = {
    "hba1c": [
        p(
            "9999999<=x<=99999999",
            grade=GRADE3,
            units=PERCENT,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ]
}
