from __future__ import annotations

from clinicedc_constants import NULL_STRING
from django.db import models
from django.utils import timezone
from sequences import get_next_value

from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.model_mixins import SiteModelMixin

from .storage_bin import StorageBin


class StorageBinItem(SiteModelMixin, BaseUuidModel):
    item_identifier = models.CharField(
        max_length=36,
        unique=True,
        null=True,
        blank=True,
        help_text="A sequential unique identifier set by the EDC",
    )

    item_datetime = models.DateTimeField(default=timezone.now)

    storage_bin = models.ForeignKey(StorageBin, on_delete=models.PROTECT)

    stock = models.OneToOneField(
        "edc_pharmacy.stock",
        on_delete=models.PROTECT,
        null=True,
        # limit_choices_to={
        #     "confirmationatlocationitem__isnull": False,
        #     "dispenseitem__isnull": True,
        # },
    )

    code = models.CharField(
        verbose_name="Stock code",
        max_length=15,
        # unique=True,
        default=NULL_STRING,
        blank=True,
        editable=False,
    )

    history = HistoricalRecords()

    def __str__(self):
        location = (
            self.storage_bin.location.site.id
            if self.storage_bin.location.site
            else self.storage_bin.location.name
        )
        return f"{location}:{self.storage_bin.bin_identifier}:{self.item_identifier}"

    def save(self, *args, **kwargs):
        self.site = self.storage_bin.location.site
        self.code = self.stock.code
        if not self.id:
            self.item_identifier = f"{get_next_value(self._meta.label_lower):06d}"
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Storage bin item"
        verbose_name_plural = "Storage bin items"
