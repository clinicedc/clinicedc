from django.db import models
from django.db.models import PROTECT
from edc_model.models import BaseUuidModel, HistoricalRecords
from sequences import get_next_value

from ..medication import Assignment, Formulation


class Product(BaseUuidModel):

    product_identifier = models.CharField(max_length=36, unique=True, null=True, blank=True)

    name = models.CharField(
        max_length=50, unique=True, blank=True, help_text="Leave blank to use default"
    )

    formulation = models.ForeignKey(Formulation, on_delete=PROTECT)

    assignment = models.ForeignKey(Assignment, on_delete=PROTECT, null=True, blank=False)

    history = HistoricalRecords()

    def __str__(self):
        return (
            f"{self.formulation.description_with_assignment(self.assignment)}"
            f" [{self.product_identifier}]"
        )

    def save(self, *args, **kwargs):
        if not self.product_identifier:
            self.product_identifier = f"{get_next_value(self._meta.label_lower):06d}"
        if not self.name:
            self.name = f"{self.formulation}-{self.assignment}"
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Product"
        verbose_name_plural = "Product"
