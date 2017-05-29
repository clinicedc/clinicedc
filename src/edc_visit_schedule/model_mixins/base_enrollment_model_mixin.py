from django.db import models

from edc_base.utils import get_utcnow, get_uuid
from edc_base.model_validators import datetime_not_future
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_protocol.validators import datetime_not_before_study_start

from ..site_visit_schedules import site_visit_schedules, SiteVisitScheduleError
from ..visit_schedule import VisitScheduleError
from .visit_schedule_model_mixins import VisitScheduleFieldsModelMixin, VisitScheduleMethodsModelMixin
from .visit_schedule_model_mixins import VisitScheduleMetaMixin


class EnrollmentModelError(Exception):
    pass


class BaseEnrollmentModelMixin(
        NonUniqueSubjectIdentifierFieldMixin,
        VisitScheduleFieldsModelMixin,
        VisitScheduleMethodsModelMixin, models.Model):
    """A base model mixin shared by the enrollment/disenrollment
    models.
    """

    report_datetime = models.DateTimeField(
        validators=[
            datetime_not_before_study_start,
            datetime_not_future],
        default=get_utcnow)

    def __str__(self):
        return self.subject_identifier

    def save(self, *args, **kwargs):
        if not self.id:
            if not self.subject_identifier:
                self.subject_identifier = get_uuid()
            self.visit_schedule_name, self.schedule_name = (
                self._meta.visit_schedule_name.split('.'))
        else:
            visit_schedule_name, schedule_name = (
                self._meta.visit_schedule_name.split('.'))
            if self.visit_schedule_name != visit_schedule_name:
                raise EnrollmentModelError(
                    f'Not allowing attempt to change visit schedule name. '
                    f'Expected \'{visit_schedule_name}\'. Got \'{self.visit_schedule_name}\'')
            if self.schedule_name != schedule_name:
                raise EnrollmentModelError(
                    f'Not allowing attempt to change schedule name. '
                    f'Expected {self.schedule_name}. Got \'{schedule_name}\'')
        # Asserts model's visit schedule/schedule is
        # registered/added or raises.
        try:
            visit_schedule = site_visit_schedules.get_visit_schedule(
                visit_schedule_name=self.visit_schedule_name)
            visit_schedule.get_schedule(
                schedule_name=self.schedule_name)
        except (SiteVisitScheduleError, VisitScheduleError) as e:
            raise EnrollmentModelError(f'Model {repr(self)} Got {e}') from e
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.subject_identifier,
                self.visit_schedule_name,
                self.schedule_name)

    class Meta(VisitScheduleMetaMixin.Meta):
        abstract = True
        unique_together = (
            'subject_identifier', 'visit_schedule_name', 'schedule_name')
