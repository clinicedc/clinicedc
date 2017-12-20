from django.db import models
from django.db.models import options
from edc_base import get_utcnow
from edc_base.model_validators.date import datetime_not_future
from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin
from edc_protocol.validators import datetime_not_before_study_start

from .subject_schedule_model_mixin import SubjectScheduleModelMixin

if 'visit_schedule_name' not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('visit_schedule_name',)

if 'consent_model' not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('consent_model',)


class OnScheduleModelError(Exception):
    pass


class OnScheduleModelMixin(UniqueSubjectIdentifierFieldMixin,
                           SubjectScheduleModelMixin, models.Model):
    """A model mixin for a schedule's onschedule model.
    """

    onschedule_datetime = models.DateTimeField(
        validators=[
            datetime_not_before_study_start,
            datetime_not_future],
        default=get_utcnow)

    def save(self, *args, **kwargs):
        if not self._meta.consent_model:
            raise OnScheduleModelError(
                'Consent model attribute not set on Meta. Got '
                f'\'{self._meta.label_lower}.consent_model\' = None')
        elif not self._meta.visit_schedule_name:
            raise OnScheduleModelError(
                'Visit schedule name attribute not set on Meta. Got '
                f'\'{self._meta.label_lower}.visit_schedule_name\' = None')
        super().save(*args, **kwargs)

    @property
    def report_datetime(self):
        return self.onschedule_datetime

    class Meta:
        abstract = True
        visit_schedule_name = None
        consent_model = None
        unique_together = (
            'subject_identifier', 'visit_schedule_name', 'schedule_name')
