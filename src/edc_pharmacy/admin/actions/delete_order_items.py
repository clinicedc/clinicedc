from django.contrib import admin, messages
from django.db.models import QuerySet
from django.utils.translation import gettext

from ...models import OrderItem, Stock


@admin.display(description=f"Delete selected {OrderItem._meta.verbose_name_plural}")
def delete_order_items_action(modeladmin, request, queryset: QuerySet[OrderItem]):
    failed_count = 0
    success_count = 0
    for obj in queryset:
        if obj.receiveitem_set.filter(stock__confirmation__isnull=False).exists():
            failed_count += 1
        else:
            Stock.objects.filter(
                receive_item__order_item=obj, stock__confirmation__isnull=True
            ).delete()
            obj.receiveitem_set.all().delete()
            obj.delete()
            success_count += 1
    if success_count > 0:
        messages.add_message(
            request,
            messages.SUCCESS,
            gettext(f"Successfully deleted {success_count} {OrderItem._meta.verbose_name}."),
        )
    if failed_count > 0:
        messages.add_message(
            request,
            messages.ERROR,
            gettext(
                f"Unable to deleted {failed_count} {OrderItem._meta.verbose_name}. "
                "Confirmed stock items exist."
            ),
        )
