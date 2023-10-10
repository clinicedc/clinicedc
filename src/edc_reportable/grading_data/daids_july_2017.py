"""
Based on Corrected Version 2.1 July 2017

Creatinine Clearance14 or eGFR, Low
*Report only one
NA
G1 N/A
G2 < 90 to 60 ml/min or ml/min/1.73 m2 OR 10 to < 30% decrease from participant’s baseline
G3 < 60 to 30 ml/min or ml/min/1.73 m2 OR 30 to < 50% decrease from participant’s baseline
G4 < 30 ml/min or ml/min/1.73 m2 OR ≥ 50% decrease from participant’s baseline
"""

from edc_constants.constants import FEMALE, MALE

from ..adult_age_options import adult_age_options
from ..constants import GRADE0, GRADE1, GRADE2, GRADE3, GRADE4, HIGH_VALUE
from ..parsers import parse as p
from ..units import (
    CELLS_PER_MILLIMETER_CUBED,
    EGFR_UNITS,
    GRAMS_PER_DECILITER,
    GRAMS_PER_LITER,
    IU_LITER,
    MICROMOLES_PER_LITER,
    MILLIGRAMS_PER_DECILITER,
    MILLIMOLES_PER_LITER,
    PERCENT,
    PLUS,
    TEN_X_9_PER_LITER,
)

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
    "crp": [
        p(
            "x<0",
            grade=GRADE0,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
}


chemistries = dict(
    albumin=[
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
    alp=[
        p(
            "1.25*ULN<=x<2.50*ULN",
            grade=GRADE1,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "2.50*ULN<=x<5.00*ULN",
            grade=GRADE2,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "5.00*ULN<=x<10.00*ULN",
            grade=GRADE3,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "10.00*ULN<=x",
            grade=GRADE4,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    alt=[
        p(
            "1.25*ULN<=x<2.50*ULN",
            grade=GRADE1,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "2.50*ULN<=x<5.00*ULN",
            grade=GRADE2,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "5.00*ULN<=x<10.00*ULN",
            grade=GRADE3,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "10.00*ULN<=x",
            grade=GRADE4,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    amylase=[
        p(
            "1.1*ULN<=x<1.5*ULN",
            grade=GRADE1,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "1.5*ULN<=x<3.0*ULN",
            grade=GRADE2,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "3.0*ULN<=x<5.0*ULN",
            grade=GRADE3,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            f"5.0*ULN<=x<{HIGH_VALUE}*ULN",
            grade=GRADE4,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    ast=[
        p(
            "1.25*ULN<=x<2.50*ULN",
            grade=GRADE1,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "2.50*ULN<=x<5.00*ULN",
            grade=GRADE2,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "5.00*ULN<=x<10.00*ULN",
            grade=GRADE3,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "10.00*ULN<=x",
            grade=GRADE4,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    chol=[
        p(
            "300<=x",
            grade=GRADE3,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "7.77<=x",
            grade=GRADE3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    creatinine=[
        p(
            "1.1*ULN<=x<=1.3*ULN",
            grade=GRADE1,
            units=MICROMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "1.3*ULN<x<=1.8*ULN",
            grade=GRADE2,
            units=MICROMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "1.8*ULN<x<3.5*ULN",
            grade=GRADE3,
            units=MICROMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "3.5*ULN<=x",
            grade=GRADE4,
            units=MICROMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "1.1*ULN<=x<=1.3*ULN",
            grade=GRADE1,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "1.3*ULN<x<=1.8*ULN",
            grade=GRADE2,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "1.8*ULN<x<3.5*ULN",
            grade=GRADE3,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "3.5*ULN<=x",
            grade=GRADE4,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    egfr=[  # not considering % drop
        p(
            "60<=x<90",
            grade=GRADE2,
            units=EGFR_UNITS,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "30<=x<60",
            grade=GRADE3,
            units=EGFR_UNITS,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "x<30",
            grade=GRADE4,
            units=EGFR_UNITS,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    egfr_drop=[  # % drop from baseline
        p(
            "10<=x<30",
            grade=GRADE2,
            units=PERCENT,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "30<=x<50",
            grade=GRADE3,
            units=PERCENT,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "50<=x",
            grade=GRADE4,
            units=PERCENT,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    glucose=[  # G3/G4 same for fasting / non-fasting
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
    ldl=[
        p(
            "4.90<=x",
            grade=GRADE3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
            fasting=True,
        ),
    ],
    magnesium=[
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
    potassium=[
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
    sodium=[
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
    # TODO: tbil in mmol/L
    tbil=[
        p(
            "1.00*ULN<=x<1.60*ULN",
            grade=GRADE1,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "1.60*ULN<=x<2.60*ULN",
            grade=GRADE2,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "2.60*ULN<=x<5.00*ULN",
            grade=GRADE3,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "5.00*ULN<=x",
            grade=GRADE4,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    trig=[
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
    uric_acid=[
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
)

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

urinalysis = {
    "proteinuria": [
        p(
            "1<=x<2",
            grade=GRADE1,
            units=PLUS,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "2<=x<3",
            grade=GRADE2,
            units=PLUS,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "3<=x",
            grade=GRADE3,
            units=PLUS,
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

grading_data = {}
grading_data.update(**dummies)
grading_data.update(**chemistries)
grading_data.update(**hematology)
grading_data.update(**hba1c)
grading_data.update(**urinalysis)
