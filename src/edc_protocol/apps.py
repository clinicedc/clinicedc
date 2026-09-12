import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.checks import register
from django.core.management.color import color_style

from .system_checks import middleware_check
from .trial_dates import TrialDates
from .trial_settings import trial_settings

style = color_style()


class AppConfig(DjangoAppConfig):
    name = "edc_protocol"
    verbose_name = "Edc Protocol"
    include_in_administration_section = True
    messages_written = False

    def ready(self):
        register(middleware_check)
        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        sys.stdout.write(f" * {trial_settings.protocol}: {trial_settings.protocol_name}.\n")
        open_date = TrialDates().study_open_datetime.strftime("%Y-%m-%d")
        sys.stdout.write(f" * Study opening date: {open_date}\n")
        close_date = TrialDates().study_close_datetime.strftime("%Y-%m-%d")
        sys.stdout.write(f" * Expected study closing date: {close_date}\n")
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
        sys.stdout.flush()
        self.messages_written = True
