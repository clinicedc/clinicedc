from django.apps import AppConfig as DjangoApponfig
from django.core.management import color_style

style = color_style()


class AppConfig(DjangoApponfig):
    name = "edc_pdutils"
    verbose_name = "Edc Pandas Utilities"
    include_in_administration_section = False
