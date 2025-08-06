from django.apps import AppConfig as DjangoAppConfig
from django.core.checks.registry import register

from .system_checks import middleware_check


class AppConfig(DjangoAppConfig):
    name = "edc_dashboard"

    listboard_template_name = None
    include_in_administration_section = False

    def ready(self):
        register(middleware_check)
