import pytz

from datetime import datetime, time

from django.db import models
from django.utils import timezone

from edc_base.model.models import BaseUuidModel, HistoricalRecords

from .managers import AppointmentManager
from .model_mixins import AppointmentModelMixin


class HolidayManager(models.Manager):

    def for_month(self, year, month, time=None):
        """Returns a list of weekdays for a given year and month."""
        return [obj.day_as_datetime(time) for obj in self.filter(day__year=year, day__month=month).order_by('day')]


class Appointment(AppointmentModelMixin, BaseUuidModel):

    objects = AppointmentManager()

    history = HistoricalRecords()

    @property
    def str_pk(self):
        return str(self.pk)

    class Meta:
        app_label = 'edc_appointment'


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
            datetime.combine(self.day, dtime or time(0, 0, 0)), timezone=pytz.utc)

    class Meta:
        ordering = ['day', ]
        app_label = 'edc_appointment'
