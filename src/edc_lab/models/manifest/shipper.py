from django.db import models

from edc_model.models import AddressMixin, BaseUuidModel, HistoricalRecords


class ShipperManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Shipper(AddressMixin, BaseUuidModel):
    name = models.CharField(unique=True, max_length=50)

    objects = ShipperManager()

    history = HistoricalRecords()

    def natural_key(self):
        return (self.name,)

    def __str__(self):
        return self.name

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Shipper"
