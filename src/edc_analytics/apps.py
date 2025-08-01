from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_analytics"
    verbose_name = "Edc Analytics"
    has_exportable_data = False
    include_in_administration_section = False
