from clinicedc_constants import NULL_STRING
from django.db import models
from django.utils import timezone
from sequences import get_next_value

from edc_model.models import BaseUuidModel, HistoricalRecords

from ...exceptions import StockTransferError
from .stock import Stock
from .stock_transaction import StockTransaction
from .stock_transfer import StockTransfer


class Manager(models.Manager):
    use_in_migrations = True


class StockTransferItem(BaseUuidModel):
    """A model to track allocated stock items transfered from Central
    to a site location.
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

    stock = models.ForeignKey(
        Stock,
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        # Sticky-pointer policy: stock.allocation can be set on dispensed /
        # damaged / etc. bottles. For transfer eligibility we want only
        # currently-active allocations, so also require ended_datetime IS NULL.
        limit_choices_to={
            "allocation__isnull": False,
            "allocation__ended_datetime__isnull": True,
        },
    )

    code = models.CharField(
        verbose_name="Stock code",
        max_length=15,
        default=NULL_STRING,
        blank=True,
        editable=False,
    )

    def __str__(self):
        return self.transfer_item_identifier

    def save(self, *args, **kwargs):
        self.code = self.stock.code
        if not self.transfer_item_identifier:
            self.transfer_item_identifier = f"{get_next_value(self._meta.label_lower):06d}"
            if self.stock.location != self.stock_transfer.from_location:
                raise StockTransferError(
                    "Location mismatch. Current stock location must match "
                    "`from_location. Perhaps catch this in the form"
                )
        super().save(*args, **kwargs)

    objects = Manager()

    history = HistoricalRecords()

    @property
    def subject_identifier(self) -> str:
        txn = self.stock.transactions.filter(to_allocation__isnull=False).first()
        if txn:
            return txn.to_allocation.subject_identifier
        return ""

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock transfer item"
        verbose_name_plural = "Stock transfer items"
