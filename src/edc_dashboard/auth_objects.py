dashboard_tuples = [
    (
        "edc_dashboard.view_lab_requisition_listboard",
        "Can view Lab requisition listboard",
    ),
    ("edc_dashboard.view_lab_receive_listboard", "Can view Lab receive listboard"),
    ("edc_dashboard.view_lab_process_listboard", "Can view Lab process listboard"),
    ("edc_dashboard.view_lab_pack_listboard", "Can view Lab pack listboard"),
    ("edc_dashboard.view_lab_aliquot_listboard", "Can view Lab aliquot listboard"),
    ("edc_dashboard.view_lab_box_listboard", "Can view Lab box listboard"),
    ("edc_dashboard.view_lab_result_listboard", "Can view Lab result listboard"),
    ("edc_dashboard.view_lab_manifest_listboard", "Can view Lab manifest listboard"),
    (
        "edc_dashboard.view_subject_review_listboard",
        "Can view Subject review listboard",
    ),
    ("edc_dashboard.view_ae_listboard", "Can view AE listboard"),
    ("edc_dashboard.view_enrolment_listboard", "Can view Enrolment listboard"),
    ("edc_dashboard.view_export_dashboard", "Can view Export Dashboard"),
    ("edc_dashboard.view_screening_listboard", "Can view Screening listboard"),
    ("edc_dashboard.view_subject_listboard", "Can view Subject listboard"),
    ("edc_dashboard.view_tmg_listboard", "Can view TMG Listboard"),
]


def add_edc_dashboard_permissions(auth_updater):
    auth_updater.create_permissions_from_tuples(
        model="edc_dashboard.dashboard", codename_tuples=dashboard_tuples
    )


def remove_permissions_to_edc_dashboard_model(auth_updater):
    for group in auth_updater.group_model_cls.objects.all():
        auth_updater.remove_permissions_by_codenames(
            group=group,
            codenames=[
                "edc_dashboard.add_dashboard",
                "edc_dashboard.change_dashboard",
                "edc_dashboard.delete_dashboard",
                "edc_dashboard.view_dashboard",
            ],
        )
