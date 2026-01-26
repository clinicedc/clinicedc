from clinicedc_constants import NULL_STRING
from django.db import models
from django.utils import timezone
from edc_model.models import BaseUuidModel, HistoricalRecords
from sequences import get_next_value

from ...exceptions import StockTransferError
from .location import Location


class Manager(models.Manager):
    use_in_migrations = True


class StockTransfer(BaseUuidModel):
    """A model to track allocated stock transfers from Central
    to a site location.
    """

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

    transfer_datetime = models.DateTimeField(default=timezone.now)

    from_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        related_name="from_location",
        # limit_choices_to={"site__isnull": True},
    )
    to_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        related_name="to_location",
        # limit_choices_to={"site__isnull": False},
    )

    item_count = models.PositiveIntegerField(
        null=True, blank=False, help_text="Suggested item count"
    )

    comment = models.TextField(
        max_length=255,
        default=NULL_STRING,
        blank=True,
    )

    cancel = models.CharField(
        verbose_name="To cancel this transfer, type 'CANCEL'",
        max_length=15,
        default=NULL_STRING,
        blank=True,
        help_text="Leave blank. Otherwise type 'CANCEL' to cancel this transfer.",
    )

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return self.transfer_identifier

    def save(self, *args, **kwargs):
        if not self.transfer_identifier:
            self.transfer_identifier = f"{get_next_value(self._meta.label_lower):06d}"
            if self.from_location == self.to_location:
                raise StockTransferError("Locations cannot be the same")
        super().save(*args, **kwargs)

    @property
    def export_references(self):
        return "Export ref"

    @property
    def shipped(self):
        return False

    @property
    def export_datetime(self):
        return timezone.now()

    @property
    def site(self):
        class Dummy:
            name = "sitename"

        return Dummy()

    @property
    def consignee(self):
        class Dummy:
            country = "Tanzania"

        return Dummy()

    @property
    def shipper(self):
        return {
            "contact_name": "Deus Buma",
            "name": "META III Central Pharmacy",
            "address": "",
            "city": "",
            "state": "",
            "postal_code": "0000",
            "country": "Tanzania",
        }

    @property
    def confirmed_items(self) -> int:
        return self.stocktransferitem_set.filter(
            confirmationatlocationitem__isnull=False
        ).count()

    @property
    def unconfirmed_items(self) -> int:
        return self.stocktransferitem_set.filter(
            confirmationatlocationitem__isnull=True
        ).count()

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock transfer"
        verbose_name_plural = "Stock transfers"
