from clinicedc_constants import NULL_STRING
from django.db import models
from django.utils import timezone
from sequences import get_next_value

from edc_model.models import BaseUuidModel, HistoricalRecords

from ...exceptions import ReturnError
from .return_request import ReturnRequest
from .stock import Stock


class Manager(models.Manager):
    use_in_migrations = True


class ReturnItem(BaseUuidModel):
    """A single stock item included in a return request."""

    return_item_identifier = models.CharField(
        max_length=36,
        unique=True,
        null=True,
        blank=True,
        help_text="A sequential unique identifier set by the EDC",
    )

    return_item_datetime = models.DateTimeField(default=timezone.now)

    return_request = models.ForeignKey(ReturnRequest, on_delete=models.PROTECT)

    stock = models.ForeignKey(
        Stock,
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        limit_choices_to={"return_requested": True},
    )

    code = models.CharField(
        verbose_name="Stock code",
        max_length=15,
        default=NULL_STRING,
        blank=True,
        editable=False,
    )

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return self.return_item_identifier

    def save(self, *args, **kwargs):
        self.code = self.stock.code
        if not self.return_item_identifier:
            self.return_item_identifier = f"{get_next_value(self._meta.label_lower):06d}"
            if self.stock.location != self.return_request.from_location:
                raise ReturnError(
                    "Location mismatch. Current stock location must match "
                    "`from_location`. Perhaps catch this in the form."
                )
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Return item"
        verbose_name_plural = "Return items"
