import sys

from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management.color import color_style
from django.db.backends.signals import connection_created
from edc_utils.sqlite import activate_foreign_keys

style = color_style()


class AppConfig(DjangoAppConfig):
    name = "edc_model"
    verbose_name = "Edc Model"

    def ready(self):
        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        connection_created.connect(activate_foreign_keys)
        sys.stdout.write(f" * default TIME_ZONE {settings.TIME_ZONE}.\n")
        if not settings.USE_TZ:
            raise ImproperlyConfigured("EDC requires settings.USE_TZ = True")
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
