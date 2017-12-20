from django.db import models

from edc_base.utils import get_uuid

from .visit_schedule_model_mixins import VisitScheduleModelMixin


class EnrollmentModelError(Exception):
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
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.subject_identifier,
                self.visit_schedule_name,
                self.schedule_name)

    class Meta:
        abstract = True
        unique_together = (
            'subject_identifier', 'visit_schedule_name', 'schedule_name')
