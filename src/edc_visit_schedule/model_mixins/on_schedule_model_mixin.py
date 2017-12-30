from django.conf import settings
from django.db import models
from django.utils import timezone
from edc_base import get_utcnow, convert_php_dateformat
from edc_base.model_mixins import SiteModelMixin
from edc_base.model_validators.date import datetime_not_future
from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin
from edc_protocol.validators import datetime_not_before_study_start

from ..site_visit_schedules import site_visit_schedules


class OnScheduleModelManager(models.Manager):

    def get_by_natural_key(self, subject_identifier):
        return self.get(subject_identifier=subject_identifier)


class OnScheduleModelMixin(UniqueSubjectIdentifierFieldMixin, SiteModelMixin, models.Model):
    """A model mixin for a schedule's onschedule model.
    """
    onschedule_datetime = models.DateTimeField(
        validators=[
            datetime_not_before_study_start,
            datetime_not_future],
        default=get_utcnow)

    objects = OnScheduleModelManager()

    def __str__(self):
        formatted_date = timezone.localtime(
            self.onschedule_datetime).strftime(
                convert_php_dateformat(settings.SHORT_DATE_FORMAT))
        return f'{self.subject_identifier} {formatted_date}'

    def natural_key(self):
        return (self.subject_identifier, )

    def put_on_schedule(self):
        _, schedule = site_visit_schedules.get_by_onschedule_model(
            self._meta.label_lower)
        schedule.put_on_schedule(onschedule_model_obj=self)

    class Meta:
        abstract = True
