import sys

from django.apps import AppConfig as DjangoAppConfig
from django.apps import apps as django_apps


class AppConfig(DjangoAppConfig):
    name = "edc_registration"
    verbose_name = "Edc Registration"
    app_label = "edc_registration"
    has_exportable_data = True
    include_in_administration_section = True

    def ready(self):
        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        sys.stdout.write(f"  * using {self.app_label}.registeredsubject\n")
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")

    @property
    def model(self):
        return django_apps.get_model(self.app_label, "registeredsubject")
