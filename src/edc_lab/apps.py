from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style

style = color_style()


class AppConfig(DjangoAppConfig):
    name = "edc_lab"
    verbose_name = "Edc Lab"
    has_exportable_data = True
    include_in_administration_section = True
    result_model = "edc_lab.result"
