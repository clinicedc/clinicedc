from django.apps import AppConfig as DjangoAppConfig
from django.core.checks.registry import register

from .system_checks import upload_dir_check


class AppConfig(DjangoAppConfig):
    name = "edc_lab_results"
    verbose_name = "Edc Lab Results"
    has_exportable_data = True
    include_in_administration_section = True

    def ready(self) -> None:
        register(upload_dir_check)
