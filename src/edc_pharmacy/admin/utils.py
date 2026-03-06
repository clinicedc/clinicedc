from __future__ import annotations

from typing import TYPE_CHECKING

from django.urls import reverse

if TYPE_CHECKING:
    from ..models import StockRequest


def stock_request_status_counts(obj: StockRequest) -> dict[str, int]:
    url = reverse("edc_pharmacy_admin:edc_pharmacy_stockrequestitem_changelist")
    url = f"{url}?q={obj.request_identifier}"
    return dict(
        total=obj.stockrequestitem_set.all().count(),
        pending=obj.stockrequestitem_set.filter(allocation__isnull=True).count(),
        allocated=(obj.stockrequestitem_set.filter(allocation__isnull=False).count()),
        allocated_and_transferred=obj.stockrequestitem_set.filter(
            allocation__isnull=False,
            allocation__stock__location=obj.location,
            allocation__stock__stocktransferitem__isnull=False,
        ).count(),
        url=url,
    )
