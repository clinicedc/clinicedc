from django.apps import AppConfig as DjangoApponfig
from django.core.management import color_style

style = color_style()


class AppConfig(DjangoApponfig):
    name = "edc_model_to_dataframe"
    verbose_name = "Edc model to pandas dataframe"
    include_in_administration_section = False
