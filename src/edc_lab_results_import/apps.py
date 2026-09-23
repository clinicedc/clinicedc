from django.apps import AppConfig as DjangoAppConfig
from django.core.checks.registry import register

from .system_checks import (
    storage_dir_check,
    upload_and_storage_dirs_check,
    upload_dir_check,
)


class AppConfig(DjangoAppConfig):
    name = "edc_lab_results_import"
    verbose_name = "Edc Lab Results (Imported)"
    has_exportable_data = True
    include_in_administration_section = True

    def ready(self) -> None:
        register(storage_dir_check)
        register(upload_dir_check)
        register(upload_and_storage_dirs_check)
