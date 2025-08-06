import sys

from django.apps import AppConfig as DjangoAppConfig
from django.core.checks.registry import register
from django.core.management.color import color_style

from .system_checks import holiday_country_check, holiday_path_check
from .utils import get_facilities

style = color_style()


class AppConfig(DjangoAppConfig):
    _holidays = {}
    name = "edc_facility"
    verbose_name = "Edc Facility"
    include_in_administration_section = True

    def ready(self):
        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        if "migrate" not in sys.argv and "showmigrations" not in sys.argv:
            register(holiday_path_check, deploy=True)
            register(holiday_country_check, deploy=True)
        else:
            sys.stdout.write(
                style.NOTICE(" * not registering system checks for migrations.\n")
            )
        for facility in get_facilities().values():
            sys.stdout.write(f" * {facility}.\n")
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")
