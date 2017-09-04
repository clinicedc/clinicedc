from django.db import models
from edc_base.model_validators import datetime_not_future
from edc_base.utils import get_utcnow
from edc_protocol.validators import datetime_not_before_study_start

from ..disenrollment_validator import DisenrollmentValidator
from .base_enrollment_model_mixin import BaseEnrollmentModelMixin


class DisenrollmentModelMixin(BaseEnrollmentModelMixin, models.Model):
    """A model mixin for a schedule's enrollment model.
    """

    disenrollment_validator_cls = DisenrollmentValidator

    disenrollment_datetime = models.DateTimeField(
        validators=[
            datetime_not_before_study_start,
            datetime_not_future],
        default=get_utcnow)

    def save(self, *args, **kwargs):
        self.disenrollment_validator_cls(
            subject_identifier=self.subject_identifier,
            disenrollment_datetime=self.disenrollment_datetime,
            visit_schedule_name=self._meta.visit_schedule_name.split('.')[0],
            schedule_name=self._meta.visit_schedule_name.split('.')[1])
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        visit_schedule_name = None
        unique_together = (
            'subject_identifier', 'visit_schedule_name', 'schedule_name')
