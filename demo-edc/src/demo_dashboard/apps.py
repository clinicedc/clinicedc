from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "demo_dashboard"
    verbose_name = "DEMO: Dashboard"
    include_in_administration_section = False
    has_exportable_data = False
