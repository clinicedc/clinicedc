import sys

from django.apps.config import AppConfig as DjangoAppConfig
from django.core.management.color import color_style

from .metadata_rules import site_metadata_rules

style = color_style()


class AppConfig(DjangoAppConfig):
    name = "edc_metadata"
    verbose_name = "Data collection status"
    metadata_rules_enabled = True
    has_exportable_data = True
    include_in_administration_section = True

    def ready(self):
        sys.stdout.write(f"Loading {self.name} ...\n")
        site_metadata_rules.autodiscover()
        if not site_metadata_rules.registry:
            sys.stdout.write(
                style.ERROR(" Warning. No metadata rules were loaded by autodiscover.\n")
            )
        if not self.metadata_rules_enabled:
            sys.stdout.write(style.NOTICE(" * metadata rules disabled!\n"))
        sys.stdout.write(f" Done loading {self.name}.\n")
