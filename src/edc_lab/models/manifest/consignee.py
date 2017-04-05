from django.db import models

from edc_base.model_mixins import AddressMixin, BaseUuidModel
from edc_base.model_managers import HistoricalRecords


class ConsigneeManager(models.Manager):

    def get_by_natural_key(self, name):
        return self.get(name=name)


class Consignee(AddressMixin, BaseUuidModel):

    name = models.CharField(
        unique=True,
        max_length=50,
        help_text='Company name')

    objects = ConsigneeManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.name, )

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'edc_lab'
        ordering = ('name', )
