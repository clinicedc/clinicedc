from django.contrib import messages
from django.utils.translation import gettext as _

from ...models import StockRequestItem


def delete_items_for_stock_request_action(modeladmin, request, queryset):
    if queryset.count() > 1 or queryset.count() == 0:
        messages.add_message(
            request,
            messages.ERROR,
            _("Select one and only one item"),
        )
    else:
        stock_request = queryset.first()
        deleted = StockRequestItem.objects.filter(stock_request=stock_request).delete()
        messages.add_message(
            request,
            messages.SUCCESS,
            _("Delete %(deleted)s items for %(stock_request)s")
            % dict(deleted=deleted, stock_request=stock_request),
        )
