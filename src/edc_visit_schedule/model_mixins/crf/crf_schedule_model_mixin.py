from __future__ import annotations

from django.db import models

from ...subject_schedule import SubjectSchedule


class CrfScheduleModelMixin(models.Model):
    """A mixin for CRF models to add the ability to determine
    if the subject is on/off schedule.

    To be declared with VisitMethodsCrfModelMixin to get access
    to `related_visit` and `subject_identifier`.
    """

    # If True, compares report_datetime and offschedule_datetime as datetimes
    # If False, (Default) compares report_datetime and
    # offschedule_datetime as dates
    offschedule_compare_dates_as_datetimes = False
    subject_schedule_cls = SubjectSchedule

    @property
    def visit_schedule_name(self):
        return self.related_visit.visit_schedule_name

    @property
    def schedule_name(self):
        return self.related_visit.schedule_name

    @property
    def visit_schedule(self):
        return self.related_visit.visit_schedule

    @property
    def schedule(self):
        return self.related_visit.schedule

    def is_onschedule_or_raise(self):
        subject_schedule = self.subject_schedule_cls(
            visit_schedule=self.visit_schedule, schedule=self.schedule
        )
        subject_schedule.onschedule_or_raise(
            subject_identifier=self.subject_identifier,
            report_datetime=self.related_visit.report_datetime,
            compare_as_datetimes=self.offschedule_compare_dates_as_datetimes,
        )

    def save(self, *args, **kwargs):
        self.is_onschedule_or_raise()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
