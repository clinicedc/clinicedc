import sys

from dateutil.relativedelta import MO, TU, WE, TH, FR
from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings
from django.core.checks.registry import register
from django.core.management.color import color_style

from .facility import Facility, FacilityError
from .system_checks import holiday_check

style = color_style()


class AppConfig(DjangoAppConfig):
    _holidays = {}
    name = "edc_facility"
    verbose_name = "Edc Facility"

    # only set if for edc_facility tests, etc
    if settings.APP_NAME == "edc_facility":
        definitions = {
            "5-day-clinic": dict(
                days=[MO, TU, WE, TH, FR], slots=[100, 100, 100, 100, 100]
            )
        }
    else:
        definitions = None

    def ready(self):
        register(holiday_check)
        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        for facility in self.facilities.values():
            sys.stdout.write(f" * {facility}.\n")
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")

    @property
    def facilities(self):
        """Returns a dictionary of facilities.
        """
        if not self.definitions:
            raise FacilityError(
                f"Facility definitions not defined. See {self.name} app_config.definitions"
            )
        return {k: Facility(name=k, **v) for k, v in self.definitions.items()}

    def get_facility(self, name=None):
        """Returns a facility instance for this name
        if it exists.
        """
        facility = self.facilities.get(name)
        if not facility:
            raise FacilityError(
                f"Facility '{name}' does not exist. Expected one "
                f"of {self.facilities}. See {repr(self)}.definitions"
            )
        return facility
