from django.db import models
from django.db.models.deletion import PROTECT
from edc_model import models as edc_models
from edc_pharmacy.constants import DISPENSED
from edc_utils import get_utcnow

from ..choices import DISPENSE_STATUS
from .prescription_item import PrescriptionItem


class Manager(models.Manager):

    use_in_migrations = True

    def get_by_natural_key(self, prescription_item, dispensed_datetime):
        return self.get(prescription_item, dispensed_datetime)


class DispenseError(Exception):
    pass


class DispensingHistory(edc_models.BaseUuidModel):

    prescription_item = models.ForeignKey(PrescriptionItem, on_delete=PROTECT)

    dispensed_datetime = models.DateTimeField(default=get_utcnow)

    dispensed = models.DecimalField(max_digits=6, decimal_places=1)

    status = models.CharField(
        verbose_name="Status", max_length=25, default=DISPENSED, choices=DISPENSE_STATUS
    )

    objects = Manager()

    history = edc_models.HistoricalRecords()

    def __str__(self):
        return f"{str(self.prescription_item)}"

    def natural_key(self):
        return (
            self.prescription_item,
            self.dispensed_datetime,
        )

    def save(self, *args, **kwargs):
        if self.prescription_item.get_remaining(exclude_id=self.id) < self.dispensed:
            raise DispenseError("Attempt to dispense more than prescribed.")
        super().save(*args, **kwargs)

    @property
    def dispensed_date(self):
        return self.dispensed_datetime.date()

    class Meta(edc_models.BaseUuidModel.Meta):
        verbose_name = "Dispensing history"
        verbose_name_plural = "Dispensing history"
        unique_together = ["prescription_item", "dispensed_datetime"]
