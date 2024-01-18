import os
import sys

from django.apps import AppConfig as DjangoApponfig
from django.core.management import color_style

from edc_export.utils import get_export_folder, get_upload_folder

style = color_style()


class AppConfig(DjangoApponfig):
    name = "edc_export"
    verbose_name = "Edc Export"
    include_in_administration_section = True
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        if not os.path.exists(get_export_folder()):
            sys.stdout.write(
                style.ERROR(
                    f"Export folder does not exist. Tried {get_export_folder()}. "
                    f"See {self.name}.\n"
                )
            )
        if not os.path.exists(get_upload_folder()):
            sys.stdout.write(
                style.ERROR(
                    f"Export folder does not exist. Tried {get_upload_folder()}. "
                    f"See {self.name}.\n"
                )
            )
