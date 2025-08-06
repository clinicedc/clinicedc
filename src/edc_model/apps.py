import sys

from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings
from django.core.checks import register
from django.core.management.color import color_style
from django.db.backends.signals import connection_created

from edc_utils.sqlite import activate_foreign_keys

from .system_checks import check_for_edc_model

style = color_style()


class AppConfig(DjangoAppConfig):
    name = "edc_model"
    verbose_name = "Edc Model"

    def ready(self):
        register(check_for_edc_model)
        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        connection_created.connect(activate_foreign_keys)
        sys.stdout.write(f" * default TIME_ZONE {settings.TIME_ZONE}.\n")
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
