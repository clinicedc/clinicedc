from django.db import models
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.model_mixins import SiteModelMixin
from edc_utils import get_utcnow
from sequences import get_next_value

from ...exceptions import StockTransferConfirmationError
from .location import Location
from .stock_transfer import StockTransfer


class Manager(models.Manager):
    use_in_migrations = True


class ConfirmationAtSite(SiteModelMixin, BaseUuidModel):

    transfer_confirmation_identifier = models.CharField(
        max_length=36,
        unique=True,
        null=True,
        blank=True,
        help_text="A sequential unique identifier set by the EDC",
    )

    transfer_confirmation_datetime = models.DateTimeField(default=get_utcnow)

    stock_transfer = models.OneToOneField(StockTransfer, on_delete=models.PROTECT)

    location = models.ForeignKey(
        Location, on_delete=models.PROTECT, limit_choices_to={"site__isnull": False}
    )

    comments = models.TextField(null=True, blank=True)

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return self.transfer_confirmation_identifier

    def save(self, *args, **kwargs):
        if self.location != self.stock_transfer.to_location:
            raise StockTransferConfirmationError(
                "Location mismatch. Perhaps catch this in the form."
            )
        self.site = self.location.site
        if not self.transfer_confirmation_identifier:
            next_id = get_next_value(self._meta.label_lower)
            self.transfer_confirmation_identifier = f"{next_id:06d}"
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock Confirmation at Site "
        verbose_name_plural = "Stock Confirmations at Site"
