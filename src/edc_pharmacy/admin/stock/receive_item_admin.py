from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields.admin import audit_fieldset_tuple
from edc_utils.date import to_local

from ...admin_site import edc_pharmacy_admin
from ...forms import ReceiveItemForm
from ...models import ReceiveItem
from ...utils import format_qty
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
            {"fields": ("receive", "order_item", "container", "lot")},
        ),
        (
            "Quantity",
            {"fields": ("qty", "unit_qty")},
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "item_date",
        "order_item_product",
        "lot",
        "container",
        "formatted_qty",
        "formatted_unit_qty",
        "order_changelist",
        "order_items_changelist",
        "receive_changelist",
        "stock_changelist",
        "modified",
        "user_created",
        "user_modified",
    )
    list_filter = (
        "receive_item_datetime",
        "lot",
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
        "lot__lot_no",
    )

    readonly_fields = ("unit_qty",)

    @admin.display(description="Item date", ordering="receive_item_datetime")
    def item_date(self, obj):
        return to_local(obj.receive_item_datetime).date()

    @admin.display(description="QTY", ordering="qty")
    def formatted_qty(self, obj):
        return format_qty(obj.qty, obj.container)

    @admin.display(description="Units", ordering="qty")
    def formatted_unit_qty(self, obj):
        return format_qty(obj.unit_qty, obj.container)

    @admin.display(description="Product", ordering="-order_item__product__name")
    def order_item_product(self, obj):
        return obj.order_item.product

    @admin.display(description="Receive #", ordering="-receive__receive_datetime")
    def receive_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_receive_changelist")
        url = f"{url}?q={obj.receive.id}"
        context = dict(
            url=url, label=obj.receive.receive_identifier, title="Back to receiving"
        )
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

    @admin.display(description="Order item #")
    def order_items_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_orderitem_changelist")
        url = f"{url}?q={str(obj.order_item.id)}"
        context = dict(
            url=url, label=obj.order_item.order_item_identifier, title="Back to order item"
        )
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="RECEIVE ITEM #", ordering="-receive_item_identifier")
    def identifier(self, obj):
        return obj.receive_item_identifier
