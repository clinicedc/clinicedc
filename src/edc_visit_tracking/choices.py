from edc_constants.constants import OTHER, NOT_APPLICABLE

from .constants import (
    MISSED_VISIT,
    SCHEDULED,
    UNSCHEDULED,
    LOST_VISIT,
    DEFERRED_VISIT,
    COMPLETED_PROTOCOL_VISIT,
    CHART,
)

VISIT_REASON = (
    (SCHEDULED, "Scheduled visit/contact"),
    (UNSCHEDULED, "Unscheduled visit/contact"),
    (MISSED_VISIT, "Missed visit"),
    (LOST_VISIT, "Lost to follow-up (use only when taking subject off study)"),
    (DEFERRED_VISIT, "Deferred"),
    (COMPLETED_PROTOCOL_VISIT, "Completed protocol"),
)

VISIT_INFO_SOURCE = (
    ("participant", "1. Clinic visit with participant"),
    ("other_contact", "2. Other contact with participant"),
    ("other_doctor", "3. Contact with external health care provider/medical doctor"),
    (
        "family",
        "4. Contact with family or designated person who can provide information",
    ),
    (CHART, "5. Hospital chart or other medical record"),
    (OTHER, "9. Other"),
)

# these defaults are not intended for production
VISIT_REASON_UNSCHEDULED = (
    ("patient_unwell_outpatient", "Patient unwell (outpatient)"),
    ("patient_hospitalised", "Patient hospitalised"),
    (OTHER, "Other"),
    (NOT_APPLICABLE, "Not applicable"),
)

# these defaults are not intended for production
VISIT_REASON_MISSED = (
    ("timepoint", "Missed timepoint"),
    (OTHER, "Other"),
    (NOT_APPLICABLE, "Not applicable"),
)
