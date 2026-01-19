from clinicedc_constants import NULL_STRING
from django.db import models
from django.utils import timezone
from sequences import get_next_value

from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.model_mixins import SiteModelMixin

from ...constants import CENTRAL_LOCATION
from ...exceptions import ConfirmAtLocationError
from .confirmation_at_location import ConfirmationAtLocation
from .stock import Stock
from .stock_transfer_item import StockTransferItem


class Manager(models.Manager):
    use_in_migrations = True


class ConfirmationAtLocationItem(SiteModelMixin, BaseUuidModel):
    confirm_at_location = models.ForeignKey(ConfirmationAtLocation, on_delete=models.PROTECT)

    transfer_confirmation_item_identifier = models.CharField(
        max_length=36,
        unique=True,
        null=True,
        blank=True,
        help_text="A sequential unique identifier set by the EDC",
    )

    transfer_confirmation_item_datetime = models.DateTimeField(default=timezone.now)

    stock = models.OneToOneField(Stock, on_delete=models.PROTECT, null=True)

    code = models.CharField(
        verbose_name="Stock code",
        max_length=15,
        default=NULL_STRING,
        blank=True,
        editable=False,
    )

    location_name = models.CharField(
        verbose_name="Location name",
        max_length=100,
        default=NULL_STRING,
        blank=True,
        editable=False,
    )

    stock_transfer_item = models.OneToOneField(
        StockTransferItem, on_delete=models.PROTECT, null=True
    )

    confirmed_datetime = models.DateTimeField(null=True, blank=True)

    confirmed_by = models.CharField(max_length=150, default="", blank=True)

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.transfer_confirmation_item_identifier} {self.code}"

    def save(self, *args, **kwargs):
        self.code = self.stock_transfer_item.stock.code
        self.location_name = self.confirm_at_location.location.name
        self.site = self.confirm_at_location.site
        if not self.stock_transfer_item:
            raise ConfirmAtLocationError(
                "Field Stock transfer item may not be null. "
                f"Got {self.stock_transfer_item.stock.code}."
            )

        if not self.transfer_confirmation_item_identifier:
            next_id = get_next_value(self._meta.label_lower)
            self.transfer_confirmation_item_identifier = f"{next_id:010d}"
        if not (
            (
                self.confirm_at_location.location.site
                == self.stock_transfer_item.stock.allocation.registered_subject.site
            )
            or (self.confirm_at_location.location.name == CENTRAL_LOCATION)
        ):
            raise ConfirmAtLocationError(
                "Location mismatch. Cannot confirm stock item at this location. "
                f"Got {self.stock_transfer_item.stock.code}."
            )
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock confirmation item at location"
        verbose_name_plural = "Stock confirmation items at location"
