from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import Container


def format_qty(qty: Decimal, container: Container):
    qty = 0 if qty is None else qty
    if container.qty_decimal_places == 0:
        return str(int(qty))
    if container.qty_decimal_places == 1:
        return f"{qty:0.1f}"
    return f"{qty:0.2f}"


__all__ = ["format_qty"]
