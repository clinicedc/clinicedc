import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style

style = color_style()


class AppConfig(DjangoAppConfig):
    name = 'edc_navbar'
    verbose_name = 'Edc Navbar'

    def ready(self):
        from .site_navbars import site_navbars
        sys.stdout.write(f'Loading {self.verbose_name} ...\n')
        site_navbars.autodiscover()
        sys.stdout.write(f' Done loading {self.verbose_name}.\n')
