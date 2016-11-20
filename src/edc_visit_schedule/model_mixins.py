from django.db import models
from django.db.models import options
from django.utils import timezone

from edc_registration.model_mixins import RegisteredSubjectMixin
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

if 'visit_schedule_name' not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('visit_schedule_name',)


class BaseVisitScheduleModelMixin(models.Model):

    visit_schedule_name = models.CharField(
        max_length=25,
        null=True,
        editable=False,
        help_text='the name of the visit schedule used to find the "schedule"')

    schedule_name = models.CharField(
        max_length=25,
        null=True,
        editable=False,
        help_text='the name of the schedule used to find the list of "visits" to create appointments')

    @property
    def schedule(self):
        visit_schedule = site_visit_schedules.get_visit_schedule(self.visit_schedule_name)
        return visit_schedule.get_schedule(self.schedule_name)

    class Meta:
        abstract = True


class VisitScheduleModelMixin(BaseVisitScheduleModelMixin, models.Model):

    """Adds field attributes that link a model instance to the schedule.

    Fields visit_schedule_name, schedule_name and visit_code must be updated manually.
    For example, appointment updates these fields when created.

    See also CreateAppointmentsMixin. """

    visit_code = models.CharField(
        max_length=25,
        null=True,
        editable=False)

    @property
    def schedule(self):
        visit_schedule = site_visit_schedules.get_visit_schedule(self.visit_schedule_name)
        return visit_schedule.get_schedule(self.schedule_name)

    class Meta:
        abstract = True


class DisenrollmentModelMixin(RegisteredSubjectMixin, BaseVisitScheduleModelMixin, models.Model):
    """A model mixin for a schedule's disenrollment model."""

    report_datetime = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.visit_schedule_name = self._meta.visit_schedule_name
        super(BaseVisitScheduleModelMixin, self).save(*args, **kwargs)

    class Meta:
        abstract = True
        visit_schedule_name = None


class EnrollmentModelMixin(DisenrollmentModelMixin, models.Model):
    """A model mixin for a schedule's enrollment model."""

    class Meta(DisenrollmentModelMixin.Meta):
        abstract = True
