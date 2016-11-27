from dateutil.relativedelta import relativedelta

from django.db import models
from django.db.models import options
from django.utils import timezone

from edc_base.utils import get_utcnow, get_uuid
from edc_base.model.validators import datetime_not_future
from edc_protocol.validators import datetime_not_before_study_start

from .exceptions import ScheduleError, EnrollmentError
from .site_visit_schedules import site_visit_schedules

if 'visit_schedule_name' not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('visit_schedule_name',)


class DisenrollmentError(Exception):
    pass


class VisitScheduleMethodsModelMixin(models.Model):
    """A model mixin that adds methods used to work with the visit schedule.

    Declare with VisitScheduleFieldsModelMixin or the fields from VisitScheduleFieldsModelMixin"""

    @property
    def schedule(self):
        """Return the schedule name from Meta.visit_schedule_name or self.schedule_name.

        Declared on Meta like this:
            visit_schedule_name = 'visit_schedule_name.schedule_name'"""
        try:
            schedule_name = self._meta.visit_schedule_name
        except AttributeError:
            schedule_name = self.schedule_name
        try:
            _, schedule_name = schedule_name.split('.')
        except ValueError:
            pass
        return self.visit_schedule.get_schedule(self.schedule_name)

    @property
    def visit_schedule(self):
        """Return the visit schedule name from Meta.visit_schedule_name or self.visit_schedule_name."""
        try:
            visit_schedule_name = self._meta.visit_schedule_name
        except AttributeError:
            visit_schedule_name = self.visit_schedule_name
        try:
            visit_schedule_name, _ = visit_schedule_name.split('.')
        except ValueError:
            pass
        visit_schedule = site_visit_schedules.get_visit_schedule(visit_schedule_name)
        return visit_schedule

    def timepoint_datetimes(self, base_datetime, schedule):
        """Returns a calculated list of unadjusted datetimes in order of timepoint based on the schedule."""
        timepoint_datetimes = []
        for visit in schedule.visits:
            if visit.base_interval == 0:
                timepoint_datetime = base_datetime
            else:
                timepoint_datetime = base_datetime + relativedelta(
                    **{visit.base_interval_unit: visit.base_interval})
            timepoint_datetimes.append((visit, timepoint_datetime))
        return timepoint_datetimes

    class Meta:
        abstract = True


class VisitScheduleFieldsModelMixin(models.Model):
    """A model mixin that adds fields required to work with the visit schedule methods on the
    VisitScheduleMethodsModelMixin.

    Note: visit_code is not included."""

    visit_schedule_name = models.CharField(
        max_length=25,
        editable=False,
        help_text='the name of the visit schedule used to find the "schedule"')

    schedule_name = models.CharField(
        max_length=25,
        editable=False)

    class Meta:
        abstract = True


class VisitScheduleModelMixin(VisitScheduleFieldsModelMixin, VisitScheduleMethodsModelMixin, models.Model):

    """A model mixin that adds adds field attributes and methods that link a model instance to its schedule.

    This mixin is used with Appointment and Visit models via their respective model mixins."""

    visit_code = models.CharField(
        max_length=25,
        null=True,
        editable=False)

    class Meta:
        abstract = True


class BaseEnrollmentModelMixin(VisitScheduleFieldsModelMixin, VisitScheduleMethodsModelMixin, models.Model):
    """A base model mixin shared by the enrollment/disenrollment models."""

    subject_identifier = models.CharField(
        verbose_name="Subject Identifier",
        max_length=50,
        default=get_uuid,
        editable=False)

    report_datetime = models.DateTimeField(
        validators=[
            datetime_not_before_study_start,
            datetime_not_future],
        default=get_utcnow)

    def __str__(self):
        return self.subject_identifier

    def save(self, *args, **kwargs):
        schedule_name = self.schedule_name
        self.visit_schedule_name, self.schedule_name = self._meta.visit_schedule_name.split('.')
        if schedule_name and schedule_name != self.schedule_name:
            raise ScheduleError(
                'Invalid schedule name specified for \'{}\'. Expected \'{}\'. Got \'{}\'.'.format(
                    self._meta.label_lower, self.schedule_name, schedule_name))
        schedule = site_visit_schedules.get_visit_schedule(self.visit_schedule_name).schedules.get(self.schedule_name)
        models = [schedule.enrollment_model._meta.label_lower, schedule.disenrollment_model._meta.label_lower]
        if self._meta.label_lower not in models:
            raise ScheduleError('\'{}\' cannot be used with schedule \'{}\'. Expected {}'.format(
                self._meta.label_lower, self.schedule_name, models))
        self.additional_validation_on_save()
        super(BaseEnrollmentModelMixin, self).save(*args, **kwargs)

    def natural_key(self):
        return (self.subject_identifier, self.visit_schedule_name, self.schedule_name)

    def additional_validation_on_save(self):
        pass

    class Meta:
        abstract = True
        visit_schedule_name = None
        unique_together = ('subject_identifier', 'visit_schedule_name', 'schedule_name')


class DisenrollmentModelMixin(BaseEnrollmentModelMixin, models.Model):
    """A model mixin for a schedule's enrollment model."""

    disenrollment_datetime = models.DateTimeField(
        validators=[
            datetime_not_before_study_start,
            datetime_not_future],
        default=get_utcnow)

    @property
    def enrollment(self):
        return site_visit_schedules.enrollment(
            self.subject_identifier, self.visit_schedule_name, self.schedule_name)

    def additional_validation_on_save(self):
        if not self.enrollment:
            raise EnrollmentError(
                'Cannot disenroll subject \'{}\' from \'{}.{}\'. Enrollment does not exist.'.format(
                    self.subject_identifier, self.visit_schedule_name, self.schedule_name))
        self.datetime_not_before_enrollment_or_raise()
        self.datetime_after_last_visit_or_raise()

    def datetime_not_before_enrollment_or_raise(self):
        if relativedelta(self.disenrollment_datetime, self.enrollment.report_datetime).days < 0:
            raise DisenrollmentError(
                'Disenrollment datetime cannot precede the enrollment datetime {}. Got {}'.format(
                    timezone.localtime(self.enrollment.report_datetime),
                    timezone.localtime(self.disenrollment_datetime)))

    def datetime_after_last_visit_or_raise(self):
        last_visit_datetime = site_visit_schedules.last_visit_datetime(
            self.subject_identifier, visit_schedule_name=self.visit_schedule_name, schedule_name=self.schedule_name)
        if relativedelta(self.disenrollment_datetime, last_visit_datetime).days < 0:
            raise DisenrollmentError(
                'Disenrollment datetime cannot precede the last visit datetime {}. Got {}'.format(
                    timezone.localtime(last_visit_datetime), timezone.localtime(self.disenrollment_datetime)))

    class Meta:
        abstract = True
        visit_schedule_name = None
        unique_together = ('subject_identifier', 'visit_schedule_name', 'schedule_name')


class EnrollmentModelMixin(BaseEnrollmentModelMixin, models.Model):
    """A model mixin for a schedule's enrollment model."""

    is_eligible = models.BooleanField(
        default=False,
        editable=False)

    class Meta:
        abstract = True
        visit_schedule_name = None
        unique_together = ('subject_identifier', 'visit_schedule_name', 'schedule_name')
