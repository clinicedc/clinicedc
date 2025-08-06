from django.apps import AppConfig as DjangoApponfig


class AppConfig(DjangoApponfig):
    name = "edc_refusal"
    verbose_name = "Edc Refusal"
    include_in_administration_section = False
    has_exportable_data = True
    default_auto_field = "django.db.models.BigAutoField"
