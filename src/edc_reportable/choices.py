from edc_constants.constants import NO, NOT_APPLICABLE

from .constants import ALREADY_REPORTED, GRADE3, GRADE4, PRESENT_AT_BASELINE

REPORTABLE = (
    (NOT_APPLICABLE, "Not applicable"),
    (GRADE3, "Yes, grade 3"),
    (GRADE4, "Yes, grade 4"),
    (NO, "Not reportable"),
    (ALREADY_REPORTED, "Already reported"),
    (PRESENT_AT_BASELINE, "Present at baseline"),
)
