from django.db import models
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_utils import get_utcnow
from sequences import get_next_value


class Manager(models.Manager):
    use_in_migrations = True


class Confirmation(BaseUuidModel):
    """Track confirmed stock items.

    Confirmed stock items are items created, labels printed, and
    `confirmed` when the label is scanned back into the EDC.

    Only confirmed stock truly exist.
    """

    confirmation_identifier = models.CharField(
        max_length=36,
        unique=True,
        null=True,
        blank=True,
        help_text="A sequential unique identifier set by the EDC",
    )

    stock = models.OneToOneField(
        "edc_pharmacy.stock",
        on_delete=models.PROTECT,
        null=True,
    )

    confirmed_datetime = models.DateTimeField(default=get_utcnow)

    confirmed_by = models.CharField(max_length=100, null=True, blank=True)

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return self.confirmation_identifier

    def save(self, *args, **kwargs):
        if not self.confirmation_identifier:
            self.confirmation_identifier = f"{get_next_value(self._meta.label_lower):06d}"
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock Confirmation"
        verbose_name_plural = "Stock Confirmations"
