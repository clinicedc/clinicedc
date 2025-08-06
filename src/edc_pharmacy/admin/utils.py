from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import StockRequest


def stock_request_status_counts(obj: StockRequest) -> dict[str, int]:
    return dict(
        total=obj.stockrequestitem_set.all().count(),
        pending=obj.stockrequestitem_set.filter(allocation__isnull=True).count(),
        allocated=(obj.stockrequestitem_set.filter(allocation__isnull=False).count()),
        allocated_and_transferred=obj.stockrequestitem_set.filter(
            allocation__isnull=False, allocation__stock__location=obj.location
        ).count(),
    )
