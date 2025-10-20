from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style

style = color_style()


class AppConfig(DjangoAppConfig):
    name = "edc_navbar"
    verbose_name = "Edc Navbar"
    register_default_navbar = True
