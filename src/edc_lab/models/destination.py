from django.db import models

from edc_base.model.models import BaseUuidModel, HistoricalRecords, ListModelMixin

from ..managers import DestinationManager


class Destination(ListModelMixin, BaseUuidModel):

    description = models.CharField(
        max_length=50)

    address = models.TextField(
        verbose_name='Address',
        null=True,
        blank=True,
        max_length=250)

    tel = models.CharField(
        verbose_name='Telephone',
        null=True,
        blank=True,
        max_length=50)

    email = models.CharField(
        verbose_name='Email',
        null=True,
        blank=True,
        max_length=25)

    objects = DestinationManager()

    history = HistoricalRecords()

    def __str__(self):
        return self.description

    class Meta(ListModelMixin.Meta):
        app_label = 'edc_lab'
