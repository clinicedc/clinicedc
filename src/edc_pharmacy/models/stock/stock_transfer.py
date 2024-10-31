import random

import edc_model.models
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import gettext as _
from edc_constants.constants import CLOSED, OPEN
from edc_model.models import BaseUuidModel
from edc_sites.model_mixins import SiteModelMixin
from sequences import Sequence

from ..medication import Lot

random.seed(7685140)

STATUS = (
    (OPEN, _("Open")),
    (CLOSED, _("Closed")),
)


class StockTransfer(SiteModelMixin, BaseUuidModel):
    """A user model for a stock transfer.

    A stock transfer is limited to a given `lot` and `site`.

    Identifier might be better as a sequence
    """

    stock_transfer_identifier = models.CharField(
        verbose_name="Stock transfer identifier", max_length=15, null=True
    )

    lot = models.ForeignKey(Lot, on_delete=models.PROTECT)

    site = models.ForeignKey(Site, on_delete=models.PROTECT)

    status = models.CharField(max_length=15, choices=STATUS, default=OPEN)

    history = edc_model.models.HistoricalRecords()

    def __str__(self):
        return self.stock_transfer_identifier

    def save(self, *args, **kwargs):
        if not self.id:
            stock_transfer_sequence = Sequence("stock_transfer_sequence")
            self.stock_transfer_identifier = f"ST{self.site.id}-{stock_transfer_sequence}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "IMP stock transfer"
        verbose_name_plural = "IMP  stock transfers"
