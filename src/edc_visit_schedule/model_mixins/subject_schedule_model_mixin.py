from django.db import models

from ..subject_schedule import SubjectSchedule


class SubjectScheduleModelMixin(models.Model):
    """A mixin for CRF models to add the ability to determine
    if the subject is on/off schedule.
    """

    # If True, compares report_datetime and offschedule_datetime as datetimes
    # If False, (Default) compares report_datetime and
    # offschedule_datetime as dates
    offschedule_compare_dates_as_datetimes = False
    subject_schedule_cls = SubjectSchedule

    def save(self, *args, **kwargs):
        visit_schedule = self.visit.appointment.visit_schedule
        schedule = self.visit.appointment.schedule
        subject_identifier = self.visit.subject_identifier
        subject_schedule = self.subject_schedule_cls(
            visit_schedule=visit_schedule, schedule=schedule
        )
        subject_schedule.onschedule_or_raise(
            subject_identifier=subject_identifier,
            report_datetime=self.visit.report_datetime,
            compare_as_datetimes=self.offschedule_compare_dates_as_datetimes,
        )
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
