from django.apps import AppConfig as DjangoAppConfig

# from edc_auth.default_role_names import CLINICIAN_ROLE
# from edc_auth.update_roles import update_roles

# def post_migrate_user_roles(sender=None, **kwargs):  # noqa
#     """Update Role model with EDC defaults.
#
#     To add custom roles, register this in your main
#     app with additional role_names and groups_by_role_name.
#     """
#     update_roles(groups_by_role_name=groups_by_role_name, role_names=role_names, verbose=True)


class AppConfig(DjangoAppConfig):
    name = "edc_unblinding"
    verbose_name = "Edc Unblinding"
    has_exportable_data = True
    include_in_administration_section = True
