from clinicedc_constants import NULL_STRING
from django.db import models
from django.utils import timezone
from sequences import get_next_value

from edc_model.models import BaseUuidModel, HistoricalRecords

from ...exceptions import ReturnError
from .location import Location


class Manager(models.Manager):
    use_in_migrations = True


class ReturnRequest(BaseUuidModel):
    """A model to track stock returns from a site location back to central."""

    return_identifier = models.CharField(
        max_length=36,
        unique=True,
        null=True,
        blank=True,
        help_text="A sequential unique identifier set by the EDC",
    )

    return_datetime = models.DateTimeField(default=timezone.now)

    from_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        related_name="return_from_location",
        help_text="Location returning the stock (usually a site)",
    )
    to_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        related_name="return_to_location",
        help_text="Destination location (usually central)",
    )

    item_count = models.PositiveIntegerField(
        null=True, blank=False, help_text="Expected number of items to return"
    )

    comment = models.TextField(
        max_length=255,
        default=NULL_STRING,
        blank=True,
    )

    cancel = models.CharField(
        verbose_name="To cancel this return, type 'CANCEL'",
        max_length=15,
        default=NULL_STRING,
        blank=True,
        help_text="Leave blank. Otherwise type 'CANCEL' to cancel this return.",
    )

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return self.return_identifier

    def save(self, *args, **kwargs):
        if not self.return_identifier:
            self.return_identifier = f"{get_next_value(self._meta.label_lower):06d}"
            if self.from_location == self.to_location:
                raise ReturnError("Locations cannot be the same")
        super().save(*args, **kwargs)

    @property
    def received_item_count(self) -> int:
        return self.returnitem_set.count()

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Return request"
        verbose_name_plural = "Return requests"
