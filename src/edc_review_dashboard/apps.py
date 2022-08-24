from django.apps import AppConfig as DjangoAppConfig
from django.core.checks.registry import register

from .system_checks import middleware_check


class AppConfig(DjangoAppConfig):
    name = "edc_review_dashboard"

    def ready(self):
        register(middleware_check)
