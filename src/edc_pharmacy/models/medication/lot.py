from django.db import models
from django.db.models import PROTECT
from edc_model.models import BaseUuidModel, HistoricalRecords

from .assignment import Assignment
from .formulation import Formulation


class Manager(models.Manager):
    use_in_migrations = True


class Lot(BaseUuidModel):

    lot_no = models.CharField(max_length=50, unique=True)

    assignment = models.ForeignKey(Assignment, on_delete=models.PROTECT, null=True, blank=True)

    expiration_date = models.DateField()

    formulation = models.ForeignKey(Formulation, on_delete=PROTECT)

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.formulation} Lot {self.lot_no}"

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Lot"
        verbose_name_plural = "Lots"
