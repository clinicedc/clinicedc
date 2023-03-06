import os
import sys

from django.apps import AppConfig as DjangoApponfig
from django.core.management import color_style

from edc_pdutils.site_values_mappings import site_values_mappings

from .utils import get_export_folder

style = color_style()


class AppConfig(DjangoApponfig):
    name = "edc_pdutils"
    verbose_name = "Edc Pandas Utilities"
    include_in_administration_section = False

    def ready(
        self,
    ):
        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        if not os.path.exists(get_export_folder()):
            sys.stdout.write(
                style.ERROR(
                    f"Export folder does not exist. Tried {get_export_folder()}. "
                    f"See {self.name}.\n"
                )
            )

        site_values_mappings.autodiscover()
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
