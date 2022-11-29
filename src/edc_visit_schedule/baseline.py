from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .site_visit_schedules import SiteVisitScheduleError, site_visit_schedules

if TYPE_CHECKING:
    from decimal import Decimal

    from .schedule import Schedule
    from .visit_schedule import VisitSchedule


class VisitScheduleBaselineError(Exception):
    pass


class Baseline:
    def __init__(
        self,
        instance: Any = None,
        timepoint: Decimal | None = None,
        visit_code_sequence: int | None = None,
        visit_schedule_name: str | None = None,
        schedule_name: str | None = None,
    ):
        if instance:
            try:
                instance = instance.appointment
            except AttributeError:
                try:
                    instance = instance.subject_visit.appointment
                except AttributeError:
                    pass
            self.visit_schedule_name = instance.visit_schedule_name
            self.schedule_name = instance.schedule_name
            self.visit_code_sequence = instance.visit_code_sequence
            self.timepoint = instance.timepoint
        else:
            self.visit_schedule_name = visit_schedule_name
            self.schedule_name = schedule_name
            self.visit_code_sequence = visit_code_sequence
            self.timepoint = timepoint
            if self.timepoint is None:
                raise VisitScheduleBaselineError("timepoint may not be None")
        if not any([x == self.timepoint for x in self.timepoints.values()]):
            raise VisitScheduleBaselineError(
                f"Unknown timepoint. For schedule {self.visit_schedule}.{self.schedule}. "
                f"Got {self.timepoint} not in {self.timepoints}"
            )
        self.value: bool = (
            self.timepoint == self.baseline_timepoint and self.visit_code_sequence == 0
        )

    @property
    def visit_schedule(self) -> VisitSchedule:
        self.have_required_attrs_or_raise()
        try:
            visit_schedule = site_visit_schedules.get_visit_schedule(self.visit_schedule_name)
        except SiteVisitScheduleError as e:
            raise VisitScheduleBaselineError(str(e))
        return visit_schedule

    @property
    def schedule(self) -> Schedule:
        try:
            schedule = self.visit_schedule.schedules.get(self.schedule_name)
        except SiteVisitScheduleError as e:
            raise VisitScheduleBaselineError(str(e))
        return schedule

    @property
    def baseline_timepoint(self) -> Decimal:
        """Returns a decimal that is the first timepoint in this schedule"""
        return self.schedule.visits.first.timepoint

    @property
    def timepoints(self) -> dict:
        return self.schedule.visits.timepoints

    def have_required_attrs_or_raise(self):
        data = {
            k: getattr(self, k, None) is None
            for k in [
                "visit_schedule_name",
                "schedule_name",
                "visit_code_sequence",
                "timepoint",
            ]
        }

        if any(data.values()):
            raise VisitScheduleBaselineError(
                "Missing value(s). Unable to determine if baseline. "
                f"Got `None` for {[k for k, v in data.items() if v is True]}."
            )
