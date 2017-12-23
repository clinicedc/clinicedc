from django.db import models
from django.utils import timezone
from edc_base.model_validators import datetime_not_future
from edc_base.utils import get_utcnow
from edc_constants.date_constants import EDC_DATETIME_FORMAT
from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin
from edc_protocol.validators import datetime_not_before_study_start

from ..site_visit_schedules import site_visit_schedules


class OffScheduleModelManager(models.Manager):

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class OffScheduleModelMixin(UniqueSubjectIdentifierFieldMixin, models.Model):
    """Model mixin for a schedule's OffSchedule model.
    """

    offschedule_datetime = models.DateTimeField(
        verbose_name="Date and time subject taken off schedule",
        validators=[
            datetime_not_before_study_start,
            datetime_not_future],
        default=get_utcnow)

    objects = OffScheduleModelManager()

    def natural_key(self):
        return (self.subject_identifier, )

    def __str__(self):
        formatted_date = timezone.localtime(
            self.offschedule_datetime).strftime(EDC_DATETIME_FORMAT)
        return f'{self.subject_identifier} {formatted_date}'

    def take_off_schedule(self):
        _, schedule = site_visit_schedules.get_by_offschedule_model(
            self._meta.label_lower)
        schedule.take_off_schedule(offschedule_model_obj=self)

    class Meta:
        abstract = True
