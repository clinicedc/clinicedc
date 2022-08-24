lab_navbar_codenames = [
    "edc_navbar.nav_lab_aliquot",
    "edc_navbar.nav_lab_manifest",
    "edc_navbar.nav_lab_pack",
    "edc_navbar.nav_lab_process",
    "edc_navbar.nav_lab_receive",
    "edc_navbar.nav_lab_requisition",
    "edc_navbar.nav_lab_section",
]

lab_navbar_tuples = []
for codename in lab_navbar_codenames:
    lab_navbar_tuples.append((codename, f"Can access {codename.split('.')[1]}"))


lab_dashboard_codenames = [
    "edc_dashboard.view_lab_aliquot_listboard",
    "edc_dashboard.view_lab_box_listboard",
    "edc_dashboard.view_lab_manifest_listboard",
    "edc_dashboard.view_lab_pack_listboard",
    "edc_dashboard.view_lab_process_listboard",
    "edc_dashboard.view_lab_receive_listboard",
    "edc_dashboard.view_lab_requisition_listboard",
    "edc_dashboard.view_lab_result_listboard",
]

lab_dashboard_tuples = []
for codename in lab_dashboard_codenames:
    lab_dashboard_tuples.append((codename, f"Can access {codename.split('.')[1]}"))
