from django.db import models
from edc_model.models import BaseUuidModel

from ..storage import ContainerType
from .container_units import ContainerUnits


class Container(BaseUuidModel):

    name = models.CharField(max_length=50, unique=True)

    container_type = models.ForeignKey(ContainerType, on_delete=models.PROTECT, null=True)

    container_units = models.ForeignKey(ContainerUnits, on_delete=models.PROTECT, null=True)

    container_qty = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.container_type.name
            if self.container_qty > 1.0:
                self.name = f"{self.name} of {self.container_qty}"
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock Unit"
        verbose_name_plural = "Stock Units"
