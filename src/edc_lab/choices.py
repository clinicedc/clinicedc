from edc_constants.constants import (
    COMPLETE,
    EQ,
    GT,
    GTE,
    LT,
    LTE,
    NOT_APPLICABLE,
    OTHER,
    PARTIAL,
    PENDING,
)
from edc_metadata.constants import NOT_REQUIRED
from edc_reportable import (
    MICROMOLES_PER_LITER,
    MICROMOLES_PER_LITER_DISPLAY,
    MILLIGRAMS_PER_DECILITER,
    MILLIMOLES_PER_LITER,
    MILLIMOLES_PER_LITER_DISPLAY,
)

from .constants import FILL_ACROSS, FILL_DOWN, FINGER_PRICK, TUBE

ABS_CALC = (("absolute", "Absolute"), ("calculated", "Calculated"))

ALIQUOT_STATUS = (("available", "available"), ("consumed", "consumed"))

ALIQUOT_CONDITIONS = (
    ("10", "OK"),
    ("20", "Inadequate volume for testing"),
    ("30", "Clotted or haemolised"),
    ("40", "Wrong tube type, unable to test"),
    ("50", "Sample degradation has occured. Unsuitable for testing"),
    ("60", "Expired tube"),
    ("70", "Technical problem at lab, unable to test"),
)

FILL_ORDER = ((FILL_ACROSS, "Across"), (FILL_DOWN, "Down"))

MODIFY_ACTIONS = (
    ("INSERT", "Insert"),
    ("UPDATE", "Update"),
    ("DELETE", "Delete"),
    ("PRINT", "Print"),
    ("VIEW", "Print"),
)

ORDER_STATUS = ((PENDING, "Pending"), (PARTIAL, "Partial"), (COMPLETE, "Complete"))

GLUCOSE_UNITS = (
    (MILLIGRAMS_PER_DECILITER, MILLIGRAMS_PER_DECILITER),
    (MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER_DISPLAY),
)

GLUCOSE_UNITS_NA = (
    (MILLIGRAMS_PER_DECILITER, MILLIGRAMS_PER_DECILITER),
    (MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER_DISPLAY),
    (NOT_APPLICABLE, "Not applicable"),
)
SERUM_CREATININE_UNITS = (
    (MILLIGRAMS_PER_DECILITER, MILLIGRAMS_PER_DECILITER),
    (MICROMOLES_PER_LITER, MICROMOLES_PER_LITER_DISPLAY),
)

SERUM_CREATININE_UNITS_NA = (
    (MILLIGRAMS_PER_DECILITER, MILLIGRAMS_PER_DECILITER),
    (MICROMOLES_PER_LITER, MICROMOLES_PER_LITER_DISPLAY),
    (NOT_APPLICABLE, "Not applicable"),
)

RESULT_RELEASE_STATUS = (
    ("NEW", "New"),
    ("RELEASED", "Released"),
    ("AMENDED", "Amended"),
)

RESULT_VALIDATION_STATUS = (("P", "Preliminary"), ("F", "Final"), ("R", "Rejected"))

RESULT_QUANTIFIER = ((EQ, EQ), (GT, GT), (GTE, GTE), (LT, LT), (LTE, LTE))

RESULT_QUANTIFIER_NA = (
    (EQ, EQ),
    (GT, GT),
    (GTE, GTE),
    (LT, LT),
    (LTE, LTE),
    (NOT_APPLICABLE, "Not applicable"),
)

VL_QUANTIFIER = (
    (EQ, EQ),
    (GT, GT),
    (LT, LT),
)

VL_QUANTIFIER_NA = (
    (EQ, EQ),
    (GT, GT),
    (LT, LT),
    (NOT_APPLICABLE, "Not applicable"),
)


SPECIMEN_MEASURE_UNITS = (
    ("mL", "mL"),
    ("uL", "uL"),
    ("spots", "spots"),
    ("n/a", "Not applicable"),
)

SPECIMEN_MEDIUM = (
    ("tube_any", "Tube"),
    ("tube_edta", "Tube EDTA"),
    ("swab", "Swab"),
    ("dbs_card", "DBS Card"),
)

UNITS = (
    ("%", "%"),
    ("10^3/uL", "10^3/uL"),
    ("10^3uL", "10^3uL"),
    ("10^6/uL", "10^6/uL"),
    ("cells/ul", "cells/ul"),
    ("copies/ml", "copies/ml"),
    ("fL", "fL"),
    ("g/dL", "g/dL"),
    ("g/L", "g/L"),
    ("mg/L", "mg/L"),
    ("mm/H", "mm/H"),
    ("mmol/L", "mmol/L"),
    ("ng/ml", "ng/ml"),
    ("pg", "pg"),
    ("ratio", "ratio"),
    ("U/L", "U/L"),
    ("umol/L", "umol/L"),
)

PRIORITY = (("normal", "Normal"), ("urgent", "Urgent"))

REASON_NOT_DRAWN = (
    (NOT_APPLICABLE, "Not applicable"),
    ("collection_failed", "Tried, but unable to obtain sample from patient"),
    ("absent", "Patient did not attend visit"),
    ("refused", "Patient refused"),
    ("no_supplies", "No supplies"),
    (NOT_REQUIRED, "No longer required for this visit"),
    (OTHER, "Other"),
)

ITEM_TYPE = (
    (NOT_APPLICABLE, "Not applicable"),
    (TUBE, "Tube"),
    (FINGER_PRICK, "Finger prick"),
    ("swab", "Swab"),
    ("dbs", "DBS Card"),
    (OTHER, "Other"),
)
