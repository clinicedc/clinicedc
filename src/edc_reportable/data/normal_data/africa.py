from edc_constants.constants import FEMALE, MALE

from ...adult_age_options import adult_age_options
from ...formula import Formula
from ...units import (
    CELLS_PER_MILLIMETER_CUBED,
    EGFR_UNITS,
    FEMTOLITERS_PER_CELL,
    GRAMS_PER_DECILITER,
    GRAMS_PER_LITER,
    IU_LITER,
    MICROMOLES_PER_LITER,
    MILLIGRAMS_PER_DECILITER,
    MILLIGRAMS_PER_LITER,
    MILLIMOLES_PER_LITER,
    PERCENT,
    PICOGRAMS_PER_CELL,
    PLUS,
    TEN_X_9_PER_LITER,
)

__all__ = ["normal_data"]

normal_data = {
    "albumin": [
        Formula(
            "3.5<=x<=5.0",
            units=GRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "35<=x<=50",
            units=GRAMS_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "alp": [Formula("40<=x<=150", units=IU_LITER, gender=[MALE, FEMALE], **adult_age_options)],
    "alt": [
        Formula("0<=x<=40", units=IU_LITER, gender=[MALE], **adult_age_options),
        Formula("0<=x<=35", units=IU_LITER, gender=[FEMALE], **adult_age_options),
    ],
    "amylase": [
        Formula("25<=x<=125", units=IU_LITER, gender=[MALE, FEMALE], **adult_age_options)
    ],
    "ast": [Formula("5<=x<=34", units=IU_LITER, gender=[MALE, FEMALE], **adult_age_options)],
    "egfr": [
        Formula(
            "0.0<=x<45.0",
            units=EGFR_UNITS,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
    "egfr_drop": [
        Formula(
            "x<40.0",
            units=PERCENT,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
    "chol": [
        Formula(
            "0.5<=x<=6.2",
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
    "creatinine": [
        Formula(
            "63.6<=x<=110.5",
            units=MICROMOLES_PER_LITER,
            gender=[MALE],
            **adult_age_options,
        ),
        Formula(
            "50.4<=x<=98.1",
            units=MICROMOLES_PER_LITER,
            gender=[FEMALE],
            **adult_age_options,
        ),
        Formula(
            "0.6<=x<=1.3",
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "crp": [
        Formula(
            "0.0<=x<=0.5",
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "0.0<=x<=5.0",
            units=MILLIGRAMS_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "hdl": [
        Formula(
            "1.04<=x<=1.55",
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "ggt": [
        Formula("12<=x<=64", units=IU_LITER, gender=[MALE], **adult_age_options),
        Formula("9<=x<=36", units=IU_LITER, gender=[FEMALE], **adult_age_options),
    ],
    "haemoglobin": [
        Formula(
            "13.0<=x<=17.0",
            units=GRAMS_PER_DECILITER,
            gender=[MALE],
            **adult_age_options,
        ),
        Formula(
            "12.0<=x<=15.0",
            units=GRAMS_PER_DECILITER,
            gender=[FEMALE],
            **adult_age_options,
        ),
    ],
    "hba1c": [
        Formula("4.4<=x<6.5", units=PERCENT, gender=[MALE, FEMALE], **adult_age_options)
    ],
    # hematocrit
    "hct": [
        Formula("37.0<=x<=54.0", units=PERCENT, gender=[MALE, FEMALE], **adult_age_options)
    ],
    "ldl": [
        Formula(
            "0.00<=x<=3.34",
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "magnesium": [
        Formula(
            "0.75<=x<=1.2",
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "1.8<=x<=2.9",
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "mch": [
        Formula(
            "27.6<=x<=33.4",
            units=PICOGRAMS_PER_CELL,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "mchc": [
        Formula(
            "32.8<=x<35.4",
            units=GRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "mcv": [
        Formula(
            "81.6<=x<=99.8",
            units=FEMTOLITERS_PER_CELL,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "neutrophil": [
        Formula(
            "2.5<=x<=7.5",
            units=TEN_X_9_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
    "platelets": [
        Formula(
            "150<=x<=450",
            units=TEN_X_9_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "150000<=x<=450000",
            units=CELLS_PER_MILLIMETER_CUBED,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "potassium": [
        Formula(
            "3.6<=x<=5.2",
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
    "proteinuria": [
        Formula(
            "0.0<=x<1.0",
            units=PLUS,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "sodium": [
        Formula(
            "136<=x<=145",
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
    "trig": [
        Formula(
            "0.00<=x<=1.69",
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    # BUN
    "urea": [
        Formula(
            "2.5<=x<=6.5",
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
    "uric_acid": [
        Formula(
            "0.15<=x<=0.35",
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "7.2<=x",
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "rbc": [
        Formula(
            "3.5<=x<=5.5",
            units=TEN_X_9_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "3500<=x<=5500",
            units=CELLS_PER_MILLIMETER_CUBED,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "tbil": [
        Formula(
            "0.2923<=x<1.2278",
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "0.00292<=x<0.0123",
            units=GRAMS_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "5.0<=x<21.0",
            units=MICROMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "wbc": [
        Formula(
            "2.49<x",
            units=TEN_X_9_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
}
