from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = "edc_view_utils"
    verbose_name = "Edc View Utils"
    has_exportable_data = False
    include_in_administration_section = False
