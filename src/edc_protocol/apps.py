import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style

from .protocol import Protocol

style = color_style()


class AppConfig(DjangoAppConfig):
    name = "edc_protocol"
    verbose_name = "Edc Protocol"
    include_in_administration_section = True
    messages_written = False

    def ready(self):
        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        protocol = Protocol()
        sys.stdout.write(f" * {protocol.protocol}: {protocol.protocol_name}.\n")
        open_date = protocol.study_open_datetime.strftime("%Y-%m-%d %Z")
        sys.stdout.write(f" * Study opening date: {open_date}\n")
        close_date = protocol.study_close_datetime.strftime("%Y-%m-%d %Z")
        sys.stdout.write(f" * Expected study closing date: {close_date}\n")
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
        sys.stdout.flush()
        self.messages_written = True
