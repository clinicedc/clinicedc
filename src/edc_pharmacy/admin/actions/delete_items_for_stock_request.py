from django.contrib import messages
from django.utils.translation import gettext

from ...models import StockRequestItem


def delete_items_for_stock_request_action(modeladmin, request, queryset):
    if queryset.count() > 1 or queryset.count() == 0:
        messages.add_message(
            request,
            messages.ERROR,
            gettext("Select one and only one item"),
        )
    else:
        stock_request = queryset.first()
        deleted = StockRequestItem.objects.filter(stock_request=stock_request).delete()
        messages.add_message(
            request,
            messages.SUCCESS,
            gettext(f"Delete {deleted} items for {stock_request}"),
        )
