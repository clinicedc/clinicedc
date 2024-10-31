from uuid import uuid4

from django.db import models
from django.db.models import PROTECT
from edc_model.models import BaseUuidModel, HistoricalRecords

from ..medication import Assignment, Formulation


class Product(BaseUuidModel):

    product_identifier = models.CharField(max_length=36, unique=True)

    name = models.CharField(max_length=50, unique=True, editable=False)

    formulation = models.ForeignKey(Formulation, on_delete=PROTECT)

    assignment = models.ForeignKey(Assignment, on_delete=PROTECT, null=True, blank=False)

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.product_identifier:
            self.product_identifier = str(uuid4())
        if not self.name:
            self.name = f"{self.formulation}-{self.assignment}"
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock: Product"
        verbose_name_plural = "Stock: Product"
