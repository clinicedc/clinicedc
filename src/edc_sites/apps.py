from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style

style = color_style()


class AppConfig(DjangoAppConfig):
    name = "edc_sites"
    verbose_name = "Edc Sites"
    has_exportable_data = True
    default_auto_field = "django.db.models.BigAutoField"
    include_in_administration_section = True
