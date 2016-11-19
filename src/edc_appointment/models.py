from django.db import models


class HolidayManager(models.Manager):

    def for_month(self, year, month):
        """Returns a list of weekdays for a given year and month."""
        return [obj.day for obj in self.filter(day__year=year, day__month=month).order_by('day')]


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

    class Meta:
        ordering = ['day', ]
        app_label = 'edc_appointment'
