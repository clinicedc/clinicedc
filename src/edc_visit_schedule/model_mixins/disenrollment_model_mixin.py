from datetime import timedelta
from dateutil.relativedelta import relativedelta

from django.db import models
from django.utils import timezone

from edc_base.model_validators import datetime_not_future
from edc_base.utils import get_utcnow
from edc_protocol.validators import datetime_not_before_study_start

from ..site_visit_schedules import site_visit_schedules
from .base_enrollment_model_mixin import BaseEnrollmentModelMixin
from edc_visit_schedule.enrolled_subject import EnrolledSubject


class DisenrollmentError(Exception):
    pass


class DisenrollmentModelMixin(BaseEnrollmentModelMixin, models.Model):
    """A model mixin for a schedule's enrollment model."""

    disenrollment_datetime = models.DateTimeField(
        validators=[
            datetime_not_before_study_start,
            datetime_not_future],
        default=get_utcnow)

    def common_clean(self):
        visit_schedule = site_visit_schedules.get_visit_schedule(
            visit_schedule_name=self.visit_schedule_name)
        schedule = visit_schedule.get_schedule(
            schedule_name=self.schedule_name)

        try:
            enrollment = schedule.enrollment_model.objects.get(
                subject_identifier=self.subject_identifier)
        except schedule.enrollment_model.DoesNotExist:
            raise DisenrollmentError(
                f'Cannot disenroll before enrollment. Subject \'{self.subject_identifier}\' '
                f'is not enrolled to \'{self.visit_schedule_name}.{self.schedule_name}\'. ')

        tdelta = enrollment.report_datetime - self.disenrollment_datetime
        if tdelta.days > 0:
            raise DisenrollmentError(
                f'Disenrollment datetime cannot precede the enrollment '
                f'datetime {timezone.localtime(enrollment.report_datetime)}. '
                f'Got {timezone.localtime(self.disenrollment_datetime)}')

        enrolled_subject = EnrolledSubject(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self._meta.visit_schedule_name.split('.')[0],
            schedule_name=self._meta.visit_schedule_name.split('.')[1])
        try:
            last_visit = enrolled_subject.visits[-1:][0]
        except IndexError:
            pass
        else:
            tdelta = last_visit.report_datetime - self.disenrollment_datetime
            if tdelta.days > 0:
                raise DisenrollmentError(
                    f'Disenrollment datetime cannot precede the last visit '
                    f'datetime {timezone.localtime(last_visit.report_datetime)}. '
                    f'Got {timezone.localtime(self.disenrollment_datetime)}')

        super().common_clean()

    class Meta:
        abstract = True
        visit_schedule_name = None
        unique_together = (
            'subject_identifier', 'visit_schedule_name', 'schedule_name')
