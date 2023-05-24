from django.db import models
from django.db.models import PROTECT
from django_crypto_fields.fields import EncryptedCharField
from edc_model.models import BaseUuidModel, HistoricalRecords

from .formulation import Formulation


class Manager(models.Manager):
    use_in_migrations = True


class MedicationLot(BaseUuidModel):
    lot_no = models.CharField(max_length=50, unique=True)

    assignment = EncryptedCharField(null=True)

    expiration_date = models.DateField()

    formulation = models.ForeignKey(Formulation, on_delete=PROTECT)

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.formulation} Lot {self.lot_no}"

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Medication lot"
        verbose_name_plural = "Medication lots"
