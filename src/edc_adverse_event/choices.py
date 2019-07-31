from edc_constants.constants import (
    NOT_APPLICABLE,
    DEAD,
    LOST_TO_FOLLOWUP,
    OTHER,
    UNKNOWN,
)

from edc_reportable import (
    GRADE3,
    GRADE4,
    GRADE5,
    MILD,
    MODERATE,
    SEVERE,
    SEVERITY_INCREASED_FROM_G3,
)

AE_INTENSITY = ((MILD, "Mild"), (MODERATE, "Moderate"), (SEVERE, "Severe"))

AE_REPORT_TYPE = (
    ("initial", "Initial"),
    ("follow_up", "Follow Up"),
    ("final", "Final"),
)

AE_GRADE = (
    (GRADE3, "Grade III - Severe"),
    (GRADE4, "Grade 4 - Life-threatening"),
    (GRADE5, "Grade 5 - Death"),
)

AE_GRADE_SIMPLE = (
    (GRADE4, "Grade 4 - Life-threatening"),
    (GRADE5, "Grade 5 - Death"),
    (NOT_APPLICABLE, "Not applicable"),
)

# TODO: validate Severity increased from Grade III
AE_OUTCOME = (
    ("continuing/update", "Continuing/Update"),
    (SEVERITY_INCREASED_FROM_G3, "Severity increased from Grade III"),
    ("recovered", "Recovered/Resolved"),
    ("recovering", "Recovering/Resolving at end of study"),
    ("not_recovered", "Not Recovered/Resolved at end of study"),
    (LOST_TO_FOLLOWUP, "Unknown/Lost to follow-up"),
    ("recovered_with_sequelae", "Recovered with sequelae"),
    (DEAD, "Death"),
)

SAE_REASONS = (
    (NOT_APPLICABLE, "Not applicable"),
    (DEAD, "Death"),
    ("life_threatening", "Life-threatening"),
    ("significant_disability", "Significant disability"),
    (
        "in-patient_hospitalization",
        "In-patient hospitalization or prolongation (17 or more days from study inclusion)",
    ),
    (
        "medically_important_event",
        "Medically important event (e.g. Severe thrombophlebitis, Bacteraemia, "
        "recurrence of symptoms not requiring admission, Hospital acquired "
        "pneumonia)",
    ),
)


# change to FK
AE_CLASSIFICATION = ((OTHER, "Other"),)


# change to FK
CAUSE_OF_DEATH = ((UNKNOWN, "Unknown"), (OTHER, "Other"))
