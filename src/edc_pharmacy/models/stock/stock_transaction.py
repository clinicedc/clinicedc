from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils import timezone
from edc_list_data.model_mixins import BaseListModelMixin, ListModelMixin
from edc_model.models import BaseUuidModel

from .stock import Stock


class StockTransactionType(ListModelMixin):
    class Meta(BaseListModelMixin.Meta):
        verbose_name = "Stock transaction type"
        verbose_name_plural = "Stock transaction types"


class StockTransaction(BaseUuidModel):
    stock = models.ForeignKey(Stock, on_delete=models.PROTECT)

    transaction_datetime = models.DateTimeField(default=timezone.now)

    transaction_type = models.ForeignKey(StockTransactionType, on_delete=models.PROTECT)

    transaction_qty = models.DecimalField(
        blank=False,
        decimal_places=2,
        max_digits=20,
        default=Decimal("0.0"),
    )

    balance = models.DecimalField(
        blank=False,
        decimal_places=2,
        max_digits=20,
        default=Decimal("0.0"),
    )

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Stock transaction"
        verbose_name_plural = "Stock transactions"
