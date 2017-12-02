import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style

from .site_list_data import site_list_data


style = color_style()


class AppConfig(DjangoAppConfig):
    name = 'edc_list_data'
    verbose_name = 'Edc List Data'

    def ready(self):

        sys.stdout.write(f'Loading {self.verbose_name} ...\n')
        site_list_data.autodiscover()
        sys.stdout.write(f' Done loading {self.verbose_name}.\n')
