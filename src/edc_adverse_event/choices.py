from edc_constants.constants import DEAD, NOT_APPLICABLE
from edc_ltfu.constants import LOST_TO_FOLLOWUP
from edc_reportable import (
    GRADE3,
    GRADE4,
    GRADE5,
    MILD,
    MODERATE,
    SEVERE,
    SEVERITY_INCREASED_FROM_G3,
)

from .constants import (
    CONTINUING_UPDATE,
    NOT_RECOVERED,
    RECOVERED,
    RECOVERED_WITH_SEQUELAE,
    RECOVERING,
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
    (CONTINUING_UPDATE, "Continuing/Update"),
    (SEVERITY_INCREASED_FROM_G3, "Severity increased from Grade III"),
    (RECOVERED, "Recovered/Resolved"),
    (RECOVERING, "Recovering/Resolving at end of study"),
    (NOT_RECOVERED, "Not Recovered/Resolved at end of study"),
    (LOST_TO_FOLLOWUP, "Unknown/Lost to follow-up"),
    (RECOVERED_WITH_SEQUELAE, "Recovered with sequelae"),
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

STUDY_DRUG_RELATIONSHIP = (
    ("not_related", "Not related"),
    ("unlikely_related", "Unlikely related"),
    ("possibly_related", "Possibly related"),
    ("probably_related", "Probably related"),
    ("definitely_related", "Definitely related"),
    (NOT_APPLICABLE, "Not applicable"),
)
