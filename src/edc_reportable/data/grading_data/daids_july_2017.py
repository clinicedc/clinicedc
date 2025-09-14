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

from ...adult_age_options import adult_age_options
from ...constants import HIGH_VALUE
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

__all__ = [
    "chemistries",
    "dummies",
    "grading_data",
    "hba1c",
    "hematology",
    "urinalysis",
]

dummies = {
    "hba1c": [
        Formula(
            "x<0",
            grade=0,
            units=PERCENT,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
    "hct": [
        Formula(
            "x<0",
            grade=0,
            units=PERCENT,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
    "hdl": [
        Formula(
            "x<0",
            grade=0,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
    "ggt": [
        Formula(
            "x<0",
            grade=0,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
    "mch": [
        Formula(
            "x<0",
            grade=0,
            units=PICOGRAMS_PER_CELL,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "mchc": [
        Formula(
            "x<0",
            grade=0,
            units=GRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "mcv": [
        Formula(
            "x<0",
            grade=0,
            units=FEMTOLITERS_PER_CELL,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "rbc": [
        Formula(
            "x<0",
            grade=0,
            units=TEN_X_9_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "x<0",
            grade=0,
            units=CELLS_PER_MILLIMETER_CUBED,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "urea": [
        Formula(
            "x<0",
            grade=0,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        )
    ],
    "crp": [
        Formula(
            "x<0",
            grade=0,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "x<0",
            grade=0,
            units=MILLIGRAMS_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
}


chemistries = dict(
    albumin=[
        Formula(
            "x<2.0",
            grade=3,
            units=GRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "x<20",
            grade=3,
            units=GRAMS_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    alp=[
        Formula(
            "1.25*ULN<=x<2.50*ULN",
            grade=1,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "2.50*ULN<=x<5.00*ULN",
            grade=2,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "5.00*ULN<=x<10.00*ULN",
            grade=3,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "10.00*ULN<=x",
            grade=4,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    alt=[
        Formula(
            "1.25*ULN<=x<2.50*ULN",
            grade=1,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "2.50*ULN<=x<5.00*ULN",
            grade=2,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "5.00*ULN<=x<10.00*ULN",
            grade=3,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "10.00*ULN<=x",
            grade=4,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    amylase=[
        Formula(
            "1.1*ULN<=x<1.5*ULN",
            grade=1,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "1.5*ULN<=x<3.0*ULN",
            grade=2,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "3.0*ULN<=x<5.0*ULN",
            grade=3,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            f"5.0*ULN<=x<{HIGH_VALUE}*ULN",
            grade=4,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    ast=[
        Formula(
            "1.25*ULN<=x<2.50*ULN",
            grade=1,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "2.50*ULN<=x<5.00*ULN",
            grade=2,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "5.00*ULN<=x<10.00*ULN",
            grade=3,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "10.00*ULN<=x",
            grade=4,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    chol=[
        Formula(
            "300<=x",
            grade=3,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "7.77<=x",
            grade=3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    creatinine=[
        Formula(
            "1.1*ULN<=x<=1.3*ULN",
            grade=1,
            units=MICROMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "1.3*ULN<x<=1.8*ULN",
            grade=2,
            units=MICROMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "1.8*ULN<x<3.5*ULN",
            grade=3,
            units=MICROMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "3.5*ULN<=x",
            grade=4,
            units=MICROMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "1.1*ULN<=x<=1.3*ULN",
            grade=1,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "1.3*ULN<x<=1.8*ULN",
            grade=2,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "1.8*ULN<x<3.5*ULN",
            grade=3,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "3.5*ULN<=x",
            grade=4,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    egfr=[  # not considering % drop
        Formula(
            "60<=x<90",
            grade=2,
            units=EGFR_UNITS,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "30<=x<60",
            grade=3,
            units=EGFR_UNITS,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "x<30",
            grade=4,
            units=EGFR_UNITS,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    egfr_drop=[  # % drop from baseline
        Formula(
            "10<=x<30",
            grade=2,
            units=PERCENT,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "30<=x<50",
            grade=3,
            units=PERCENT,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "50<=x",
            grade=4,
            units=PERCENT,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    # glucose=[  # G3/G4 same for fasting / non-fasting
    #     Formula(
    #         "13.89<=x<27.75",
    #         grade=3,
    #         units=MILLIMOLES_PER_LITER,
    #         gender=[MALE, FEMALE],
    #         **adult_age_options,
    #         fasting=True,
    #     ),
    #     Formula(
    #         "27.75<=x",
    #         grade=4,
    #         units=MILLIMOLES_PER_LITER,
    #         gender=[MALE, FEMALE],
    #         **adult_age_options,
    #         fasting=True,
    #     ),
    #     Formula(
    #         "13.89<=x<27.75",
    #         grade=3,
    #         units=MILLIMOLES_PER_LITER,
    #         gender=[MALE, FEMALE],
    #         **adult_age_options,
    #         fasting=False,
    #     ),
    #     Formula(
    #         "27.75<=x",
    #         grade=4,
    #         units=MILLIMOLES_PER_LITER,
    #         gender=[MALE, FEMALE],
    #         **adult_age_options,
    #         fasting=False,
    #     ),
    # ],
    ldl=[
        Formula(
            "4.90<=x",
            grade=3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
            fasting=True,
        ),
    ],
    magnesium=[
        Formula(
            "0.30<=x<=0.44",
            grade=3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "x<0.30",
            grade=4,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "0.7<=x<=1.1",
            grade=3,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "x<0.7",
            grade=4,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    potassium=[
        Formula(
            "2.0<=x<2.5",
            grade=3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "x<2.0",
            grade=4,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "6.5<=x<7.0",
            grade=3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "7.0<=x",
            grade=4,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    sodium=[
        Formula(
            "121<=x<125",
            grade=3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "154<=x<160",
            grade=3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "160<=x",
            grade=4,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "x<=120",
            grade=4,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    tbil=[
        Formula(
            "1.10*ULN<=x<1.60*ULN",
            grade=1,
            units=MICROMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "1.60*ULN<=x<2.60*ULN",
            grade=2,
            units=MICROMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "2.60*ULN<=x<5.00*ULN",
            grade=3,
            units=MICROMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "5.00*ULN<=x",
            grade=4,
            units=MICROMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "1.10*ULN<=x<1.60*ULN",
            grade=1,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "1.60*ULN<=x<2.60*ULN",
            grade=2,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "2.60*ULN<=x<5.00*ULN",
            grade=3,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "5.00*ULN<=x",
            grade=4,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "1.10*ULN<=x<1.60*ULN",
            grade=1,
            units=GRAMS_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "1.60*ULN<=x<2.60*ULN",
            grade=2,
            units=GRAMS_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "2.60*ULN<=x<5.00*ULN",
            grade=3,
            units=GRAMS_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "5.00*ULN<=x",
            grade=4,
            units=GRAMS_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    trig=[
        Formula(
            "5.7<=x<=11.4",
            grade=3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
            fasting=True,
        ),
        Formula(
            "11.4<x",
            grade=3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
            fasting=True,
        ),
    ],
    uric_acid=[
        Formula(
            "12.0<=x<15.0",
            grade=3,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "15.0<=x",
            grade=4,
            units=MILLIGRAMS_PER_DECILITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "0.71<=x<0.89",
            grade=3,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "0.89<=x",
            grade=4,
            units=MILLIMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
)

hematology = {
    "haemoglobin": [
        Formula(
            "7.0<=x<9.0",
            grade=3,
            units=GRAMS_PER_DECILITER,
            gender=[MALE],
            **adult_age_options,
        ),
        Formula(
            "6.5<=x<8.5",
            grade=3,
            units=GRAMS_PER_DECILITER,
            gender=[FEMALE],
            **adult_age_options,
        ),
        Formula(
            "x<7.0",
            grade=4,
            units=GRAMS_PER_DECILITER,
            gender=[MALE],
            **adult_age_options,
        ),
        Formula(
            "x<6.5",
            grade=4,
            units=GRAMS_PER_DECILITER,
            gender=[FEMALE],
            **adult_age_options,
        ),
    ],
    "platelets": [
        Formula(
            "25<=x<=50",
            grade=3,
            units=TEN_X_9_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "x<25",
            grade=4,
            units=TEN_X_9_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "25000<=x<=50000",
            grade=3,
            units=CELLS_PER_MILLIMETER_CUBED,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "x<25000",
            grade=4,
            units=CELLS_PER_MILLIMETER_CUBED,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "neutrophil": [
        Formula(
            "0.40<=x<=0.59",
            grade=3,
            units=TEN_X_9_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "x<0.40",
            grade=4,
            units=TEN_X_9_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
    "wbc": [
        Formula(
            "1.00<=x<=1.49",
            grade=3,
            units=TEN_X_9_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "x<1.00",
            grade=4,
            units=TEN_X_9_PER_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
}

urinalysis = {
    "proteinuria": [
        Formula(
            "1<=x<2",
            grade=1,
            units=PLUS,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "2<=x<3",
            grade=2,
            units=PLUS,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        Formula(
            "3<=x",
            grade=3,
            units=PLUS,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
}

hba1c = {
    "hba1c": [
        Formula(
            "9999999<=x<=99999999",
            grade=3,
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
