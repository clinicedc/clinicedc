import os
import sys

from django.apps import AppConfig as DjangoApponfig
from django.core.management import color_style
from edc_export.utils import get_export_folder

style = color_style()


class AppConfig(DjangoApponfig):
    name = "edc_pdutils"
    verbose_name = "Edc Pandas Utilities"
    include_in_administration_section = False

    def ready(self):
        if not os.path.exists(get_export_folder()):
            sys.stdout.write(
                style.ERROR(
                    f"Export folder does not exist. Tried {get_export_folder()}. "
                    f"See {self.name}.\n"
                )
            )
