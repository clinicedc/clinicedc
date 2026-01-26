from decimal import Decimal

from clinicedc_constants import NULL_STRING
from django.core.validators import MinValueValidator
from django.db import models
from edc_model.models import BaseUuidModel, HistoricalRecords

from .container_type import ContainerType
from .container_units import ContainerUnits


class Manager(models.Manager):
    use_in_migrations = True


class Container(BaseUuidModel):
    name = models.CharField(max_length=50, unique=True, blank=False)

    display_name = models.CharField(
        max_length=100, unique=True, default=NULL_STRING, blank=False
    )

    container_type = models.ForeignKey(ContainerType, on_delete=models.PROTECT, null=True)

    units = models.ForeignKey(ContainerUnits, on_delete=models.PROTECT, null=True)

    unit_qty_default = models.DecimalField(
        verbose_name="Default qty",
        decimal_places=2,
        max_digits=10,
        null=True,
        blank=False,
        validators=[MinValueValidator(Decimal("1.0"))],
        help_text="May be adjusted. Default value for entry form",
    )

    unit_qty_places = models.IntegerField(
        default=0.0,
        blank=False,
        validators=[MinValueValidator(0)],
        help_text="May NOT be adjusted at receiving",
    )

    unit_qty_max = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        null=True,
        blank=False,
        validators=[MinValueValidator(Decimal("1.0"))],
        help_text="Maximum unit capacity of container",
    )

    max_items_per_subject = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text=(
            "Maximum number of this container that may be "
            "allocated to a subject per stock request. "
            "(For example, no more than 3 bottles per subject)"
        ),
    )

    may_order_as = models.BooleanField(
        verbose_name="Container may be used for ordering", default=False
    )

    may_receive_as = models.BooleanField(
        verbose_name="Container may be used for receiving", default=False
    )

    may_repack_as = models.BooleanField(
        verbose_name="Container may be used for repack request", default=False
    )

    may_request_as = models.BooleanField(
        verbose_name="Container may be used for stock request",
        default=False,
    )

    may_dispense_as = models.BooleanField(
        verbose_name="Container may be used for dispensing to subject", default=False
    )

    objects = Manager()

    history = HistoricalRecords()

    def __str__(self):
        return self.display_name or self.name

    def save(self, *args, **kwargs):
        if self.may_request_as or self.may_repack_as:
            self.may_order_as = False
            self.may_receive_as = False
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Container"
        verbose_name_plural = "Containers"
