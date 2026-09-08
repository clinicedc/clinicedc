from django.apps import AppConfig as DjangoAppConfig
from django.core.checks.registry import register
from django.core.signals import setting_changed

from .system_checks import result_model_panel_check
from .utils import clear_result_model_cache


class AppConfig(DjangoAppConfig):
    name = "edc_lab_results"
    verbose_name = "Edc Lab Results"
    has_exportable_data = False
    include_in_administration_section = False

    def ready(self) -> None:
        register(result_model_panel_check)
        setting_changed.connect(clear_result_model_cache)
