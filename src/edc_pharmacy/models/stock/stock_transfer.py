from django.db import models
from edc_model.models import BaseUuidModel
from edc_utils import get_utcnow
from sequences import get_next_value

from ...exceptions import StockTransferError
from .location import Location


class StockTransfer(BaseUuidModel):
    """A model to track allocated stock transfers from location A
    to location B.
    """

    transfer_identifier = models.CharField(
        max_length=36,
        unique=True,
        null=True,
        blank=True,
        help_text="A sequential unique identifier set by the EDC",
    )

    transfer_datetime = models.DateTimeField(default=get_utcnow)

    from_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        related_name="from_location",
        limit_choices_to={"site__isnull": True},
    )
    to_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        related_name="to_location",
        limit_choices_to={"site__isnull": False},
    )

    item_count = models.PositiveIntegerField(null=True, blank=False)

    def __str__(self):
        return self.transfer_identifier

    def save(self, *args, **kwargs):
        if not self.transfer_identifier:
            self.transfer_identifier = f"{get_next_value(self._meta.label_lower):06d}"
            if self.from_location == self.to_location:
                raise StockTransferError("Locations cannot be the same")
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock transfer"
        verbose_name_plural = "Stock transfers"
