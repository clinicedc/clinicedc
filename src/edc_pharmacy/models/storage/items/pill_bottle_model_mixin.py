from django.db import models
from edc_model.models import BaseUuidModel

from ...formulation import Formulation
from ...medication_lot import MedicationLot
from .container_model_mixin import ContainerModelMixin


class PillBottleError(Exception):
    pass


class PillBottleModelMixin(ContainerModelMixin, BaseUuidModel):
    formulation = models.ForeignKey(Formulation, on_delete=models.PROTECT, blank=True)

    medication_lot = models.ForeignKey(MedicationLot, on_delete=models.PROTECT)

    max_unit_qty = models.IntegerField(blank=False, default=0)

    unit_qty = models.IntegerField(blank=False, default=0)

    source_container = models.ForeignKey(
        "self", on_delete=models.PROTECT, blank=True, null=True
    )

    unit_qty_out = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.formulation} {self.unit_qty} count"

    def save(self, *args, **kwargs):
        self.contains_uniquely_identifiable_items = False
        if self.unit_qty < self.unit_qty_out:
            raise PillBottleError(f"Qty cannot be negative. See {self}.")
        if self.max_unit_qty and self.max_unit_qty > self.unit_qty:
            raise PillBottleError(f"Qty exceeds max_unit_qty. See {self}.")
        self.formulation = self.medication_lot.formulation
        super().save(*args, **kwargs)

    class Meta(ContainerModelMixin.Meta, BaseUuidModel.Meta):
        abstract = True
        verbose_name = "Pill Bottle"
        verbose_name_plural = "Pill Bottles"
