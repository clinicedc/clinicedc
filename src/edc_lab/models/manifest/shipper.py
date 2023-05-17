from django.db import models
from edc_model import models as edc_models


class ShipperManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Shipper(edc_models.AddressMixin, edc_models.BaseUuidModel):
    name = models.CharField(unique=True, max_length=50)

    objects = ShipperManager()

    history = edc_models.HistoricalRecords()

    def natural_key(self):
        return (self.name,)

    def __str__(self):
        return self.name

    class Meta(edc_models.BaseUuidModel.Meta):
        verbose_name = "Shipper"
        ordering = ("name",)
