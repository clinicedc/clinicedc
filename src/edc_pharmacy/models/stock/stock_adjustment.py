from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_utils import get_utcnow

from .stock import Stock


class StockAdjustmentManager(models.Manager):
    pass


class StockAdjustment(BaseUuidModel):

    stock = models.ForeignKey(
        Stock,
        # related_name="source_stock",
        on_delete=models.PROTECT,
        null=True,
    )

    adjustment_datetime = models.DateTimeField(default=get_utcnow)

    unit_qty_in_old = models.DecimalField(
        decimal_places=2,
        max_digits=20,
        default=Decimal(0.0),
        validators=[MinValueValidator(0)],
    )

    unit_qty_in_new = models.DecimalField(
        decimal_places=2,
        max_digits=20,
        default=Decimal(0.0),
        validators=[MinValueValidator(0)],
    )

    reason = models.TextField(null=True)

    objects = StockAdjustmentManager()

    history = HistoricalRecords()

    def __str__(self):
        return (
            f"Stock Adjustment for {self.stock.code}. "
            f"{self.unit_qty_in_old}->{self.unit_qty_in_new}."
        )

    def save(self, *args, **kwargs):
        self.unit_qty_in_new = (
            Stock.objects.filter(from_stock=self.stock)
            .aggregate(unit_qty_in=Sum("unit_qty_in"))
            .get("unit_qty_in")
        )
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Stock Adjustments"
        verbose_name = "Stock Adjustment"
