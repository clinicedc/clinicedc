from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_utils"
    verbose_name = "Edc Utils"
    has_exportable_data = False
    include_in_administration_section = False
