from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_lab_results"
    verbose_name = "Edc Lab Results"
    has_exportable_data = False
    include_in_administration_section = False
