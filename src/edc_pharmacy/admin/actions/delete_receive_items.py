from django.contrib import admin, messages
from django.db.models import QuerySet
from django.utils.translation import gettext

from ...models import ReceiveItem, Stock


@admin.display(description=f"Delete selected {ReceiveItem._meta.verbose_name_plural}")
def delete_receive_items_action(modeladmin, request, queryset: QuerySet[ReceiveItem]):
    failed_count = 0
    success_count = 0
    for obj in queryset:
        if obj.stock_set.filter(confirmation__isnull=False).exists():
            failed_count += 1
        else:
            Stock.objects.filter(receive_item=obj, confirmation__isnull=True).delete()
            obj.delete()
            success_count += 1
    if success_count > 0:
        messages.add_message(
            request,
            messages.SUCCESS,
            gettext(f"Successfully deleted {success_count} {ReceiveItem._meta.verbose_name}."),
        )
    if failed_count > 0:
        messages.add_message(
            request,
            messages.ERROR,
            gettext(
                f"Unable to deleted {failed_count} {ReceiveItem._meta.verbose_name}. "
                "Confirmed stock items exist."
            ),
        )
