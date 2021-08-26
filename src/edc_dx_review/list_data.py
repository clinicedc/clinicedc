from edc_constants.constants import (
    DEAD,
    DIABETES,
    FREE_OF_CHARGE,
    HIV,
    HOSPITALIZED,
    HYPERTENSION,
    NOT_APPLICABLE,
    OTHER,
    REFILL,
    ROUTINE_VISIT,
    STUDY_DEFINED_TIMEPOINT,
    UNKNOWN,
    UNWELL_VISIT,
)
from edc_ltfu.constants import LOST_TO_FOLLOWUP
from edc_offstudy.constants import LATE_EXCLUSION, WITHDRAWAL
from edc_transfer.constants import TRANSFERRED

list_data = {
    "edc_dx_review.diagnosislocations": [
        ("hospital", "Hospital"),
        ("gov_clinic", "Government clinic"),
        ("private_clinic", "Private clinic"),
        ("private_doctor", "Private doctor"),
        ("mocca_clinic", "MOCCA study clinic"),
        (UNKNOWN, "Don't recall"),
        (OTHER, "Other, specify"),
    ],
}
