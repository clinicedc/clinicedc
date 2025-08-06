from django.apps import AppConfig as DjangoAppConfig
from django.core.checks.registry import register
from django.core.management.color import color_style

from .system_checks import edc_notification_check

style = color_style()


class AppConfig(DjangoAppConfig):
    name = "edc_notification"
    verbose_name = "Edc Notification"
    include_in_administration_section = True

    def ready(self):
        register(edc_notification_check)
