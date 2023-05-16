from django.db import models
from django.db.models.deletion import PROTECT
from edc_model import models as edc_models
from edc_utils import get_utcnow

from .rx_refill import RxRefill


class ReturnError(Exception):
    pass


class Manager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, prescription_item, return_datetime):
        return self.get(prescription_item, return_datetime)


class ReturnHistory(edc_models.BaseUuidModel):
    rx_refill = models.ForeignKey(RxRefill, on_delete=PROTECT)

    return_datetime = models.DateTimeField(default=get_utcnow)

    returned = models.DecimalField(max_digits=6, decimal_places=1)

    objects = Manager()

    history = edc_models.HistoricalRecords()

    def __str__(self):
        return f"{str(self.rx_refill)}"

    def natural_key(self):
        return (
            self.rx_refill,
            self.return_datetime,
        )

    # TODO: calculate to verify number of returns makes sense
    # def save(self, *args, **kwargs):
    #     if self.prescription_item.get_remaining(exclude_id=self.id) < self.returned:
    #         raise ReturnError("Attempt to return more than prescribed.")
    #     super().save(*args, **kwargs)

    @property
    def return_date(self):
        return self.return_datetime.date()

    class Meta(edc_models.BaseUuidModel.Meta):
        verbose_name = "Return history"
        verbose_name_plural = "Return history"
        unique_together = ["rx_refill", "return_datetime"]
