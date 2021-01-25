import sys

from dateutil.relativedelta import MO, TU, WE, TH, FR, SA, SU
from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings
from django.core.checks.registry import register
from django.core.management.color import color_style
from warnings import warn

from .facility import Facility, FacilityError
from .system_checks import holiday_path_check, holiday_country_check

style = color_style()


class AppConfig(DjangoAppConfig):
    _holidays = {}
    name = "edc_facility"
    verbose_name = "Edc Facility"
    include_in_administration_section = True

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
        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        # if "runtests.py" not in sys.argv and "test" not in sys.argv:
        if "migrate" not in sys.argv and "showmigrations" not in sys.argv:
            register(holiday_path_check, deploy=True)
            register(holiday_country_check, deploy=True)
        else:
            sys.stdout.write(
                style.NOTICE(" * not registering system checks for migrations.\n")
            )
        for facility in self.facilities.values():
            sys.stdout.write(f" * {facility}.\n")
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")

    @property
    def facilities(self):
        """Returns a dictionary of facilities.
        """
        if not self.definitions:
            try:
                warn_user = not settings.EDC_FACILITY_USE_DEFAULTS
            except AttributeError:
                warn_user = True
            if warn_user:
                warn(
                    f"Facility definitions not defined. See {self.name} "
                    "app_config.definitions. Using defaults. "
                    "To silence, set EDC_FACILITY_USE_DEFAULTS=True in settings."
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
