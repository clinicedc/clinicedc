"""To customize any of the values below,
use settings.LAB_DASHBOARD_BASE_TEMPLATES.
"""
from django.conf import settings
from edc_dashboard.utils import insert_bootstrap_version

dashboard_templates = dict(
    aliquot_listboard_template="edc_lab_dashboard/aliquot_listboard.html",
    box_listboard_template="edc_lab_dashboard/box_listboard.html",
    edc_lab_base_template="edc_lab_dashboard/base.html",
    home_template="edc_lab_dashboard/home.html",
    edc_lab_base_listboard_template="edc_lab_dashboard/base_listboard.html",
    edc_lab_listboard_template="edc_lab_dashboard/listboard.html",
    manage_box_listboard_template="edc_lab_dashboard/manage_box_listboard.html",
    manage_manifest_listboard_template="edc_lab_dashboard/manage_manifest_listboard.html",  # noqa
    manifest_listboard_template="edc_lab_dashboard/manifest_listboard.html",
    pack_listboard_template="edc_lab_dashboard/pack_listboard.html",
    process_listboard_template="edc_lab_dashboard/process_listboard.html",
    receive_listboard_template="edc_lab_dashboard/receive_listboard.html",
    requisition_listboard_template="edc_lab_dashboard/requisition_listboard.html",
    result_listboard_template="edc_lab_dashboard/result_listboard.html",
    verify_box_listboard_template="edc_lab_dashboard/verify_box_listboard.html",
)

try:
    dashboard_templates.update(**settings.LAB_DASHBOARD_BASE_TEMPLATES)
except AttributeError:
    pass

dashboard_templates = insert_bootstrap_version(**dashboard_templates)
