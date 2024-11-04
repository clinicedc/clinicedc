from django.apps.config import AppConfig as DjangoAppConfig
from django.core.management.color import color_style

style = color_style()


class AppConfig(DjangoAppConfig):
    name = "edc_visit_schedule"
    verbose_name = "Edc Visit Schedules"
    validate_models = True
    include_in_administration_section = True
