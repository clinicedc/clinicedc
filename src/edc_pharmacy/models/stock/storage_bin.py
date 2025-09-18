from __future__ import annotations

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import PROTECT
from django.utils import timezone
from sequences import get_next_value

from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.model_mixins import SiteModelMixin

from .location import Location


class StorageBin(SiteModelMixin, BaseUuidModel):
    bin_identifier = models.CharField(
        max_length=36,
        unique=True,
        null=True,
        blank=True,
        help_text="A sequential unique identifier set by the EDC",
    )

    bin_datetime = models.DateTimeField(default=timezone.now)

    name = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        unique=True,
        help_text="May be left blank or set to any unique name.",
    )

    location = models.ForeignKey(Location, on_delete=PROTECT, null=True, blank=False)

    capacity = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])

    in_use = models.BooleanField(default=True)

    description = models.CharField(max_length=100, default="", blank=True)

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.location.site.id}:{self.bin_identifier}"

    def save(self, *args, **kwargs):
        self.site = self.location.site
        if not self.id:
            self.bin_identifier = f"{get_next_value(self._meta.label_lower):06d}"
        if not self.name:
            self.name = self.bin_identifier
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Storage bin"
        verbose_name_plural = "Storage bins"
