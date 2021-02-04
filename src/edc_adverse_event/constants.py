from django.conf import settings

ADVERSE_EVENT_APP_LABEL = getattr(settings, "ADVERSE_EVENT_APP_LABEL", "edc_adverse_event")
ADVERSE_EVENT_ADMIN_SITE = getattr(
    settings, "ADVERSE_EVENT_ADMIN_SITE", "edc_adverse_event_admin"
)
AESI_ACTION = "submit-aesi-report"
AE_FOLLOWUP_ACTION = "submit-ae-followup-report"
AE_INITIAL_ACTION = "submit-initial-ae-report"
AE_SUSAR_ACTION = "submit-ae-susar-report"
AE_TMG_ACTION = "submit-ae-tmg-report"
CONTINUING_UPDATE = "continuing/update"
DEATH_REPORT_ACTION = "submit-death-report"
DEATH_REPORT_TMG_ACTION = "submit-death-report-tmg"
DEATH_REPORT_TMG_SECOND_ACTION = "submit-death-report-tmg-2nd"
NOT_RECOVERED = "not_recovered"
RECOVERED = "recovered"
RECOVERED_WITH_SEQUELAE = "recovered_with_sequelae"
RECOVERING = "recovering"
STUDY_TERMINATION_CONCLUSION_ACTION = "submit-study-termination-conclusion"
