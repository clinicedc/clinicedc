import sys

from django.apps import AppConfig as DjangoAppConfig

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
