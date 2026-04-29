from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import PROTECT
from django.utils import timezone
from sequences import get_next_value

from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.model_mixins import SiteModelMixin

from .storage_bin import StorageBin

IN_PROGRESS = "in_progress"
COMPLETED = "completed"

STOCK_TAKE_STATUS = (
    (IN_PROGRESS, "In progress"),
    (COMPLETED, "Completed"),
)


class StockTake(SiteModelMixin, BaseUuidModel):
    """Records a single stock-take event for a storage bin."""

    stock_take_identifier = models.CharField(
        max_length=36,
        unique=True,
        null=True,
        blank=True,
        editable=False,
    )

    storage_bin = models.ForeignKey(
        StorageBin,
        on_delete=PROTECT,
        related_name="stock_takes",
    )

    stock_take_datetime = models.DateTimeField(default=timezone.now)

    performed_by = models.ForeignKey(
        get_user_model(),
        on_delete=PROTECT,
        null=True,
        blank=True,
        related_name="+",
    )

    status = models.CharField(
        max_length=25,
        choices=STOCK_TAKE_STATUS,
        default=IN_PROGRESS,
    )

    expected_count = models.PositiveIntegerField(
        verbose_name="Expected",
        default=0,
        help_text="Number of items registered in the bin at the time of the stock take.",
    )

    scanned_count = models.PositiveIntegerField(
        verbose_name="Scanned",
        default=0,
        help_text="Number of codes scanned during the stock take.",
    )

    matched_count = models.PositiveIntegerField(verbose_name="Matched", default=0)
    missing_count = models.PositiveIntegerField(verbose_name="Missing", default=0)
    unexpected_count = models.PositiveIntegerField(verbose_name="Unexpected", default=0)

    note = models.TextField(default="", blank=True)

    history = HistoricalRecords()

    def __str__(self):
        return (
            f"{self.stock_take_identifier}: {self.storage_bin} ({self.get_status_display()})"
        )

    def save(self, *args, **kwargs):
        if not self.stock_take_identifier:
            self.stock_take_identifier = f"ST-{get_next_value(self._meta.label_lower):06d}"
        self.site = self.storage_bin.location.site
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock take"
        verbose_name_plural = "Stock takes"
        ordering = ("-stock_take_datetime",)
