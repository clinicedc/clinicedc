import arrow

from django.conf import settings

from .exceptions import ScheduleError


class ScheduledVisitWindowError(Exception):
    pass


class UnScheduledVisitWindowError(Exception):
    pass


enforce_window_period_enabled = getattr(
    settings, "EDC_VISIT_SCHEDULE_ENFORCE_WINDOW_PERIOD", True
)


class Window:
    def __init__(
        self,
        name=None,
        visits=None,
        dt=None,
        timepoint_datetime=None,
        visit_code=None,
        visit_code_sequence=None,
        baseline_timepoint_datetime=None,
    ):
        self.name = name
        self.visits = visits
        self.timepoint_datetime = timepoint_datetime
        self.dt = dt
        self.visit_code = visit_code
        self.visit_code_sequence = visit_code_sequence
        self.baseline_timepoint_datetime = baseline_timepoint_datetime

    @property
    def datetime_in_window(self):
        if enforce_window_period_enabled:
            if not self.visits.get(self.visit_code):
                raise ScheduleError(
                    f"Visit not added to schedule. Got visit `{self.visit_code}` "
                    f"not in schedule `{self.name}`. Expected one of "
                    f"{[x for x in self.visits]}."
                )
            if self.is_scheduled_visit or not self.visits.next(self.visit_code):
                self.raise_for_scheduled_not_in_window()
            else:
                self.raise_for_unscheduled_not_in_window()
        return True

    @property
    def is_scheduled_visit(self):
        return self.visit_code_sequence == 0 or self.visit_code_sequence is None

    def raise_for_scheduled_not_in_window(self):
        """Returns the datetime if it falls within the
        window period for a scheduled `visit` otherwise
        raises an exception.

        In this case, `visit` is the object from schedule and
        not a model instance.
        """
        visit = self.visits.get(self.visit_code)
        visit.timepoint_datetime = self.timepoint_datetime
        if not (
            visit.dates.lower
            <= arrow.get(self.dt).to("utc").datetime
            <= visit.dates.upper
        ):
            raise ScheduledVisitWindowError(
                "Invalid datetime. Falls outside of the "
                f"window period for this `scheduled` visit. "
                f"Expected a datetime between {visit.dates.lower} "
                f"and {visit.dates.upper} "
                f"Got `{self.visit_code}`@`{self.dt}`. "
            )

    def raise_for_unscheduled_not_in_window(self):
        """Returns the datetime if it falls within the
        window period for a unscheduled `visit` otherwise
        raises an exception.

        Window period for an unscheduled date is anytime
        on or after the scheduled date and before the projected
        lower bound of the next visit.

        In this case, `visit` is the object from schedule and
        not a model instance.
        """
        next_visit = self.visits.next(self.visit_code)
        next_timepoint_datetime = self.visits.timepoint_dates(
            dt=self.baseline_timepoint_datetime
        ).get(next_visit)
        if not (self.dt < next_timepoint_datetime - next_visit.rlower):
            raise UnScheduledVisitWindowError(
                "Invalid datetime. Falls outside of the "
                f"window period for this `unscheduled` visit. "
                f"Expected a datetime before the next visit. "
                f"Next visit is `{next_visit.code}` expected any time "
                f"from `{next_timepoint_datetime - next_visit.rlower}`."
                f"Got `{self.visit_code}`@`{self.dt}`. "
            )
