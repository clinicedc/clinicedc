from edc_constants.constants import HOSPITALIZED, OTHER

list_data = {
    "edc_visit_tracking.subjectvisitmissedreasons": [
        ("forgot", "Forgot / Can’t remember being told about appointment"),
        ("family_emergency", "Family emergency (e.g. funeral) and was away"),
        ("travelling", "Away travelling/visiting"),
        ("working_schooling", "Away working/schooling"),
        ("too_sick", "Too sick or weak to come to the centre"),
        ("lack_of_transport", "Transportation difficulty"),
        (HOSPITALIZED, "Hospitalized"),
        (OTHER, "Other reason (specify below)"),
    ],
}
