from edc_base import NavbarItem

navbar_items = []
config = [
    ('edc_lab_dashboard', 'requisition', 'Requisitions', None,
     'requisition_listboard_url_name'),
    ('edc_lab_dashboard', 'receive', 'Receive', None,
     'receive_listboard_url_name'),
    ('edc_lab_dashboard', 'process', 'Process', None,
     'process_listboard_url_name'),
    ('edc_lab_dashboard', 'pack', 'Pack', None,
     'pack_listboard_url_name'),
    ('edc_lab_dashboard', 'manifest', 'Manifests', None,
     'manifest_listboard_url_name'),
    ('edc_lab_dashboard', 'aliquot', 'Aliquots', None,
     'aliquot_listboard_url_name'),
    ('edc_lab_dashboard', 'result', 'Results', None,
     'result_listboard_url_name'),
    ('edc_lab_dashboard', 'home', '', 'fa-flask', 'home_url_name')
]
for app_config_name, name, label, fa_icon, app_config_attr in config:
    navbar_item = NavbarItem(
        app_config_name=app_config_name,
        name=name,
        label=label,
        fa_icon=fa_icon,
        app_config_attr=app_config_attr)
    navbar_items.append(navbar_item)
