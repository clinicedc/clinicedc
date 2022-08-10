"""To customize any of the values below,
use settings.LAB_DASHBOARD_URL_NAMES.
"""
from django.conf import settings

dashboard_urls = dict(
    aliquot_listboard_url="edc_lab_dashboard:aliquot_listboard_url",
    dashboard_url="edc_lab_dashboard:home_url",
    # home_url="edc_lab_dashboard:home_url",
    listboard_url="edc_lab_dashboard:requisition_listboard_url",
    manage_box_listboard_url="edc_lab_dashboard:manage_box_listboard_url",
    manage_manifest_listboard_url="edc_lab_dashboard:manage_manifest_listboard_url",
    manifest_listboard_url="edc_lab_dashboard:manifest_listboard_url",
    pack_listboard_url="edc_lab_dashboard:pack_listboard_url",
    process_listboard_url="edc_lab_dashboard:process_listboard_url",
    receive_listboard_url="edc_lab_dashboard:receive_listboard_url",
    requisition_listboard_url="edc_lab_dashboard:requisition_listboard_url",
    result_listboard_url="edc_lab_dashboard:result_listboard_url",
    verify_box_listboard_url="edc_lab_dashboard:verify_box_listboard_url",
    print_manifest_url="edc_lab_dashboard:print_manifest_url",
    aliquot_form_action_url="edc_lab_dashboard:aliquot_form_action_url",
    manage_box_item_form_action_url="edc_lab_dashboard:manage_box_item_form_action_url",
    manage_manifest_item_form_action_url=(
        "edc_lab_dashboard:manage_manifest_item_form_action_url"
    ),
    manifest_form_action_url="edc_lab_dashboard:manifest_form_action_url",
    pack_form_action_url="edc_lab_dashboard:pack_form_action_url",
    process_form_action_url="edc_lab_dashboard:process_form_action_url",
    receive_form_action_url="edc_lab_dashboard:receive_form_action_url",
    requisition_form_action_url="edc_lab_dashboard:requisition_form_action_url",
    verify_box_item_form_action_url="edc_lab_dashboard:verify_box_item_form_action_url",
)

try:
    dashboard_urls.update(**settings.LAB_DASHBOARD_URL_NAMES)
except AttributeError:
    pass
