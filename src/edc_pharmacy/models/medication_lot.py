from django.db import models
from django.db.models import PROTECT
from edc_model import models as edc_models

from .formulation import Formulation


class Manager(models.Manager):

    use_in_migrations = True


class MedicationLot(edc_models.BaseUuidModel):

    lot_no = models.CharField(max_length=50, unique=True)

    expiration_date = models.DateField()

    formulation = models.ForeignKey(Formulation, on_delete=PROTECT)

    objects = Manager()

    history = edc_models.HistoricalRecords()

    def __str__(self):
        return self.lot_no

    class Meta(edc_models.BaseUuidModel.Meta):
        verbose_name = "Medication lot"
        verbose_name_plural = "Medication lots"
