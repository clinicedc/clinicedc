from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ..exceptions import InsufficientStockError

if TYPE_CHECKING:
    from ..models import Stock


def get_unit_qty_out(stock: Stock) -> Decimal:
    """Get the unit_qty_out by summing the container qty per
    stock obj.
    """
    unit_qty_out = 0
    for stock_obj in stock.__class__.objects.filter(from_stock=stock):
        unit_qty_out += stock_obj.container.qty
    if stock.unit_qty_out > stock.unit_qty_in:
        raise InsufficientStockError(f"Unit QTY OUT cannot exceed Unit QTY IN. See {stock}.")
    return unit_qty_out
