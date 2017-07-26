from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = 'edc_lab_dashboard'
    url_namespace = 'edc_lab_dashboard'

    admin_site_name = 'edc_lab_admin'
    dashboard_name = 'edc_lab_dashboard'

    aliquot_listboard_template_name = 'edc_lab_dashboard/aliquot_listboard.html'
    manage_box_listboard_template_name = 'edc_lab_dashboard/manage_box_listboard.html'
    manage_manifest_listboard_template_name = 'edc_lab_dashboard/manage_manifest_listboard.html'
    manifest_listboard_template_name = 'edc_lab_dashboard/manifest_listboard.html'
    pack_listboard_template_name = 'edc_lab_dashboard/pack_listboard.html'
    process_listboard_template_name = 'edc_lab_dashboard/process_listboard.html'
    receive_listboard_template_name = 'edc_lab_dashboard/receive_listboard.html'
    requisition_listboard_template_name = 'edc_lab_dashboard/requisition_listboard.html'
    result_listboard_template_name = 'edc_lab_dashboard/result_listboard.html'
    verify_box_listboard_template_name = 'edc_lab_dashboard/verify_box_listboard.html'

    aliquot_listboard_url_name = f'{dashboard_name}:aliquot_listboard_url'
    home_url_name = f'{dashboard_name}:home_url'
    manage_box_listboard_url_name = f'{dashboard_name}:manage_box_listboard_url'
    manage_manifest_listboard_url_name = f'{dashboard_name}:manage_manifest_listboard_url'
    manifest_listboard_url_name = f'{dashboard_name}:manifest_listboard_url'
    pack_listboard_url_name = f'{dashboard_name}:pack_listboard_url'
    process_listboard_url_name = f'{dashboard_name}:process_listboard_url'
    receive_listboard_url_name = f'{dashboard_name}:receive_listboard_url'
    requisition_listboard_url_name = f'{dashboard_name}:requisition_listboard_url'
    result_listboard_url_name = f'{dashboard_name}:result_listboard_url'
    verify_box_listboard_url_name = f'{dashboard_name}:verify_box_listboard_url'
