from django.db import models
from edc_model.models import BaseUuidModel
from edc_utils import get_utcnow
from sequences import get_next_value

from ...exceptions import StockTransferError
from .location import Location
from .stock import Stock


class StockTransfer(BaseUuidModel):
    """A model to track allocated stock transfers from location A
    to location B.
    """

    transfer_identifier = models.CharField(max_length=36, unique=True, null=True, blank=True)

    transfer_datetime = models.DateTimeField(default=get_utcnow)

    stock = models.OneToOneField(
        Stock,
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        limit_choices_to={"allocation__isnull": False},
    )

    from_location = models.ForeignKey(
        Location, on_delete=models.PROTECT, null=True, blank=False
    )
    to_location = models.ForeignKey(Location, on_delete=models.PROTECT, null=True, blank=False)

    def __str__(self):
        return self.transfer_identifier

    def save(self, *args, **kwargs):
        if not self.transfer_identifier:
            self.transfer_identifier = f"{get_next_value(self._meta.label_lower):06d}"
            if self.stock.location != self.from_location:
                raise StockTransferError(
                    "Location mismatch. Current stock location must match "
                    "`from_location. Perhaps catch this in the form"
                )
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Allocation"
        verbose_name_plural = "Allocations"
