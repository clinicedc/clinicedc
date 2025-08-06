from edc_constants.constants import (
    HOSPITAL_NOTES,
    IN_PERSON,
    NEXT_OF_KIN,
    NOT_APPLICABLE,
    OTHER,
    OTHER_PLEASE_SPECIFY_TEXT,
    OUTPATIENT_CARDS,
    PARTICIPANT,
    PATIENT,
    PATIENT_REPRESENTATIVE,
    TELEPHONE,
    TIMEPOINT,
)

from .constants import (
    CHART,
    COMPLETED_PROTOCOL_VISIT,
    DEFERRED_VISIT,
    LOST_VISIT,
    MISSED_VISIT,
    SCHEDULED,
    UNSCHEDULED,
)

ASSESSMENT_WHO_CHOICES = (
    (PATIENT, "Patient"),
    (NEXT_OF_KIN, "Next of kin"),
    (NOT_APPLICABLE, "Not applicable (if missed)"),
    (OTHER, OTHER_PLEASE_SPECIFY_TEXT),
)

ASSESSMENT_TYPES = (
    (TELEPHONE, "Telephone"),
    (IN_PERSON, "In person"),
    (NOT_APPLICABLE, "Not applicable (if missed)"),
    (OTHER, OTHER_PLEASE_SPECIFY_TEXT),
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
    (PARTICIPANT, "1. Clinic visit with participant"),
    ("other_contact", "2. Other contact with participant"),
    ("other_doctor", "3. Contact with external health care provider/medical doctor"),
    (
        "family",
        "4. Contact with family or designated person who can provide information",
    ),
    (CHART, "5. Hospital chart or other medical record"),
    (OTHER, "9. Other"),
)

# another option for VISIT_INFO_SOURCE
VISIT_INFO_SOURCE2 = (
    (PATIENT, "Patient"),
    (
        PATIENT_REPRESENTATIVE,
        "Patient representative (e.g., next of kin, relative, guardian)",
    ),
    (HOSPITAL_NOTES, "Hospital notes"),
    (OUTPATIENT_CARDS, "Outpatient cards"),
    (NOT_APPLICABLE, "Not applicable (if missed)"),
    (OTHER, "Other"),
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
    (TIMEPOINT, "Missed timepoint"),
    (OTHER, "Other"),
    (NOT_APPLICABLE, "Not applicable"),
)
