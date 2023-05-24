from django.db import models
from django.db.models.deletion import PROTECT
from edc_model import models as edc_models
from edc_utils import get_utcnow

from ..choices import DISPENSE_STATUS
from ..constants import DISPENSED
from ..dispense import Dispensing
from .rx_refill import RxRefill


class Manager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, rx_refill, dispensed_datetime):
        return self.get(rx_refill, dispensed_datetime)


class DispensingHistory(edc_models.BaseUuidModel):
    """A model to capture an amount dispensed against a refill"""

    rx_refill = models.ForeignKey(RxRefill, on_delete=PROTECT)

    dispensed_datetime = models.DateTimeField(default=get_utcnow)

    dispensed = models.DecimalField(max_digits=6, decimal_places=1)

    status = models.CharField(
        verbose_name="Status", max_length=25, default=DISPENSED, choices=DISPENSE_STATUS
    )

    objects = Manager()

    history = edc_models.HistoricalRecords()

    def __str__(self):
        return f"{str(self.rx_refill)}"

    def natural_key(self):
        return (
            self.rx_refill,
            self.dispensed_datetime,
        )

    def save(self, *args, **kwargs):
        # will raise an exception if nothing remaining on refill
        Dispensing(rx_refill=self.rx_refill, dispensed=self.dispensed, exclude_id=self.id)
        super().save(*args, **kwargs)

    @property
    def dispensed_date(self):
        return self.dispensed_datetime.date()

    class Meta(edc_models.BaseUuidModel.Meta):
        verbose_name = "Dispensing history"
        verbose_name_plural = "Dispensing history"
        unique_together = ["rx_refill", "dispensed_datetime"]
