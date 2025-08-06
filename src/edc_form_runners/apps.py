from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_form_runners"
    verbose_name = "Edc Form Runners"
    description = ""
    admin_site_name = "edc_form_runners_admin"
    include_in_administration_section = True
    has_exportable_data = True
    default_auto_field = "django.db.models.BigAutoField"
