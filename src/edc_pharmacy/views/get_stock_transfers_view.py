# views.py
from django.db.models import Count, Q
from django.http import JsonResponse

from ..models import StockTransfer


def get_stock_transfers_view(request):
    """Return the list of stock transfers with unconfirmed items.

    Each row includes ``unconfirmed_items`` so the
    /confirm-at-location/ entry form can compute the max for the
    "Number of items" input on reference change without a round-trip.
    """
    location_id = request.GET.get("location_id", None)
    stock_transfers = (
        StockTransfer.objects.filter(
            to_location_id=location_id,
            stocktransferitem__confirmationatlocationitem__isnull=True,
        )
        .annotate(
            count=Count("transfer_identifier"),
            unconfirmed_items_count=Count(
                "stocktransferitem",
                filter=Q(stocktransferitem__confirmationatlocationitem__isnull=True),
            ),
        )
        .values("id", "transfer_identifier", "item_count", "unconfirmed_items_count")
        .order_by("-transfer_identifier")
    )
    # Rename the annotation to a stable JSON key for the template's JS.
    payload = [
        {
            "id": row["id"],
            "transfer_identifier": row["transfer_identifier"],
            "item_count": row["item_count"],
            "unconfirmed_items": row["unconfirmed_items_count"],
        }
        for row in stock_transfers
    ]
    return JsonResponse(payload, safe=False)
