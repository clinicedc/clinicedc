from django.apps import AppConfig as DjangoAppConfig
from django.core.checks.registry import register
from django.core.management.color import color_style

from .system_checks import context_processors_check

style = color_style()


class AppConfig(DjangoAppConfig):
    name = "edc_visit_tracking"
    verbose_name = "Edc Visit Tracking"
    report_datetime_allowance: int = 30
    allow_crf_report_datetime_before_visit: bool = False
    reason_field: dict = {}  # noqa: RUF012

    def ready(self):
        register(context_processors_check)
