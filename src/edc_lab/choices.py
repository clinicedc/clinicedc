from django.utils.translation import gettext_lazy as _
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
    ("10", _("OK")),
    ("20", _("Inadequate volume for testing")),
    ("30", _("Clotted or haemolised")),
    ("40", _("Wrong tube type, unable to test")),
    ("50", _("Sample degradation has occured. Unsuitable for testing")),
    ("60", _("Expired tube")),
    ("70", _("Technical problem at lab, unable to test")),
)

FILL_ORDER = ((FILL_ACROSS, _("Across")), (FILL_DOWN, _("Down")))

MODIFY_ACTIONS = (
    ("INSERT", _("Insert")),
    ("UPDATE", _("Update")),
    ("DELETE", _("Delete")),
    ("PRINT", _("Print")),
    ("VIEW", _("Print")),
)

ORDER_STATUS = ((PENDING, _("Pending")), (PARTIAL, _("Partial")), (COMPLETE, _("Complete")))

GLUCOSE_UNITS = (
    (MILLIGRAMS_PER_DECILITER, MILLIGRAMS_PER_DECILITER),
    (MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER_DISPLAY),
)

GLUCOSE_UNITS_NA = (
    (MILLIGRAMS_PER_DECILITER, MILLIGRAMS_PER_DECILITER),
    (MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER_DISPLAY),
    (NOT_APPLICABLE, _("Not applicable")),
)
SERUM_CREATININE_UNITS = (
    (MILLIGRAMS_PER_DECILITER, MILLIGRAMS_PER_DECILITER),
    (MICROMOLES_PER_LITER, MICROMOLES_PER_LITER_DISPLAY),
)

SERUM_CREATININE_UNITS_NA = (
    (MILLIGRAMS_PER_DECILITER, MILLIGRAMS_PER_DECILITER),
    (MICROMOLES_PER_LITER, MICROMOLES_PER_LITER_DISPLAY),
    (NOT_APPLICABLE, _("Not applicable")),
)

RESULT_RELEASE_STATUS = (
    ("NEW", _("New")),
    ("RELEASED", _("Released")),
    ("AMENDED", _("Amended")),
)

RESULT_VALIDATION_STATUS = (("P", _("Preliminary")), ("F", _("Final")), ("R", _("Rejected")))

RESULT_QUANTIFIER = ((EQ, EQ), (GT, GT), (GTE, GTE), (LT, LT), (LTE, LTE))

RESULT_QUANTIFIER_NA = (
    (EQ, EQ),
    (GT, GT),
    (GTE, GTE),
    (LT, LT),
    (LTE, LTE),
    (NOT_APPLICABLE, _("Not applicable")),
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
    (NOT_APPLICABLE, _("Not applicable")),
)


SPECIMEN_MEASURE_UNITS = (
    ("mL", "mL"),
    ("uL", "uL"),
    ("spots", _("spots")),
    ("n/a", _("Not applicable")),
)

SPECIMEN_MEDIUM = (
    ("tube_any", _("Tube")),
    ("tube_edta", _("Tube EDTA")),
    ("swab", _("Swab")),
    ("dbs_card", _("DBS Card")),
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

PRIORITY = (("normal", _("Normal")), ("urgent", _("Urgent")))

REASON_NOT_DRAWN = (
    (NOT_APPLICABLE, _("Not applicable")),
    ("collection_failed", _("Tried, but unable to obtain sample from patient")),
    ("absent", _("Patient did not attend visit")),
    ("refused", _("Patient refused")),
    ("no_supplies", _("No supplies")),
    (NOT_REQUIRED, _("No longer required for this visit")),
    (OTHER, _("Other")),
)

ITEM_TYPE = (
    (NOT_APPLICABLE, _("Not applicable")),
    (TUBE, _("Tube")),
    (FINGER_PRICK, _("Finger prick")),
    ("swab", _("Swab")),
    ("dbs", _("DBS Card")),
    (OTHER, _("Other")),
)
