from .utils import get_adverse_event_app_label, get_hospitalization_model_app_label

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
    f"{get_adverse_event_app_label()}.add_aefollowup",
    f"{get_adverse_event_app_label()}.add_aeinitial",
    f"{get_adverse_event_app_label()}.add_aesusar",
    f"{get_adverse_event_app_label()}.add_deathreport",
    f"{get_hospitalization_model_app_label()}.add_hospitalization",
    f"{get_adverse_event_app_label()}.change_aefollowup",
    f"{get_adverse_event_app_label()}.change_aeinitial",
    f"{get_adverse_event_app_label()}.change_aesusar",
    f"{get_adverse_event_app_label()}.change_deathreport",
    f"{get_hospitalization_model_app_label()}.change_hospitalization",
    f"{get_adverse_event_app_label()}.delete_aefollowup",
    f"{get_adverse_event_app_label()}.delete_aeinitial",
    f"{get_adverse_event_app_label()}.delete_aesusar",
    f"{get_adverse_event_app_label()}.delete_deathreport",
    f"{get_hospitalization_model_app_label()}.delete_hospitalization",
    f"{get_adverse_event_app_label()}.view_aefollowup",
    f"{get_adverse_event_app_label()}.view_aeinitial",
    f"{get_adverse_event_app_label()}.view_aesusar",
    f"{get_adverse_event_app_label()}.view_aetmg",
    f"{get_adverse_event_app_label()}.view_deathreport",
    f"{get_adverse_event_app_label()}.view_deathreporttmg",
    f"{get_adverse_event_app_label()}.view_deathreporttmgsecond",
    f"{get_hospitalization_model_app_label()}.view_hospitalization",
    f"{get_adverse_event_app_label()}.view_historicalaefollowup",
    f"{get_adverse_event_app_label()}.view_historicalaeinitial",
    f"{get_adverse_event_app_label()}.view_historicalaesusar",
    f"{get_adverse_event_app_label()}.view_historicalaetmg",
    f"{get_adverse_event_app_label()}.view_historicaldeathreport",
    f"{get_adverse_event_app_label()}.view_historicaldeathreporttmg",
    f"{get_adverse_event_app_label()}.view_historicaldeathreporttmgsecond",
    f"{get_hospitalization_model_app_label()}.view_historicalhospitalization",
]

tmg_codenames = [
    "edc_adverse_event.nav_tmg_section",
    "edc_adverse_event.view_tmg_listboard",
    "edc_adverse_event.view_aeclassification",
    "edc_adverse_event.view_causeofdeath",
    "edc_adverse_event.view_saereason",
    f"{get_adverse_event_app_label()}.add_aetmg",
    f"{get_adverse_event_app_label()}.add_deathreporttmg",
    f"{get_adverse_event_app_label()}.add_deathreporttmgsecond",
    f"{get_adverse_event_app_label()}.change_aetmg",
    f"{get_adverse_event_app_label()}.change_deathreporttmg",
    f"{get_adverse_event_app_label()}.change_deathreporttmgsecond",
    f"{get_adverse_event_app_label()}.delete_aetmg",
    f"{get_adverse_event_app_label()}.delete_deathreporttmg",
    f"{get_adverse_event_app_label()}.delete_deathreporttmgsecond",
    f"{get_adverse_event_app_label()}.view_aefollowup",
    f"{get_adverse_event_app_label()}.view_aeinitial",
    f"{get_adverse_event_app_label()}.view_aesusar",
    f"{get_adverse_event_app_label()}.view_aetmg",
    f"{get_adverse_event_app_label()}.view_deathreport",
    f"{get_adverse_event_app_label()}.view_deathreporttmg",
    f"{get_adverse_event_app_label()}.view_deathreporttmgsecond",
    f"{get_hospitalization_model_app_label()}.view_hospitalization",
    f"{get_adverse_event_app_label()}.view_historicalaefollowup",
    f"{get_adverse_event_app_label()}.view_historicalaeinitial",
    f"{get_adverse_event_app_label()}.view_historicalaesusar",
    f"{get_adverse_event_app_label()}.view_historicalaetmg",
    f"{get_adverse_event_app_label()}.view_historicaldeathreport",
    f"{get_adverse_event_app_label()}.view_historicaldeathreporttmg",
    f"{get_adverse_event_app_label()}.view_historicaldeathreporttmgsecond",
    f"{get_hospitalization_model_app_label()}.view_historicalhospitalization",
]

tmg_view_codenames = [c for c in tmg_codenames if "view_" in c]

ae_dashboard_tuples = (("edc_adverse_event.view_ae_listboard", "Can view AE listboard"),)
ae_navbar_tuples = (("edc_adverse_event.nav_ae_section", "Can view AE section"),)

tmg_dashboard_tuples = (("edc_adverse_event.view_tmg_listboard", "Can view TMG Listboard"),)
tmg_navbar_tuples = (("edc_adverse_event.nav_tmg_section", "Can view TMG section"),)
