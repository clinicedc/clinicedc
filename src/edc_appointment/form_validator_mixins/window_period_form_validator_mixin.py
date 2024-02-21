from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from dateutil.relativedelta import relativedelta
from django.utils.translation import gettext as _
from edc_utils import formatted_date, to_utc
from edc_utils.date import floor_secs
from edc_visit_schedule.exceptions import (
    ScheduledVisitWindowError,
    UnScheduledVisitWindowError,
)
from edc_visit_schedule.utils import get_lower_datetime

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
            try:
                appointment.schedule.datetime_in_window(
                    timepoint_datetime=appointment.timepoint_datetime,
                    dt=proposed_appt_datetime,
                    visit_code=appointment.visit_code,
                    visit_code_sequence=appointment.visit_code_sequence,
                    baseline_timepoint_datetime=self.baseline_timepoint_datetime(appointment),
                )
            except UnScheduledVisitWindowError:
                if not self.ignore_window_period_for_unscheduled(
                    appointment, proposed_appt_datetime
                ):
                    # TODO: fix the dates on this message to match e.message
                    lower = floor_secs(get_lower_datetime(appointment))
                    try:
                        # one day less than the next related_visit, if it exists
                        upper = floor_secs(
                            appointment.next.related_visit.report_datetime
                            - relativedelta(days=1)
                        )
                    except AttributeError:
                        # lower bound of next appointment
                        upper = floor_secs(get_lower_datetime(appointment.next))
                    dt_lower = formatted_date(lower)
                    dt_upper = formatted_date(upper)
                    self.raise_validation_error(
                        {
                            form_field: (
                                _(
                                    "Invalid. Expected a date between "
                                    "%(dt_lower)s and %(dt_upper)s (U)."
                                )
                                % dict(dt_lower=dt_lower, dt_upper=dt_upper)
                            )
                        },
                        UNSCHEDULED_WINDOW_ERROR,
                    )
            except ScheduledVisitWindowError as e:
                self.raise_validation_error({form_field: (str(e))}, SCHEDULED_WINDOW_ERROR)

    @staticmethod
    def baseline_timepoint_datetime(appointment: Appointment) -> datetime:
        return appointment.__class__.objects.first_appointment(
            subject_identifier=appointment.subject_identifier,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
        ).timepoint_datetime
