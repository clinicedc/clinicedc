# views.py
from django.db.models import Count
from django.http import JsonResponse

from ..models import StockTransfer


def get_stock_transfers_view(request):
    location_id = request.GET.get("location_id", None)
    stock_transfers = (
        StockTransfer.objects.filter(
            to_location_id=location_id,
            stocktransferitem__stock__confirmationatsiteitem__isnull=True,
        )
        .annotate(count=Count("transfer_identifier"))
        .values("id", "transfer_identifier", "item_count")
        .order_by("-transfer_identifier")
    )
    return JsonResponse(list(stock_transfers), safe=False)
