import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.checks.registry import register

from .system_checks import context_processors_check


class AppConfig(DjangoAppConfig):
    _holidays: dict = {}
    name = "edc_appointment"
    verbose_name = "Appointments"
    has_exportable_data = True
    include_in_administration_section = True

    def ready(self):
        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        register(context_processors_check)
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
