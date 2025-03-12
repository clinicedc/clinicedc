from django.db import models
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.model_mixins import SiteModelMixin
from edc_utils import get_utcnow
from sequences import get_next_value

from ..stock import Stock
from .stock_transfer_confirmation import StockTransferConfirmation


class Manager(models.Manager):
    use_in_migrations = True


class StockTransferConfirmationItem(SiteModelMixin, BaseUuidModel):

    stock_transfer_confirmation = models.ForeignKey(
        StockTransferConfirmation, on_delete=models.PROTECT
    )

    transfer_confirmation_item_identifier = models.CharField(
        max_length=36,
        unique=True,
        null=True,
        blank=True,
        help_text="A sequential unique identifier set by the EDC",
    )

    transfer_confirmation_item_datetime = models.DateTimeField(default=get_utcnow)

    stock = models.OneToOneField(Stock, on_delete=models.PROTECT)

    confirmed_datetime = models.DateTimeField(null=True, blank=True)

    confirmed_by = models.CharField(max_length=150, null=True, blank=True)

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return self.transfer_confirmation_item_identifier

    def save(self, *args, **kwargs):
        self.site = self.stock_transfer_confirmation.site
        if not self.transfer_confirmation_item_identifier:
            next_id = get_next_value(self._meta.label_lower)
            self.transfer_confirmation_item_identifier = f"{next_id:010d}"
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock Transfer Confirmation Item"
        verbose_name_plural = "Stock Transfer Confirmation Items"
