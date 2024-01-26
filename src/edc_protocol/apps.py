import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.checks import register
from django.core.management.color import color_style

from .research_protocol_config import ResearchProtocolConfig
from .system_checks import middleware_check

style = color_style()


class AppConfig(DjangoAppConfig):
    name = "edc_protocol"
    verbose_name = "Edc Protocol"
    include_in_administration_section = True
    messages_written = False

    def ready(self):
        register(middleware_check)
        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        protocol = ResearchProtocolConfig()
        sys.stdout.write(f" * {protocol.protocol}: {protocol.protocol_name}.\n")
        open_date = protocol.study_open_datetime.strftime("%Y-%m-%d %Z")
        sys.stdout.write(f" * Study opening date: {open_date}\n")
        close_date = protocol.study_close_datetime.strftime("%Y-%m-%d %Z")
        sys.stdout.write(f" * Expected study closing date: {close_date}\n")
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
        sys.stdout.flush()
        self.messages_written = True
