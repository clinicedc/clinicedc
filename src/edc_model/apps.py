import sys

from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings
from django.db.backends.signals import connection_created
from django.core.management.color import color_style
from django.core.exceptions import ImproperlyConfigured


style = color_style()


def activate_foreign_keys(sender, connection, **kwargs):
    """Enable integrity constraint with sqlite.
    """
    if connection.vendor == "sqlite":
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")


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
