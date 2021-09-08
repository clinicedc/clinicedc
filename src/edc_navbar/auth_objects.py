navbars = [
    "edc_navbar.nav_administration",
    "edc_navbar.nav_action_item_section",
    "edc_navbar.nav_ae_section",
    "edc_navbar.nav_data_manager_section",
    "edc_navbar.nav_home",
    "edc_navbar.nav_export_section",
    "edc_navbar.nav_lab_aliquot",
    "edc_navbar.nav_lab_manifest",
    "edc_navbar.nav_lab_pack",
    "edc_navbar.nav_lab_process",
    "edc_navbar.nav_lab_receive",
    "edc_navbar.nav_lab_requisition",
    "edc_navbar.nav_lab_section",
    "edc_navbar.nav_logout",
    "edc_navbar.nav_pharmacy_section",
    "edc_navbar.nav_public",
    "edc_navbar.nav_screening_section",
    "edc_navbar.nav_enrolment_section",
    "edc_navbar.nav_subject_section",
    "edc_navbar.nav_tmg_section",
]

navbar_tuples = []
for codename in navbars:
    navbar_tuples.append((codename, f"Can access {codename.split('.')[1]}"))


def create_edc_navbar_permissions(auth_updater):
    auth_updater.create_permissions_from_tuples(
        model="edc_navbar.navbar", codename_tuples=navbar_tuples
    )


def remove_permissions_to_edc_navbar_model(auth_updater):
    for group in auth_updater.group_model_cls.objects.all():
        auth_updater.remove_permissions_by_codenames(
            group=group,
            codenames=[
                "edc_navbar.add_navbar",
                "edc_navbar.change_navbar",
                "edc_navbar.delete_navbar",
                "edc_navbar.view_navbar",
            ],
        )
