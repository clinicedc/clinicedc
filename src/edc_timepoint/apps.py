import sys

from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings
from edc_appointment.constants import COMPLETE_APPT

from .timepoint import Timepoint
from .timepoint_collection import TimepointCollection


class AppConfig(DjangoAppConfig):
    name = "edc_timepoint"
    verbose_name = "Edc Timepoint"

    timepoints = TimepointCollection(
        timepoints=[
            Timepoint(
                model="edc_appointment.appointment",
                datetime_field="appt_datetime",
                status_field="appt_status",
                closed_status=COMPLETE_APPT,
            ),
            Timepoint(
                model="edc_appointment.appointment",
                datetime_field="appt_datetime",
                status_field="appt_status",
                closed_status=COMPLETE_APPT,
            ),
        ]
    )

    def ready(self):
        sys.stdout.write(f"Loading {self.verbose_name} ...\n")
        for model in self.timepoints:
            sys.stdout.write(f" * '{model}' is a timepoint model.\n")
        sys.stdout.write(f" Done loading {self.verbose_name}.\n")


if settings.APP_NAME == "edc_timepoint":
    from dateutil.relativedelta import FR, MO, SA, SU, TH, TU, WE
    from edc_facility.apps import AppConfig as BaseEdcFacilityAppConfig

    class EdcFacilityAppConfig(BaseEdcFacilityAppConfig):
        definitions = {
            "7-day-clinic": dict(
                days=[MO, TU, WE, TH, FR, SA, SU],
                slots=[100, 100, 100, 100, 100, 100, 100],
            ),
            "5-day-clinic": dict(days=[MO, TU, WE, TH, FR], slots=[100, 100, 100, 100, 100]),
            "3-day-clinic": dict(
                days=[TU, WE, TH],
                slots=[100, 100, 100],
                best_effort_available_datetime=True,
            ),
        }
