from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields.admin import audit_fieldset_tuple

from ...admin_site import edc_pharmacy_admin
from ...forms import ReceiveItemForm
from ...models import ReceiveItem
from ..model_admin_mixin import ModelAdminMixin


@admin.register(ReceiveItem, site=edc_pharmacy_admin)
class ReceiveItemAdmin(ModelAdminMixin, admin.ModelAdmin):
    show_object_tools = True
    show_cancel = True

    form = ReceiveItemForm
    include_audit_fields_in_list_display = False
    ordering = ("-receive_item_identifier",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "receive",
                    "order_item",
                    "container",
                )
            },
        ),
        (
            "Quantity",
            {
                "fields": (
                    "qty",
                    "unit_qty",
                    "added_to_stock",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "qty",
        "unit_qty",
        "added_to_stock",
        "change_order_url",
        "change_order_items_url",
        "change_receive_url",
        "modified",
        "user_created",
        "user_modified",
    )
    list_filter = (
        "receive_item_datetime",
        "created",
        "modified",
    )
    search_fields = (
        "id",
        "receive_item_identifier",
        "order_item__id",
        "receive__id",
        "receive__receive_identifier",
        "container__name",
    )

    readonly_fields = ("unit_qty",)

    @admin.display(description="Receive", ordering="-receive__receive_datetime")
    def change_receive_url(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_receive_changelist")
        url = f"{url}?q={obj.receive.receive_identifier}"
        context = dict(url=url, label="Receive", title="Back to receiving")
        return render_to_string("edc_pharmacy/stock/items.html", context=context)

    @admin.display(description="Order #")
    def change_order_url(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_order_changelist")
        url = f"{url}?q={str(obj.order_item.order.id)}"
        context = dict(
            url=url, label=obj.order_item.order.order_identifier, title="Back to order"
        )
        return render_to_string("edc_pharmacy/stock/items.html", context=context)

    @admin.display(description="Order items")
    def change_order_items_url(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_orderitem_changelist")
        url = f"{url}?q={str(obj.order_item.id)}"
        context = dict(url=url, label="Order items", title="Back to order items")
        return render_to_string("edc_pharmacy/stock/items.html", context=context)

    @admin.display(description="ID", ordering="-receive_item_identifier")
    def identifier(self, obj):
        return obj.receive_item_identifier
