from django.db import models
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_utils import get_utcnow
from sequences import get_next_value

from ...exceptions import ReceiveError
from .location import Location
from .order import Order
from .supplier import Supplier


class Manager(models.Manager):
    use_in_migrations = True


class Receive(BaseUuidModel):

    receive_identifier = models.CharField(
        max_length=36,
        unique=True,
        null=True,
        blank=True,
        help_text="A sequential unique identifier set by the EDC",
    )

    receive_datetime = models.DateTimeField(default=get_utcnow)

    item_count = models.IntegerField(verbose_name="Item count", null=True)

    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        limit_choices_to={"site__isnull": True},
    )

    order = models.ForeignKey(Order, on_delete=models.PROTECT, null=True, blank=False)

    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, verbose_name="Supplier", null=True, blank=False
    )

    invoice_number = models.CharField(max_length=50, null=True, blank=True)

    invoice_date = models.DateField(null=True, blank=True)

    comment = models.TextField(null=True, blank=True)

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return self.receive_identifier

    def save(self, *args, **kwargs):
        if not self.receive_identifier:
            self.receive_identifier = f"{get_next_value(self._meta.label_lower):06d}"
        if not self.order:
            raise ReceiveError("Order may not be null.")
        if not self.location:
            raise ReceiveError("Location may not be null.")
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Receive"
        verbose_name_plural = "Receive"
