from clinicedc_constants import NEW
from django.core.validators import MinValueValidator
from django.db import models
from sequences import get_next_value

from edc_model.models import BaseUuidModel, HistoricalRecords

from ...choices import ORDER_CHOICES
from .supplier import Supplier


class Manager(models.Manager):
    use_in_migrations = True


class Order(BaseUuidModel):
    order_identifier = models.CharField(
        max_length=36,
        unique=True,
        null=True,
        blank=True,
        help_text="A sequential unique identifier set by the EDC",
    )

    order_datetime = models.DateTimeField(verbose_name="Order date/time")

    item_count = models.IntegerField(
        verbose_name="Item count",
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Cached count of order items. Updated automatically by signal.",
    )

    title = models.CharField(
        max_length=50,
        default="",
        blank=False,
        help_text="A short description of this order",
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        verbose_name="Supplier",
        null=True,
        blank=False,
    )
    comment = models.TextField(default="", blank=True)

    printed = models.BooleanField(
        default=False,
        help_text="Set automatically when the PDF is first printed.",
    )

    printed_datetime = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of the first PDF print.",
    )

    printed_by = models.CharField(
        max_length=150,
        default="",
        blank=True,
        help_text="Username that triggered the first PDF print.",
    )

    status = models.CharField(
        max_length=25,
        choices=ORDER_CHOICES,
        default=NEW,
        help_text="Updates in the signal",
    )

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.order_identifier}"

    def save(self, *args, **kwargs):
        if not self.order_identifier:
            self.order_identifier = f"{get_next_value(self._meta.label_lower):06d}"
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Order"
        verbose_name_plural = "Orders"
