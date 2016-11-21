from dateutil.relativedelta import relativedelta
from uuid import uuid4

from django.db import models
from django.db.models import options
from django.utils import timezone

from .site_visit_schedules import site_visit_schedules

if 'visit_schedule_name' not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('visit_schedule_name',)


def get_uuid():
    return str(uuid4())


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


class DisenrollmentModelMixin(VisitScheduleFieldsModelMixin, VisitScheduleMethodsModelMixin, models.Model):
    """A model mixin for a schedule's disenrollment model."""

    subject_identifier = models.CharField(
        verbose_name="Subject Identifier",
        max_length=50,
        unique=True,
        default=get_uuid,
        editable=False)

    report_datetime = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        try:
            self.visit_schedule_name, self.schedule_name = self._meta.visit_schedule_name.split('.')
        except ValueError:
            self.visit_schedule_name = self._meta.visit_schedule_name
        super(DisenrollmentModelMixin, self).save(*args, **kwargs)

    class Meta:
        abstract = True
        visit_schedule_name = None


class EnrollmentModelMixin(DisenrollmentModelMixin, models.Model):
    """A model mixin for a schedule's enrollment model."""

    class Meta:
        abstract = True
        visit_schedule_name = None
