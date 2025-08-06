from django.apps import AppConfig as DjangoApponfig
from django.core.management.color import color_style

style = color_style()


class AppConfig(DjangoApponfig):
    name = "edc_action_item"
    verbose_name = "Action Items"
    has_exportable_data = True
    include_in_administration_section = True
