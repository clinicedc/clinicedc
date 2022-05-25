from datetime import datetime
from typing import Any

from django.conf import settings
from edc_utils import convert_php_dateformat
from edc_visit_schedule.schedule.window import (
    ScheduledVisitWindowError,
    UnScheduledVisitWindowError,
)

UNSCHEDULED_WINDOW_ERROR = "unscheduled_window_error"
SCHEDULED_WINDOW_ERROR = "scheduled_window_error"


class WindowPeriodFormValidatorMixin:
    def validate_appt_datetime_in_window_period(self: Any, appointment, *args) -> None:
        # if not appointment.is_baseline_appt:
        self.datetime_in_window_or_raise(appointment, *args)

    def validate_visit_datetime_in_window_period(self: Any, *args) -> None:
        self.datetime_in_window_or_raise(*args)

    def validate_crf_datetime_in_window_period(self: Any, *args) -> None:
        self.datetime_in_window_or_raise(*args)

    def datetime_in_window_or_raise(
        self,
        appointment: Any,
        proposed_datetime: datetime,
        form_field: str,
    ):
        if proposed_datetime:
            datestring = convert_php_dateformat(settings.SHORT_DATE_FORMAT)
            appointment.visit_from_schedule.timepoint_datetime = appointment.timepoint_datetime
            lower = appointment.visit_from_schedule.dates.lower.strftime(datestring)
            try:
                appointment.schedule.datetime_in_window(
                    timepoint_datetime=appointment.timepoint_datetime,
                    dt=proposed_datetime,
                    visit_code=appointment.visit_code,
                    visit_code_sequence=appointment.visit_code_sequence,
                    baseline_timepoint_datetime=self.baseline_timepoint_datetime(appointment),
                )
            except UnScheduledVisitWindowError as e:
                upper = appointment.schedule.visits.next(
                    appointment.visit_code
                ).dates.lower.strftime(datestring)
                self.raise_validation_error(
                    {
                        form_field: (
                            f"Invalid. Expected a date between {lower} and {upper} (U). "
                            f"Got {e}"
                        )
                    },
                    UNSCHEDULED_WINDOW_ERROR,
                )
            except ScheduledVisitWindowError:
                upper = appointment.visit_from_schedule.dates.upper.strftime(datestring)
                self.raise_validation_error(
                    {form_field: f"Invalid. Expected a date between {lower} and {upper} (S)."},
                    SCHEDULED_WINDOW_ERROR,
                )

    @staticmethod
    def baseline_timepoint_datetime(appointment) -> datetime:
        return appointment.__class__.objects.first_appointment(
            subject_identifier=appointment.subject_identifier,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
        ).timepoint_datetime
