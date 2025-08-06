from edc_constants.constants import NOT_APPLICABLE, OTHER

list_data = {
    "edc_protocol_incident.protocolviolations": [
        ("failure_to_obtain_informed_consent", "Failure to obtain informed " "consent"),
        ("enrollment_of_ineligible_patient", "Enrollment of ineligible patient"),
        (
            "screening_procedure not done",
            "Screening procedure required by protocol not done",
        ),
        (
            "screening_or_on-study_procedure",
            "Screening or on-study procedure/lab work required not done",
        ),
        (
            "incorrect_research_treatment",
            "Incorrect research treatment given to patient",
        ),
        (
            "procedure_not_completed",
            "On-study procedure required by protocol not completed",
        ),
        ("visit_non-compliance", "Visit non-compliance"),
        ("medication_stopped_early", "Medication stopped early"),
        ("medication_noncompliance", "Medication_noncompliance"),
        (
            "national_regulations_not_met",
            "Standard WPD, ICH-GCP, local/national regulations not met",
        ),
        (OTHER, "Other"),
        (NOT_APPLICABLE, "Not applicable"),
    ],
    "edc_protocol_incident.actionsrequired": [
        ("remain_on_study", "Participant to remain on trial"),
        ("to_be_withdrawn", "Participant to be withdrawn from trial"),
        (
            "remain_on_study_modified",
            "Patient remains on study but data analysis will be modified",
        ),
    ],
}
