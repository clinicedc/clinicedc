import sys

from django.apps import AppConfig as DjangoAppConfig

from .site_prn_forms import site_prn_forms


class AppConfig(DjangoAppConfig):
    name = "edc_prn"
    verbose_name = "Edc PRN"

    def ready(self):
        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        site_prn_forms.autodiscover()
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
