from django.apps.config import AppConfig as DjangoAppConfig
from django.core.management.color import color_style

style = color_style()


class AppConfig(DjangoAppConfig):
    name = "edc_metadata"
    verbose_name = "Data Collection Status"
    metadata_rules_enabled = True
    has_exportable_data = True
    include_in_administration_section = True
