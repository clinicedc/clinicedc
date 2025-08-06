from django.apps import AppConfig as DjangoApponfig
from django.core.management import color_style

style = color_style()


class AppConfig(DjangoApponfig):
    name = "edc_export"
    verbose_name = "Edc Export"
    include_in_administration_section = True
    default_auto_field = "django.db.models.BigAutoField"
