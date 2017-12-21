from django.db import models

from edc_base.utils import get_uuid

from .visit_schedule_model_mixins import VisitScheduleModelMixin
from edc_visit_schedule.site_visit_schedules import SiteVisitScheduleError,\
    site_visit_schedules
from edc_visit_schedule.visit_schedule.visit_schedule import VisitScheduleError


class SubjectScheduleModelError(Exception):
    pass


class SubjectScheduleModelMixin(VisitScheduleModelMixin, models.Model):
    """A base model mixin shared by the off_schedule/on_schedule
    models.
    """
    consent_identifier = models.UUIDField()

    def __str__(self):
        s = f'{self.subject_identifier}'
        if self.visit_schedule_name:
            s = f'{s} {self.visit_schedule_name}'
            if self.schedule_name:
                s = f'{s}.{self.schedule_name}'
        return s

    def save(self, *args, **kwargs):
        if not self.id:
            if not self.subject_identifier:
                self.subject_identifier = get_uuid()
        self.visit_schedule_name, self.schedule_name = (
            self._meta.visit_schedule_name.split('.'))
        try:
            visit_schedule = site_visit_schedules.get_visit_schedule(
                visit_schedule_name=self.visit_schedule_name)
        except (SiteVisitScheduleError, VisitScheduleError) as e:
            raise SubjectScheduleModelError(
                f'Visit Schedule not found. Model {repr(self)} Got {e}') from e
        try:
            visit_schedule.get_schedule(
                schedule_name=self.schedule_name)
        except (SiteVisitScheduleError, VisitScheduleError) as e:
            raise SubjectScheduleModelError(
                f'Schedule not found. Model {repr(self)} Got {e}') from e
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        unique_together = (
            'subject_identifier', 'visit_schedule_name', 'schedule_name')
