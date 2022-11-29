from django.apps import AppConfig as DjangoApponfig


class AppConfig(DjangoApponfig):
    name = "edc_rx"
    verbose_name = "Edc RX"
    include_in_administration_section = False
    has_exportable_data = False
    default_auto_field = "django.db.models.BigAutoField"
