from django.db import models
from django.utils import timezone
from sequences import get_next_value

from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.model_mixins import SiteModelMixin

from ...exceptions import ConfirmAtSiteError
from .confirmation_at_site import ConfirmationAtSite
from .stock import Stock


class Manager(models.Manager):
    use_in_migrations = True


class ConfirmationAtSiteItem(SiteModelMixin, BaseUuidModel):
    confirmation_at_site = models.ForeignKey(ConfirmationAtSite, on_delete=models.PROTECT)

    transfer_confirmation_item_identifier = models.CharField(
        max_length=36,
        unique=True,
        null=True,
        blank=True,
        help_text="A sequential unique identifier set by the EDC",
    )

    transfer_confirmation_item_datetime = models.DateTimeField(default=timezone.now)

    stock = models.OneToOneField(Stock, on_delete=models.PROTECT)

    confirmed_datetime = models.DateTimeField(null=True, blank=True)

    confirmed_by = models.CharField(max_length=150, default="", blank=True)

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.transfer_confirmation_item_identifier} {self.stock.code}"

    def save(self, *args, **kwargs):
        self.site = self.confirmation_at_site.site
        if not self.transfer_confirmation_item_identifier:
            next_id = get_next_value(self._meta.label_lower)
            self.transfer_confirmation_item_identifier = f"{next_id:010d}"
        if (
            self.confirmation_at_site.location.site
            != self.stock.allocation.registered_subject.site
        ):
            raise ConfirmAtSiteError(
                "Location mismatch. Cannot confirm stock item at this location. "
                f"Got {self.stock}."
            )
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock Confirmation at Site Item"
        verbose_name_plural = "Stock Confirmation at Site Items"
