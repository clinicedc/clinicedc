from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.utils.translation import gettext as _

from edc_utils import (
    ceil_secs,
    convert_php_dateformat,
    floor_secs,
    formatted_date,
    to_local,
)

from ..exceptions import (
    ScheduledVisitWindowError,
    UnScheduledVisitWindowError,
)
from ..utils import get_enforce_window_period_enabled


class Window:
    def __init__(
        self,
        name=None,
        dt=None,
        baseline_timepoint_datetime=None,
        timepoint_datetime=None,
        visit=None,
        next_visit=None,
        visit_code_sequence=None,
    ):
        self.name = name

        # convert dates to local tzinfo
        self.dt = to_local(dt)
        self.timepoint_datetime = to_local(timepoint_datetime)
        self.baseline_timepoint_datetime = to_local(baseline_timepoint_datetime)

        self.visit = visit
        self.visit.timepoint_datetime = self.timepoint_datetime

        self.next_visit = next_visit
        if self.next_visit:
            self.next_visit.timepoint_datetime = (
                self.baseline_timepoint_datetime + self.next_visit.rbase
            )

        self.visit_code_sequence = visit_code_sequence

    @property
    def datetime_in_window(self):
        if get_enforce_window_period_enabled():
            if not self.dt:
                raise UnScheduledVisitWindowError("Invalid datetime")
            if self.is_scheduled_visit:
                self.raise_for_scheduled_not_in_window()
            else:
                self.raise_for_unscheduled_not_in_window()
        return True

    @property
    def is_scheduled_visit(self):
        return self.visit_code_sequence == 0 or self.visit_code_sequence is None

    def get_window_gap_days(self) -> int:
        days = 0
        if self.visit.add_window_gap_to_lower and self.next_visit:
            days = abs(
                (self.timepoint_datetime + self.visit.rupper)
                - (self.timepoint_datetime - self.next_visit.rlower)
            ).days
        return days

    def raise_for_scheduled_not_in_window(self):
        """Returns the datetime if it falls within the
        window period for a scheduled `visit` otherwise
        raises an exception.

        In this case, `visit` is the object from schedule and
        not a model instance.
        """

        gap_days = self.get_window_gap_days()
        lower = floor_secs(to_local(self.visit.dates.lower) - relativedelta(days=gap_days))
        upper = ceil_secs(to_local(self.visit.dates.upper))
        if not (lower <= floor_secs(to_local(self.dt)) <= upper):
            lower_date = to_local(lower).strftime(
                convert_php_dateformat(settings.SHORT_DATETIME_FORMAT)
            )
            upper_date = to_local(upper).strftime(
                convert_php_dateformat(settings.SHORT_DATETIME_FORMAT)
            )
            dt = to_local(self.dt).strftime(
                convert_php_dateformat(settings.SHORT_DATETIME_FORMAT)
            )

            raise ScheduledVisitWindowError(
                "Invalid. Date falls outside of the "
                f"window period for this `scheduled` visit. "
                f"Expected a date between {lower_date} "
                f"and {upper_date} for {self.visit.code}. Got `{dt}`."
            )

    def raise_for_unscheduled_not_in_window(self):
        """Returns the datetime if it falls within the
        window period for an unscheduled `visit` otherwise
        raises an exception.

        Window period for an unscheduled date is anytime
        on or after the scheduled date and before the projected
        lower bound of the next visit.

        In this case, `visit` is the object from schedule and
        not a model instance.
        """
        formatted_dt = formatted_date(self.dt)
        if self.next_visit:
            in_window = floor_secs(to_local(self.dt)) < floor_secs(
                to_local(self.next_visit.timepoint_datetime - self.next_visit.rlower)
            )
            msg = _(
                "Invalid datetime. Falls outside of the "
                "window period for this `unscheduled` visit. "
                "Expected a datetime before the next visit. "
                "Next visit is `%(next_visit_code)s` expected any time "
                "from `%(dt_lower)s`."
                "Got `%(visit_code)s`@`%(dt)s`. "
            ) % dict(
                next_visit_code=self.next_visit.code,
                dt_lower=formatted_date(
                    self.next_visit.timepoint_datetime - self.next_visit.rlower
                ),
                visit_code=self.visit.code,
                dt=formatted_dt,
            )
        else:
            in_window = floor_secs(to_local(self.dt)) < floor_secs(
                to_local(
                    self.visit.timepoint_datetime
                    + (self.visit.rupper_extended or self.visit.rupper)
                )
            )
            msg = _(
                "Invalid datetime. Falls outside of the "
                "window period for this `unscheduled` visit. "
                "Expected a datetime before `%(dt_upper)s`."
                "Got `%(visit_code)s`@`%(dt)s`. "
            ) % dict(
                dt_upper=formatted_date(
                    to_local(
                        self.visit.timepoint_datetime
                        + (self.visit.rupper_extended or self.visit.rupper)
                    )
                ),
                visit_code=self.visit.code,
                dt=formatted_dt,
            )
        if not in_window:
            raise UnScheduledVisitWindowError(msg)
