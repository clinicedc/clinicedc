from edc_constants.constants import DEAD, NOT_APPLICABLE, OTHER, UNKNOWN

list_data = {
    "edc_adverse_event.aeclassification": [
        ("adr", "Adverse drug reaction (ADR)"),
        (OTHER, "Other"),
    ],
    "edc_adverse_event.saereason": [
        (NOT_APPLICABLE, "Not applicable"),
        (DEAD, "Death"),
        ("life_threatening", "Life-threatening"),
        ("significant_disability", "Significant disability"),
        (
            "in-patient_hospitalization",
            "In-patient hospitalization or prolongation ",
        ),
        (
            "medically_important_event",
            "Medically important event",
        ),
    ],
    "edc_adverse_event.causeofdeath": [
        (UNKNOWN, "Unknown"),
        (OTHER, "Other"),
    ],
    "edc_adverse_event.aeactionclassification": [
        (UNKNOWN, "Unknown"),
        (OTHER, "Other"),
    ],
}
