from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields.admin import audit_fieldset_tuple

from ...admin_site import edc_pharmacy_admin
from ...forms import StockForm
from ...models import Stock
from ..model_admin_mixin import ModelAdminMixin


@admin.register(Stock, site=edc_pharmacy_admin)
class StockAdmin(ModelAdminMixin, admin.ModelAdmin):
    change_list_title = "Pharmacy: Stock"
    show_object_tools = False
    show_cancel = True

    show_form_tools = True
    show_history_label = True
    autocomplete_fields = ["container", "receive_item"]

    form = StockForm

    fieldsets = (
        (
            None,
            {"fields": ("stock_identifier",)},
        ),
        (
            "Product",
            {"fields": ("product", "container")},
        ),
        (
            "Receive",
            {"fields": ("receive_item",)},
        ),
        (
            "Quantity",
            {"fields": ("qty_in", "qty_out")},
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "product",
        "container",
        "qty_in",
        "qty_out",
        "unit_qty",
        "order_changelist",
        "receive_item_changelist",
        "created",
        "modified",
    )
    list_filter = (
        "product__name",
        "product__formulation",
        "container__name",
        "created",
        "modified",
    )
    search_fields = (
        "stock_identifier",
        "product__name",
        "receive_item__receive__id",
        "receive_item__order_item__order__id",
        "receive_item__order_item__order__order_identifier",
    )
    ordering = ("stock_identifier",)
    readonly_fields = (
        "stock_identifier",
        "product",
        "receive_item",
        "container",
        "qty_in",
        "qty_out",
    )

    @admin.display(description="Identifier", ordering="-stock_datetime")
    def identifier(self, obj):
        return obj.stock_identifier.split("-")[0]

    @admin.display(description="unit qty")
    def unit_qty(self, obj):
        return obj.unit_qty_in - obj.unit_qty_out

    @admin.display(description="Order #", ordering="-order__order_datetime")
    def order_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_order_changelist")
        url = f"{url}?q={obj.receive_item.order_item.order.order_identifier}"
        context = dict(
            url=url,
            label=obj.receive_item.order_item.order.order_identifier,
            title="Go to order",
        )
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Receive #", ordering="-receive_item__receive_item_datetime")
    def receive_item_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_receiveitem_changelist")
        url = f"{url}?q={obj.receive_item.id}"
        context = dict(
            url=url,
            label=obj.receive_item.receive_item_identifier,
            title="Go to received item",
        )
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
