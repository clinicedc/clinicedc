from datetime import datetime, time
from django.db import models
from django.utils import timezone


class HolidayManager(models.Manager):

    def for_month(self, year, month, time=None):
        """Returns a list of weekdays for a given year and month."""
        return [obj.day_as_datetime(time) for obj in self.filter(day__year=year, day__month=month).order_by('day')]


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

    def day_as_datetime(self, time=None):
        return timezone.make_aware(datetime.combine(self.day, time or time(0, 0, 0)))

    class Meta:
        ordering = ['day', ]
        app_label = 'edc_appointment'
