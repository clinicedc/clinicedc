from edc_constants.constants import FEMALE, MALE

from edc_reportable import (
    GRAMS_PER_DECILITER,
    IU_LITER,
    MICROMOLES_PER_LITER,
    MILLIGRAMS_PER_DECILITER,
    MILLIMOLES_PER_LITER,
    TEN_X_9_PER_LITER,
    adult_age_options,
)
from edc_reportable import parse as p
from edc_reportable.units import (
    CELLS_PER_MILLIMETER_CUBED,
    EGFR_UNITS,
    GRAMS_PER_LITER,
    PERCENT,
    PLUS,
)

normal_data = {
    "albumin": [
        p(
            "3.5<=x<=5.0",
            units=GRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "35<=x<=50",
            units=GRAMS_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "alp": [p("40<=x<=150", units=IU_LITER, gender=[MALE, FEMALE], **adult_age_options)],
    "alt": [p("0<=x<=55", units=IU_LITER, gender=[MALE, FEMALE], **adult_age_options)],
    "amylase": [p("25<=x<=125", units=IU_LITER, gender=[MALE, FEMALE], **adult_age_options)],
    "ast": [p("5<=x<=34", units=IU_LITER, gender=[MALE, FEMALE], **adult_age_options)],
    "egfr": [
        p(
            "0.0<=x<45.0",
            units=EGFR_UNITS,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
    "egfr_drop": [
        p(
            "x<40.0",
            units=PERCENT,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
    "chol": [
        p(
            "0.5<=x<=6.2",
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
    "creatinine": [
        p(
            "63.6<=x<=110.5",
            units=MICROMOLES_PER_LITER,
            gender=[MALE],
            **adult_age_options,
        ),
        p(
            "50.4<=x<=98.1",
            units=MICROMOLES_PER_LITER,
            gender=[FEMALE],
            **adult_age_options,
        ),
        p(
            "0.6<=x<=1.3",
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "crp": [
        p("0.0<=x<1.0", units=PLUS, gender=[MALE, FEMALE], **adult_age_options),
    ],
    "glucose": [
        p(
            "4.0<=x<=6.11",
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            fasting=True,
            **adult_age_options,
        ),
        p(
            "4.0<=x<=6.44",
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            fasting=False,
            **adult_age_options,
        ),
    ],
    "hba1c": [p("4.4<=x<=6.6", units=PERCENT, gender=[MALE, FEMALE], **adult_age_options)],
    "hdl": [
        p(
            "1.04<=x<=1.55",
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "ggt": [
        p("12<=x<=64", units=IU_LITER, gender=[MALE], **adult_age_options),
        p("9<=x<=36", units=IU_LITER, gender=[FEMALE], **adult_age_options),
    ],
    "haemoglobin": [
        p(
            "13.0<=x<=17.0",
            units=GRAMS_PER_DECILITER,
            gender=[MALE],
            **adult_age_options,
        ),
        p(
            "12.0<=x<=15.0",
            units=GRAMS_PER_DECILITER,
            gender=[FEMALE],
            **adult_age_options,
        ),
    ],
    # hematocrit
    "hct": [p("37.0<=x<=54.0", units=PERCENT, gender=[MALE, FEMALE], **adult_age_options)],
    "ldl": [
        p(
            "0.00<=x<=3.34",
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "magnesium": [
        p(
            "0.75<=x<=1.2",
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "1.8<=x<=2.9",
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "neutrophil": [
        p(
            "2.5<=x<=7.5",
            units=TEN_X_9_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
    "platelets": [
        p(
            "150<=x<=450",
            units=TEN_X_9_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "150000<=x<=450000",
            units=CELLS_PER_MILLIMETER_CUBED,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "potassium": [
        p(
            "3.6<=x<=5.2",
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
    "proteinuria": [
        p(
            "0.0<=x<1.0",
            units=PLUS,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "sodium": [
        p(
            "135<=x<=145",
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
    "trig": [
        p(
            "0.00<=x<=1.69",
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    # BUN
    "urea": [
        p(
            "2.5<=x<=6.5",
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
    "uric_acid": [
        p(
            "0.15<=x<=0.35",
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "7.2<=x",
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "rbc": [
        p(
            "3.5<=x<=5.5",
            units=TEN_X_9_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "3500<=x<=5500",
            units=CELLS_PER_MILLIMETER_CUBED,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    # TODO: tbil normal range is not set. range needed
    "tbil": [
        p(
            "0.0<=x<9999.0",
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "wbc": [
        p("2.49<x", units=TEN_X_9_PER_LITER, gender=[MALE, FEMALE], **adult_age_options),
    ],
}
