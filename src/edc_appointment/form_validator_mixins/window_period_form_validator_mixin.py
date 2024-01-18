from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from django.conf import settings
from edc_utils import convert_php_dateformat, to_utc
from edc_utils.date import ceil_datetime, floor_secs
from edc_visit_schedule.exceptions import (
    ScheduledVisitWindowError,
    UnScheduledVisitWindowError,
)
from edc_visit_schedule.utils import get_lower_datetime, get_upper_datetime

from ..constants import COMPLETE_APPT, INCOMPLETE_APPT

if TYPE_CHECKING:
    from edc_appointment.models import Appointment

UNSCHEDULED_WINDOW_ERROR = "unscheduled_window_error"
SCHEDULED_WINDOW_ERROR = "scheduled_window_error"


class WindowPeriodFormValidatorMixin:
    def validate_appt_datetime_in_window_period(self, appointment: Appointment, *args) -> None:
        self.datetime_in_window_or_raise(appointment, *args)

    @staticmethod
    def ignore_window_period_for_unscheduled(
        appointment: Appointment, proposed_appt_datetime: datetime
    ) -> bool:
        """Returns True if this is an unscheduled appt"""
        value = False
        if (
            appointment
            and appointment.visit_code_sequence > 0
            and appointment.next
            and appointment.next.appt_status in [INCOMPLETE_APPT, COMPLETE_APPT]
            and to_utc(proposed_appt_datetime) < appointment.next.appt_datetime
        ):
            value = True
        return value

    def datetime_in_window_or_raise(
        self,
        appointment: Appointment,
        proposed_appt_datetime: datetime,
        form_field: str,
    ):
        if proposed_appt_datetime:
            datetimestring = convert_php_dateformat(settings.SHORT_DATETIME_FORMAT)
            try:
                appointment.schedule.datetime_in_window(
                    timepoint_datetime=appointment.timepoint_datetime,
                    dt=proposed_appt_datetime,
                    visit_code=appointment.visit_code,
                    visit_code_sequence=appointment.visit_code_sequence,
                    baseline_timepoint_datetime=self.baseline_timepoint_datetime(appointment),
                )
            except UnScheduledVisitWindowError as e:
                if not self.ignore_window_period_for_unscheduled(
                    appointment, proposed_appt_datetime
                ):
                    # TODO: fix the dates on this message to match e.message
                    lower = floor_secs(get_lower_datetime(appointment)).strftime(
                        datetimestring
                    )
                    upper = floor_secs(get_lower_datetime(appointment.next)).strftime(
                        datetimestring
                    )
                    self.raise_validation_error(
                        {
                            form_field: (
                                "Invalid. Expected a date/time between "
                                f"{lower} and {upper} (U). Got {e}."
                            )
                        },
                        UNSCHEDULED_WINDOW_ERROR,
                    )
            except ScheduledVisitWindowError:
                lower = floor_secs(get_lower_datetime(appointment)).strftime(datetimestring)
                upper = floor_secs(ceil_datetime(get_upper_datetime(appointment))).strftime(
                    datetimestring
                )
                proposed = floor_secs(proposed_appt_datetime).strftime(datetimestring)
                # TODO: check this is correctly limiting (e.g. requistions)
                self.raise_validation_error(
                    {
                        form_field: (
                            f"Invalid. Expected a date/time between {lower} and {upper} (S). "
                            f"Got {proposed}."
                        )
                    },
                    SCHEDULED_WINDOW_ERROR,
                )

    @staticmethod
    def baseline_timepoint_datetime(appointment: Appointment) -> datetime:
        return appointment.__class__.objects.first_appointment(
            subject_identifier=appointment.subject_identifier,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
        ).timepoint_datetime
