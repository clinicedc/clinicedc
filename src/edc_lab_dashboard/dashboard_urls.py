from django.conf import settings

"""To customize any of the values below,
use settings.LAB_DASHBOARD_URL_NAMES.
"""

dashboard_urls = dict(
    listboard_url=f'edc_lab_dashboard:requisition_listboard_url',
    dashboard_url=f'edc_lab_dashboard:home_url',
    aliquot_listboard_url=f'edc_lab_dashboard:aliquot_listboard_url',
    home_url=f'edc_lab_dashboard:home_url',
    manage_box_listboard_url=f'edc_lab_dashboard:manage_box_listboard_url',
    manage_manifest_listboard_url=f'edc_lab_dashboard:manage_manifest_listboard_url',
    manifest_listboard_url=f'edc_lab_dashboard:manifest_listboard_url',
    pack_listboard_url=f'edc_lab_dashboard:pack_listboard_url',
    process_listboard_url=f'edc_lab_dashboard:process_listboard_url',
    receive_listboard_url=f'edc_lab_dashboard:receive_listboard_url',
    requisition_listboard_url=f'edc_lab_dashboard:requisition_listboard_url',
    result_listboard_url=f'edc_lab_dashboard:result_listboard_url',
    verify_box_listboard_url=f'edc_lab_dashboard:verify_box_listboard_url',

    manage_box_item_action_url=f'edc_lab_dashboard:manage_box_item_url',
    manage_manifest_item_action_url=f'edc_lab_dashboard:manage_manifest_item_url',
    requisition_action_url=f'edc_lab_dashboard:requisition_url',
    receive_action_url=f'edc_lab_dashboard:receive_url',
    pack_action_url=f'edc_lab_dashboard:pack_url',
    verify_box_item_action_url=f'edc_lab_dashboard:verify_box_item_url',
)

try:
    dashboard_urls.update(**settings.LAB_DASHBOARD_URL_NAMES)
except AttributeError:
    pass
