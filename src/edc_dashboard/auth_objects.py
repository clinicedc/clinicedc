dashboard_tuples = [
    ("edc_dashboard.view_enrolment_listboard", "Can view Enrolment listboard"),
    ("edc_dashboard.view_export_dashboard", "Can view Export Dashboard"),
]


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
