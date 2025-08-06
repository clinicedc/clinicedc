from django.apps.config import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_model_form"
    verbose_name = "Edc Model Form"
    has_exportable_data = False
    include_in_administration_section = False
