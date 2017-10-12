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

    @property
    def label(self):
        return self.name

    @property
    def local_date(self):
        return self.day.strftime("%Y-%m-%d")

    def __str__(self):
        return f'{self.label} on {self.local_date}'

    class Meta:
        ordering = ['day', ]


if 'edc_appointment' in settings.APP_NAME:
    from .tests import models
