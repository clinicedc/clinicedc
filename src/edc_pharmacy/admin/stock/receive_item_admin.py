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
    change_list_title = "Pharmacy: Received items"
    show_object_tools = False
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
        "order_changelist",
        "change_order_items_url",
        "receive_changelist",
        "stock_changelist",
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
        # "receive_item_identifier",
        "order_item__id",
        "order_item__order__order_identifier",
        "receive__id",
        "container__name",
    )

    readonly_fields = ("unit_qty", "added_to_stock")

    @admin.display(description="Receiving", ordering="-receive__receive_datetime")
    def receive_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_receive_changelist")
        url = f"{url}?q={obj.receive.id}"
        context = dict(url=url, label="Receiving", title="Back to receiving")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Stock")
    def stock_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")
        url = f"{url}?q={obj.order_item.order.order_identifier}"
        context = dict(url=url, label="Stock", title="Go to stock")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Order #")
    def order_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_order_changelist")
        url = f"{url}?q={str(obj.order_item.order.order_identifier)}"
        context = dict(
            url=url, label=obj.order_item.order.order_identifier, title="Back to order"
        )
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Order items")
    def change_order_items_url(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_orderitem_changelist")
        url = f"{url}?q={str(obj.order_item.id)}"
        context = dict(url=url, label="Order items", title="Back to order items")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="ID", ordering="-receive_item_identifier")
    def identifier(self, obj):
        return obj.receive_item_identifier
