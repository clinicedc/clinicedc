from django.db import models
from edc_model.models import BaseUuidModel, HistoricalRecords
from sequences import get_next_value

from ..stock import Stock


class Manager(models.Manager):
    use_in_migrations = True


class StockTransferConfirmation(BaseUuidModel):

    transfer_confirmation_identifier = models.CharField(
        max_length=36,
        unique=True,
        null=True,
        blank=True,
        help_text="A sequential unique identifier set by the EDC",
    )

    stock = models.OneToOneField(Stock, on_delete=models.PROTECT)

    confirmed_datetime = models.DateTimeField(null=True, blank=True)
    confirmed_by = models.CharField(max_length=150, null=True, blank=True)
    objects = Manager()

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.transfer_confirmation_identifier:
            next_id = get_next_value(self._meta.label_lower)
            self.transfer_confirmation_identifier = f"{next_id:010d}"
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock Transfer Confirmation"
        verbose_name_plural = "Stock Transfer Confirmations"
