from dateutil.relativedelta import relativedelta

from django.db import models
from django.db.models import options
from django.utils import timezone

from edc_base.utils import get_utcnow, get_uuid
from edc_base.model_validators import datetime_not_future
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_protocol.validators import datetime_not_before_study_start

from .site_visit_schedules import site_visit_schedules, RegistryNotLoaded, SiteVisitScheduleError
from .visit_schedule import VisitScheduleModelError

if 'visit_schedule_name' not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('visit_schedule_name',)


class EnrollmentModelError(Exception):
    pass


class EnrollmentError(Exception):
    pass


class DisenrollmentError(Exception):
    pass


class VisitScheduleMethodsModelMixin(models.Model):
    """A model mixin that adds methods used to work with the visit schedule.

    Declare with VisitScheduleFieldsModelMixin or the fields from
    VisitScheduleFieldsModelMixin
    """

    @property
    def schedule(self):
        """Returns a schedule object from Meta.visit_schedule_name or
        self.schedule_name.

        Declared on Meta like this:
            visit_schedule_name = 'visit_schedule_name.schedule_name'
        """
        try:
            _, schedule_name = self._meta.visit_schedule_name.split('.')
        except ValueError as e:
            raise VisitScheduleModelError(f'{self.__class__.__name__}. Got {e}') from e
        return self.visit_schedule.get_schedule(schedule_name=schedule_name)

    @property
    def visit_schedule(self):
        """Returns a visit schedule object from Meta.visit_schedule_name.

        Declared on Meta like this:
            visit_schedule_name = 'visit_schedule_name.schedule_name'
        """
        try:
            visit_schedule_name, _ = self._meta.visit_schedule_name.split('.')
        except ValueError as e:
            raise VisitScheduleModelError(f'{self.__class__.__name__}. Got {e}') from e
        try:
            visit_schedule = site_visit_schedules.get_visit_schedule(
                visit_schedule_name)
        except RegistryNotLoaded as e:
            raise VisitScheduleModelError(
                f'visit_schedule_name: \'{visit_schedule_name}\'. Got {e}') from e
        except SiteVisitScheduleError as e:
            raise VisitScheduleModelError(
                f'visit_schedule_name: \'{visit_schedule_name}\'. Got {e}') from e
        return visit_schedule

    def timepoint_datetimes(self, base_datetime, schedule):
        """Returns a calculated list of unadjusted datetimes in order
        of timepoint based on the schedule."""
        for visit in schedule.visits:
            if visit.base_interval == 0:
                timepoint_datetime = base_datetime
            else:
                timepoint_datetime = base_datetime + relativedelta(
                    **{visit.base_interval_unit: visit.base_interval})
            yield (visit, timepoint_datetime)

    class Meta:
        abstract = True


class VisitScheduleFieldsModelMixin(models.Model):
    """A model mixin that adds fields required to work with the visit
    schedule methods on the VisitScheduleMethodsModelMixin.

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


class VisitScheduleModelMixin(VisitScheduleFieldsModelMixin,
                              VisitScheduleMethodsModelMixin,
                              models.Model):

    """A model mixin that adds adds field attributes and methods that
    link a model instance to its schedule.

    This mixin is used with Appointment and Visit models via their
    respective model mixins.
    """

    visit_code = models.CharField(
        max_length=25,
        null=True,
        editable=False)

    class Meta:
        abstract = True


class BaseEnrollmentModelMixin(
        NonUniqueSubjectIdentifierFieldMixin, VisitScheduleFieldsModelMixin,
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

    def common_clean(self):
        self.visit_schedule_name, schedule_name = (
            self._meta.visit_schedule_name.split('.'))
        if self.schedule_name and self.schedule_name != schedule_name:
            raise EnrollmentModelError(
                f'Invalid schedule name specified for \'{self._meta.label_lower}\'. '
                f'Expected \'{schedule_name}\' (field). Got \'{self.schedule_name}\' (model._meta).')
        visit_schedule = site_visit_schedules.get_visit_schedule(
            visit_schedule_name=self.visit_schedule_name)
        if not visit_schedule:
            raise EnrollmentModelError(
                f'Invalid visit schedule name or visit schedule not registered. '
                f'Got \'{self.visit_schedule_name}\'.')
        schedule = visit_schedule.get_schedule(
            schedule_name=self.schedule_name)
        if not schedule:
            raise EnrollmentModelError(
                f'Invalid schedule name or schedule name not added. '
                f'Got \'{self.schedule_name}\'.')
        models = [schedule.enrollment_model._meta.label_lower,
                  schedule.disenrollment_model._meta.label_lower]
        if self._meta.label_lower not in models:
            raise EnrollmentModelError(
                f'\'{self._meta.label_lower}\' cannot be used with schedule '
                f' \'{self.schedule_name}\'. Expected {models}')
        super().common_clean()

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
                    f'Expected {self.visit_schedule_name}. Got \'{visit_schedule_name}\'')
            if self.schedule_name != schedule_name:
                raise EnrollmentModelError(
                    f'Not allowing attempt to change schedule name. '
                    f'Expected {self.schedule_name}. Got \'{schedule_name}\'')
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.subject_identifier,
                self.visit_schedule_name,
                self.schedule_name)

    class Meta:
        abstract = True
        visit_schedule_name = None
        unique_together = (
            'subject_identifier', 'visit_schedule_name', 'schedule_name')


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
            self.subject_identifier,
            self.visit_schedule_name,
            self.schedule_name)

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

        if relativedelta(self.disenrollment_datetime, enrollment.report_datetime).days < 0:
            raise DisenrollmentError(
                f'Disenrollment datetime cannot precede the enrollment '
                f'datetime {timezone.localtime(enrollment.report_datetime)}. '
                f'Got {timezone.localtime(self.disenrollment_datetime)}')

        visit = visit_schedule.models.visit_model.objects.filter(
            subject_identifier=self.subject_identifier,
            visit_schedule_name=self.visit_schedule_name,
            schedule_name=self.schedule_name).order_by('report_datetime').last()

        if visit:
            if relativedelta(self.disenrollment_datetime, visit.last_visit_datetime).days < 0:
                raise DisenrollmentError(
                    f'Disenrollment datetime cannot precede the last visit '
                    f'datetime {timezone.localtime(visit.last_visit_datetime)}. '
                    f'Got {timezone.localtime(self.disenrollment_datetime)}')

        super().common_clean()

    class Meta:
        abstract = True
        visit_schedule_name = None
        unique_together = (
            'subject_identifier', 'visit_schedule_name', 'schedule_name')


class EnrollmentModelMixin(BaseEnrollmentModelMixin, models.Model):
    """A model mixin for a schedule's enrollment model."""

    is_eligible = models.BooleanField(
        default=False,
        editable=False)

    class Meta:
        abstract = True
        visit_schedule_name = None
        unique_together = (
            'subject_identifier', 'visit_schedule_name', 'schedule_name')
