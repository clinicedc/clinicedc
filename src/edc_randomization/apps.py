import os
from warnings import warn

from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings
from django.core.checks.registry import register

from .system_checks import randomizationlist_check


class AppConfig(DjangoAppConfig):
    name = "edc_randomization"
    verbose_name = "Edc Randomization"
    has_exportable_data = True
    include_in_administration_section = True

    def ready(self):
        register(randomizationlist_check, deploy=True)

    @property
    def randomization_list_path(self):
        warn(
            "Use of settings.RANDOMIZATION_LIST_PATH has been deprecated. "
            "See site_randomizers in edc_randomization"
        )
        return os.path.join(settings.RANDOMIZATION_LIST_PATH)
