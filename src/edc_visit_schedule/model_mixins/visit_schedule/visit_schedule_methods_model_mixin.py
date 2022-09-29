from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models

from ...site_visit_schedules import site_visit_schedules

if TYPE_CHECKING:
    from ...schedule import Schedule, VisitCollection
    from ...visit import Visit
    from ...visit_schedule import VisitSchedule


class VisitScheduleModelMixinError(Exception):
    pass


class VisitScheduleMethodsModelMixin(models.Model):
    """A model mixin that adds methods used to work with the visit schedule.

    Declare with VisitScheduleFieldsModelMixin or the fields from
    VisitScheduleFieldsModelMixin
    """

    @property
    def visit(self) -> Visit:
        """Returns the visit object from the schedule object
        for this visit code.

        Note: This is not a model instance.
        """
        return self.visit_from_schedule

    @property
    def visit_from_schedule(self) -> Visit:
        """Returns the visit object from the schedule object
        for this visit code.

        Note: This is not a model instance.
        """
        visit = self.schedule.visits.get(self.visit_code)
        if not visit:
            raise VisitScheduleModelMixinError(
                f"Visit not found in schedule. Expected one of {self.schedule.visits}. "
                f"Got {self.visit_code}."
            )
        return visit

    @property
    def visits(self) -> VisitCollection:
        """Returns all visit objects from the schedule object."""
        return self.schedule.visits

    @property
    def schedule(self) -> Schedule:
        """Returns a schedule object from Meta.visit_schedule_name or
        self.schedule_name.

        Declared on Meta like this:
            visit_schedule_name = 'visit_schedule_name.schedule_name'
        """
        return self.visit_schedule.schedules.get(self.schedule_name)

    @property
    def visit_schedule(self) -> VisitSchedule:
        """Returns a visit schedule object"""
        return site_visit_schedules.get_visit_schedule(
            visit_schedule_name=self.visit_schedule_name
        )

    class Meta:
        abstract = True
