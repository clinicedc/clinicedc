from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django.apps import apps as django_apps

from .get_unit_qty_out import get_unit_qty_out

if TYPE_CHECKING:
    from ..models import Allocation, Stock, StockAdjustment


def get_allocation_model_cls() -> Allocation:
    return django_apps.get_model("edc_pharmacy.allocation")


def get_stockadjustment_model_cls() -> StockAdjustment:
    return django_apps.get_model("edc_pharmacy.stockadjustment")


def update_stock_instance(stock: Stock) -> Stock:
    """Update stock instance fields 'unit_qty_in', 'unit_qty_out',
    'qty', 'qty_out'
    """
    # check if unit_qty_in has been manually adjusted or not
    if get_stockadjustment_model_cls().objects.filter(stock=stock).exists():
        # use adjusted value
        stock.unit_qty_in = (
            get_stockadjustment_model_cls()
            .objects.filter(stock=stock)
            .order_by("adjustment_datetime")
            .last()
            .unit_qty_in_new
        )
    else:
        # confirm default value from container definition
        stock.unit_qty_in = Decimal(stock.qty_in) * Decimal(stock.container.qty)
    # recalculate unit_qty_out
    stock.unit_qty_out = get_unit_qty_out(stock)
    # update overall container quantity if in-out==0
    if stock.unit_qty_out == stock.unit_qty_in:
        stock.qty_out = 1
        stock.qty = 0
    stock.save(update_fields=["unit_qty_in", "unit_qty_out", "qty", "qty_out"])
    stock.refresh_from_db()
    return stock
