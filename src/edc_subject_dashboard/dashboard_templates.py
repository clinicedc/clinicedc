"""To customize any of the values below,
use settings.DASHBOARD_BASE_TEMPLATES.
"""

from edc_dashboard.utils import insert_bootstrap_version

dashboard_templates = dict(
    edc_subject_dashboard_template="edc_subject_dashboard/dashboard.html"
)

dashboard_templates = insert_bootstrap_version(**dashboard_templates)
