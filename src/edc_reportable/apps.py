import sys

from django.apps import AppConfig as BaseAppConfig

from .site_reportables import site_reportables


class AppConfig(BaseAppConfig):
    name = "edc_reportable"

    def ready(self):
        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        site_reportables.autodiscover()
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
