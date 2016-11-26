import pytz

from datetime import datetime, time

from django.db import models
from django.utils import timezone

from edc_appointment.model_mixins import AppointmentModelMixin
from edc_base.model.models import BaseUuidModel, HistoricalRecords
from edc_consent.model_mixins import RequiresConsentMixin


class HolidayManager(models.Manager):

    def for_month(self, year, month, time=None):
        """Returns a list of weekdays for a given year and month."""
        return [obj.day_as_datetime(time) for obj in self.filter(day__year=year, day__month=month).order_by('day')]


class AppointmentManager(models.Manager):

    def get_by_natural_key(self, subject_identifer, visit_code):
        return self.get(subject_identifer=subject_identifer, visit_code=visit_code)


class Appointment(AppointmentModelMixin, RequiresConsentMixin, BaseUuidModel):

    objects = AppointmentManager()

    history = HistoricalRecords()

    @property
    def str_pk(self):
        return str(self.pk)

    def natural_key(self):
        return (self.subject_identifier, self.visit_code)


class Holiday(models.Model):

    day = models.DateField(
        unique=True)

    name = models.CharField(
        max_length=25,
        null=True,
        blank=True)

    objects = HolidayManager()

    def __str__(self):
        return '{} on {}'.format(self.name, self.day.strftime('%Y-%m-%d'))

    def day_as_datetime(self, dtime=None):
        return timezone.make_aware(
            datetime.combine(self.day, dtime or time(0, 0, 0)), timezone=pytz.timezone("UTC"))

    class Meta:
        ordering = ['day', ]
        app_label = 'edc_appointment'
