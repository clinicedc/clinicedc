from django.conf import settings

AE = "AE"
AE_REVIEW = "AE_REVIEW"
AE_ROLE = "ae_role"
AE_SUPER = "AE_SUPER"

TMG = "TMG"
TMG_REVIEW = "TMG_REVIEW"
TMG_ROLE = "tmg"

ae_codenames = [
    "edc_adverse_event.nav_ae_section",
    "edc_adverse_event.view_ae_listboard",
    "edc_adverse_event.view_aeclassification",
    "edc_adverse_event.view_causeofdeath",
    "edc_adverse_event.view_saereason",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.add_aefollowup",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.add_aeinitial",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.add_aesusar",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.add_deathreport",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.change_aefollowup",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.change_aeinitial",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.change_aesusar",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.change_deathreport",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.delete_aefollowup",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.delete_aeinitial",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.delete_aesusar",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.delete_deathreport",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.view_aefollowup",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.view_aeinitial",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.view_aesusar",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.view_aetmg",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.view_deathreport",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.view_deathreporttmg",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.view_deathreporttmgsecond",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.view_historicalaefollowup",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.view_historicalaeinitial",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.view_historicalaesusar",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.view_historicalaetmg",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.view_historicaldeathreport",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.view_historicaldeathreporttmg",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.view_historicaldeathreporttmgsecond",
]

tmg_codenames = [
    "edc_adverse_event.nav_tmg_section",
    "edc_adverse_event.view_tmg_listboard",
    "edc_adverse_event.view_aeclassification",
    "edc_adverse_event.view_causeofdeath",
    "edc_adverse_event.view_saereason",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.add_aetmg",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.add_deathreporttmg",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.add_deathreporttmgsecond",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.change_aetmg",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.change_deathreporttmg",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.change_deathreporttmgsecond",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.delete_aetmg",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.delete_deathreporttmg",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.delete_deathreporttmgsecond",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.view_aefollowup",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.view_aeinitial",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.view_aesusar",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.view_aetmg",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.view_deathreport",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.view_deathreporttmg",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.view_deathreporttmgsecond",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.view_historicalaefollowup",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.view_historicalaeinitial",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.view_historicalaesusar",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.view_historicalaetmg",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.view_historicaldeathreport",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.view_historicaldeathreporttmg",
    f"{settings.ADVERSE_EVENT_APP_LABEL}.view_historicaldeathreporttmgsecond",
]

tmg_view_codenames = [c for c in tmg_codenames if "view_" in c]

ae_dashboard_tuples = (("edc_adverse_event.view_ae_listboard", "Can view AE listboard"),)
ae_navbar_tuples = (("edc_adverse_event.nav_ae_section", "Can view AE section"),)

tmg_dashboard_tuples = (("edc_adverse_event.view_tmg_listboard", "Can view TMG Listboard"),)
tmg_navbar_tuples = (("edc_adverse_event.nav_tmg_section", "Can view TMG section"),)
