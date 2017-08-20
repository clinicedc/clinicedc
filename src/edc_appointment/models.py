from django.db import models

from edc_base.model_mixins import BaseUuidModel
from edc_base.model_managers import HistoricalRecords

from .managers import AppointmentManager
from .model_mixins import AppointmentModelMixin
from django.conf import settings


class Appointment(AppointmentModelMixin, BaseUuidModel):

    objects = AppointmentManager()

    history = HistoricalRecords()

    class Meta(AppointmentModelMixin.Meta):
        app_label = 'edc_appointment'


class Holiday(models.Model):

    day = models.DateField(
        unique=True)

    name = models.CharField(
        max_length=25,
        null=True,
        blank=True)

    def __str__(self):
        return '{} on {}'.format(self.name, self.day.strftime('%Y-%m-%d'))

    class Meta:
        ordering = ['day', ]
        app_label = 'edc_appointment'


if 'edc_appointment' in settings.APP_NAME:
    from .tests import models
