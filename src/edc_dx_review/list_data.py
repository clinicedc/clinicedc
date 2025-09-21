from edc_constants.constants import OTHER, UNKNOWN

list_data = {
    "edc_dx_review.diagnosislocations": [
        ("hospital", "Hospital"),
        ("gov_clinic", "Government clinic"),
        ("private_clinic", "Private clinic"),
        ("private_doctor", "Private doctor"),
        ("study_clinic", "Study clinic"),
        (UNKNOWN, "Don't recall"),
        (OTHER, "Other, specify"),
    ],
    "edc_dx_review.reasonsfortesting": [
        ("patient_request", "Patient was well and made a request"),
        ("patient_complication", "Patient had a clinical complication"),
        ("signs_symptoms", "Patient had suggestive signs and symptoms"),
        (OTHER, "Other reason (specify below)"),
    ],
}
