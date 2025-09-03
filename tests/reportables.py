from edc_constants.constants import FEMALE, MALE
from edc_reportable import (
    MICROMOLES_PER_LITER,
    MILLIGRAMS_PER_DECILITER,
    PERCENT,
    TEN_X_9_PER_LITER,
    Formula,
)
from edc_reportable.adult_age_options import adult_age_options
from edc_reportable.data import africa, daids_july_2017

grading_data = {}
grading_data.update(**daids_july_2017.dummies)
grading_data.update(**daids_july_2017.chemistries)
grading_data.update(**daids_july_2017.hematology)

collection_name = "my_reportables"
normal_data = africa.normal_data
reportable_grades = [3, 4]
reportable_grades_exceptions = {}

normal_data.update(
    {
        "creatinine": [
            Formula(
                "63.6<=x<=114.0",
                units=MICROMOLES_PER_LITER,
                gender=[MALE],
                **adult_age_options,
            ),
            Formula(
                "63.6<=x<=114.0",
                units=MICROMOLES_PER_LITER,
                gender=[FEMALE],
                **adult_age_options,
            ),
            Formula(
                "0.71868<=x<=1.2882",
                units=MILLIGRAMS_PER_DECILITER,
                gender=[MALE],
                **adult_age_options,
            ),
            Formula(
                "0.71868<=x<=1.2882",
                units=MILLIGRAMS_PER_DECILITER,
                gender=[FEMALE],
                **adult_age_options,
            ),
        ],
        "neutrophil_diff": [
            Formula(
                "40.0<=x<=60.0",
                units=PERCENT,
                gender=[MALE, FEMALE],
                **adult_age_options,
            )
        ],
        "lymphocyte": [
            Formula(
                "1.00<=x<=4.80",
                units=TEN_X_9_PER_LITER,
                gender=[MALE, FEMALE],
                **adult_age_options,
            )
        ],
        "lymphocyte_diff": [
            Formula(
                "20.0<=x<=40.0",
                units=PERCENT,
                gender=[MALE, FEMALE],
                **adult_age_options,
            )
        ],
        "csf_wbc": [
            Formula(
                "0<=x<=99999",
                units=PERCENT,
                gender=[MALE, FEMALE],
                **adult_age_options,
            )
        ],
        "csf_glucose": [
            Formula(
                "0<=x<=99999",
                units=PERCENT,
                gender=[MALE, FEMALE],
                **adult_age_options,
            )
        ],
        "csf_protein": [
            Formula(
                "0<=x<=99999",
                units=PERCENT,
                gender=[MALE, FEMALE],
                **adult_age_options,
            )
        ],
        "csf_crag": [
            Formula(
                "0<=x<=99999",
                units=PERCENT,
                gender=[MALE, FEMALE],
                **adult_age_options,
            )
        ],
        "csf_crag_lfa": [
            Formula(
                "0<=x<=99999",
                units=PERCENT,
                gender=[MALE, FEMALE],
                **adult_age_options,
            )
        ],
    }
)

grading_data.update(
    {
        "neutrophil_diff": [
            Formula(
                "x<0",
                grade=0,
                units=PERCENT,
                gender=[MALE, FEMALE],
                **adult_age_options,
            )
        ],
        "lymphocyte": [
            Formula(
                "x<0",
                grade=0,
                units=TEN_X_9_PER_LITER,
                gender=[MALE, FEMALE],
                **adult_age_options,
            )
        ],
        "lymphocyte_diff": [
            Formula(
                "x<0",
                grade=0,
                units=PERCENT,
                gender=[MALE, FEMALE],
                **adult_age_options,
            )
        ],
        "csf_wbc": [
            Formula(
                "x<0",
                grade=0,
                units=PERCENT,
                gender=[MALE, FEMALE],
                **adult_age_options,
            )
        ],
        "csf_glucose": [
            Formula(
                "x<0",
                grade=0,
                units=PERCENT,
                gender=[MALE, FEMALE],
                **adult_age_options,
            )
        ],
        "csf_protein": [
            Formula(
                "x<0",
                grade=0,
                units=PERCENT,
                gender=[MALE, FEMALE],
                **adult_age_options,
            )
        ],
        "csf_crag": [
            Formula(
                "x<0",
                grade=0,
                units=PERCENT,
                gender=[MALE, FEMALE],
                **adult_age_options,
            )
        ],
        "csf_crag_lfa": [
            Formula(
                "x<0",
                grade=0,
                units=PERCENT,
                gender=[MALE, FEMALE],
                **adult_age_options,
            )
        ],
        "proteinuria": [
            Formula(
                "x<0",
                grade=0,
                units=PERCENT,
                gender=[MALE, FEMALE],
                **adult_age_options,
            )
        ],
    }
)


reference_range_options = dict(
    collection_name=collection_name,
    normal_data=africa.normal_data,
    grading_data=grading_data,
    reportable_grades=reportable_grades,
    reportable_grades_exceptions=reportable_grades_exceptions,
)
