from django.db import models
from edc_base.model_validators.date import datetime_not_future
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_protocol.validators import datetime_not_before_study_start
from edc_base.model_mixins import BaseUuidModel

from ..choices import SCHEDULE_STATUS
from ..model_mixins import VisitScheduleFieldsModelMixin


class OnScheduleModelError(Exception):
    pass


class SubjectScheduleModelManager(models.Manager):

    def get_by_natural_key(self, subject_identifier, visit_schedule_name, schedule_name):
        return self.get(
            subject_identifier=subject_identifier,
            visit_schedule_name=visit_schedule_name,
            schedule_name=schedule_name)


class SubjectScheduleHistory(NonUniqueSubjectIdentifierFieldMixin,
                             VisitScheduleFieldsModelMixin, BaseUuidModel):

    onschedule_model = models.CharField(
        max_length=100)

    offschedule_model = models.CharField(
        max_length=100)

    onschedule_datetime = models.DateTimeField(
        validators=[
            datetime_not_before_study_start,
            datetime_not_future])

    offschedule_datetime = models.DateTimeField(
        validators=[
            datetime_not_before_study_start,
            datetime_not_future],
        null=True)

    schedule_status = models.CharField(
        max_length=15,
        choices=SCHEDULE_STATUS,
        null=True)

    objects = SubjectScheduleModelManager()

    def natural_key(self):
        return (self.subject_identifier, self.visit_schedule_name, self.schedule_name)

    class Meta:
        unique_together = (
            'subject_identifier', 'visit_schedule_name', 'schedule_name')
