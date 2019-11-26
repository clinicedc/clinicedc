from django.conf import settings

from .action_items import action_items
from .ae_review import ae_review

tmg = [
    "edc_appointment.view_appointment",
    "edc_appointment.view_historicalappointment",
    "edc_dashboard.view_screening_listboard",
    "edc_dashboard.view_subject_listboard",
    "edc_dashboard.view_subject_review_listboard",
    "edc_dashboard.view_tmg_listboard",
    "edc_navbar.nav_screening_section",
    "edc_navbar.nav_subject_section",
    "edc_navbar.nav_tmg_section",
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

tmg.extend([c for c in ae_review])
tmg.extend(action_items)
