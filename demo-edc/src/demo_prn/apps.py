from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "demo_prn"
    verbose_name = "DEMO: PRN"
    include_in_administration_section = True
    has_exportable_data = True
