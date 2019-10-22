from edc_dashboard.utils import insert_bootstrap_version

dashboard_templates = dict(
    home_template="edc_review_dashboard/home.html",
    subject_review_listboard_template="edc_review_dashboard/subject_review_listboard.html",
)
dashboard_templates = insert_bootstrap_version(**dashboard_templates)
