from edc_dashboard.utils import insert_bootstrap_version

dashboard_templates = dict(
    ae_home_template="edc_adverse_event/ae/ae_home.html",
    ae_listboard_template="edc_adverse_event/ae/ae_listboard.html",
    ae_death_report_listboard_template="edc_adverse_event/ae/ae_death_report_listboard.html",
    tmg_ae_listboard_template="edc_adverse_event/tmg/tmg_ae_listboard.html",
    tmg_ae_listboard_result_template="edc_adverse_event/tmg/tmg_ae_listboard_result.html",
    tmg_death_listboard_template="edc_adverse_event/tmg/tmg_death_listboard.html",
    tmg_home_template="edc_adverse_event/tmg/tmg_home.html",
    tmg_summary_listboard_template="edc_adverse_event/tmg/tmg_summary_listboard.html",
)
dashboard_templates = insert_bootstrap_version(**dashboard_templates)
