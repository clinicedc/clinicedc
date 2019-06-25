import sys

from dateutil.relativedelta import MO, TU, WE, TH, FR, SA, SU
from django.apps import AppConfig as DjangoAppConfig
from django.core.checks.registry import register
from django.core.management.color import color_style

from .facility import Facility, FacilityError
from .system_checks import holiday_check
from _warnings import warn
from django.conf import settings

style = color_style()


class AppConfig(DjangoAppConfig):
    _holidays = {}
    name = "edc_facility"
    verbose_name = "Edc Facility"
    include_in_administration_section = False

    definitions = None

    default_definitions = {
        "7-day-clinic": dict(
            days=[MO, TU, WE, TH, FR, SA, SU], slots=[100, 100, 100, 100, 100, 100, 100]
        ),
        "5-day-clinic": dict(
            days=[MO, TU, WE, TH, FR], slots=[100, 100, 100, 100, 100]
        ),
        "3-day-clinic": dict(
            days=[TU, WE, TH],
            slots=[100, 100, 100],
            best_effort_available_datetime=True,
        ),
    }

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
            try:
                warn_user = not settings.USE_EDC_FACILITY_DEFAULTS
            except AttributeError:
                warn_user = True
            if warn_user:
                warn(
                    f"Facility definitions not defined. See {self.name} "
                    f"app_config.definitions. Using defaults. "
                    "To silence, set USE_EDC_FACILITY_DEFAULTS=True in settings."
                )
        return {
            k: Facility(name=k, **v)
            for k, v in (self.definitions or self.default_definitions).items()
        }

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
