import sys

from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings
from django.core.management.color import color_style

style = color_style()


class AppConfig(DjangoAppConfig):
    name = "edc_navbar"
    verbose_name = "Edc Navbar"
    register_default_navbar = True

    def ready(self):
        from .site_navbars import site_navbars

        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        site_navbars.autodiscover()
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")

    @property
    def default_navbar_name(self):
        try:
            return settings.DEFAULT_NAVBAR_NAME
        except AttributeError:
            return "default"
