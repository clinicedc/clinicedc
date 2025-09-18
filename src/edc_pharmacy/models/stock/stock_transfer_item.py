from django.db import models
from django.utils import timezone
from sequences import get_next_value

from edc_model.models import BaseUuidModel, HistoricalRecords

from ...exceptions import StockTransferError
from .stock import Stock
from .stock_transfer import StockTransfer


class Manager(models.Manager):
    use_in_migrations = True


class StockTransferItem(BaseUuidModel):
    """A model to track allocated stock transfers from location A
    to location B.
    """

    transfer_item_identifier = models.CharField(
        max_length=36,
        unique=True,
        null=True,
        blank=True,
        help_text="A sequential unique identifier set by the EDC",
    )

    transfer_item_datetime = models.DateTimeField(default=timezone.now)

    stock_transfer = models.ForeignKey(StockTransfer, on_delete=models.PROTECT)

    stock = models.OneToOneField(
        Stock,
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        limit_choices_to={"allocation__isnull": False},
    )

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return self.transfer_item_identifier

    def save(self, *args, **kwargs):
        if not self.transfer_item_identifier:
            self.transfer_item_identifier = f"{get_next_value(self._meta.label_lower):06d}"
            if self.stock.location != self.stock_transfer.from_location:
                raise StockTransferError(
                    "Location mismatch. Current stock location must match "
                    "`from_location. Perhaps catch this in the form"
                )
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock transfer item"
        verbose_name_plural = "Stock transfer items"
