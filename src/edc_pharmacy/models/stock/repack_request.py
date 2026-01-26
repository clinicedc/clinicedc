from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from edc_model.models import BaseUuidModel, HistoricalRecords
from sequences import get_next_value

from ...exceptions import RepackRequestError
from .container import Container


class Manager(models.Manager):
    use_in_migrations = True


class RepackRequest(BaseUuidModel):
    """A model to repack stock from one container into another.

    Move stock from one phycical container into another, for example
    move stock from a bottle of 50000 into x number of containers
    of 128.

    Location is not changed here.
    """

    repack_identifier = models.CharField(
        max_length=36,
        unique=True,
        null=True,
        blank=True,
        help_text="A sequential unique identifier set by the EDC",
    )

    repack_datetime = models.DateTimeField(default=timezone.now)

    from_stock = models.ForeignKey(
        "edc_pharmacy.stock",
        on_delete=models.PROTECT,
        related_name="repack_requests",
        null=True,
        blank=False,
        limit_choices_to={"repack_request__isnull": True},
    )

    container = models.ForeignKey(
        Container,
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        limit_choices_to={"may_repack_as": True},
    )

    container_unit_qty = models.DecimalField(
        verbose_name="Container unit quantity",
        decimal_places=2,
        max_digits=10,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("1.0"))],
        help_text="Leave blank for default.",
    )

    override_container_unit_qty = models.BooleanField(default=False)

    item_qty_repack = models.IntegerField(
        verbose_name="Number of containers to repack",
        null=True,
        blank=False,
        validators=[MinValueValidator(0)],
    )

    item_qty_processed = models.IntegerField(
        verbose_name="Number of containers processed", blank=False, default=0
    )

    unit_qty_processed = models.DecimalField(
        verbose_name="Unit quantity processed",
        default=Decimal("0.0"),
        blank=False,
        decimal_places=2,
        max_digits=10,
        help_text="Automatically calculated",
    )

    stock_count = models.IntegerField(null=True, blank=True)

    task_id = models.UUIDField(null=True)

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return self.repack_identifier

    def save(self, *args, **kwargs):
        if not self.repack_identifier:
            next_id = get_next_value(self._meta.label_lower)
            self.repack_identifier = f"{next_id:06d}"
            self.processed = False
        if not self.from_stock.confirmed:
            raise RepackRequestError(
                "Unconfirmed stock item. Only confirmed stock items may "
                "be used to repack. Perhaps catch this in the form"
            )
        self.container_unit_qty = self.container_unit_qty or self.container.unit_qty_default
        self.item_qty_processed = (
            0 if self.item_qty_processed is None else self.item_qty_processed
        )
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Repack request"
        verbose_name_plural = "Repack request"
