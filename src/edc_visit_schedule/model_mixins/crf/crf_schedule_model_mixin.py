from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models

from ...subject_schedule import SubjectSchedule

if TYPE_CHECKING:
    from ...schedule import Schedule
    from ...visit_schedule import VisitSchedule


class CrfScheduleModelMixin(models.Model):
    """A mixin for CRF models to add the ability to determine
    if the subject is on/off schedule.

    To be declared with VisitMethodsModelMixin to get access
    to `related_visit` and `subject_identifier`.
    """

    # If True, compares report_datetime and offschedule_datetime as datetimes
    # If False, (Default) compares report_datetime and
    # offschedule_datetime as dates
    offschedule_compare_dates_as_datetimes = False

    def save(self, *args, **kwargs):
        self.is_onschedule_or_raise()
        super().save(*args, **kwargs)

    @property
    def visit_schedule_name(self) -> str:
        return self.related_visit.visit_schedule_name

    @property
    def schedule_name(self) -> str:
        return self.related_visit.schedule_name

    @property
    def visit_schedule(self) -> VisitSchedule:
        return self.related_visit.visit_schedule

    @property
    def schedule(self) -> Schedule:
        return self.related_visit.schedule

    def is_onschedule_or_raise(self) -> None:
        subject_schedule = SubjectSchedule(
            visit_schedule=self.visit_schedule, schedule=self.schedule
        )
        subject_schedule.onschedule_or_raise(
            subject_identifier=self.subject_identifier,
            report_datetime=self.report_datetime,
            compare_as_datetimes=self.offschedule_compare_dates_as_datetimes,
        )

    class Meta:
        abstract = True
