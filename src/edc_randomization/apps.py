import os
import sys
from warnings import warn

from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings
from django.core.checks.registry import register

from .site_randomizers import site_randomizers
from .system_checks import randomizationlist_check


class AppConfig(DjangoAppConfig):
    name = "edc_randomization"
    verbose_name = "Edc Randomization"
    has_exportable_data = True
    include_in_administration_section = True

    def ready(self):
        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        site_randomizers.autodiscover()
        register(randomizationlist_check, deploy=True)
        sys.stdout.write(f" Done loading {self.verbose_name} ...\n")

    @property
    def randomization_list_path(self):
        warn(
            "Use of settings.RANDOMIZATION_LIST_PATH has been deprecated. "
            "See site_randomizers in edc_randomization"
        )
        return os.path.join(settings.RANDOMIZATION_LIST_PATH)
