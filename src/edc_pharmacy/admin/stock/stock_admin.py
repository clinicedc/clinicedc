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
    list_per_page = 20

    show_form_tools = True
    show_history_label = True
    autocomplete_fields = ["container"]

    form = StockForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "stock_identifier",
                    "confirmed",
                )
            },
        ),
        (
            "Product",
            {"fields": ("product", "container", "location")},
        ),
        (
            "Receive",
            {"fields": ("receive_item",)},
        ),
        (
            "Repackage",
            {"fields": ("repack_request", "from_stock")},
        ),
        (
            "Quantity",
            {"fields": ("qty_in", "qty_out")},
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "confirmed",
        "from_stock__product",
        "container",
        "qty_in",
        "qty_out",
        "unit_qty",
        "order_changelist",
        "receive_item_changelist",
        "repack_request_changelist",
        "created",
        "modified",
    )
    list_filter = (
        "confirmed",
        "location__display_name",
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
        "repack_request__id",
    )
    ordering = ("stock_identifier",)
    readonly_fields = (
        "confirmed",
        "stock_identifier",
        "product",
        "location",
        "receive_item",
        "repack_request",
        "from_stock",
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
        url = f"{url}?q={obj.get_receive_item().order_item.order.order_identifier}"
        context = dict(
            url=url,
            label=obj.get_receive_item().order_item.order.order_identifier,
            title="Go to order",
        )
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Receive #", ordering="-receive_item__receive_item_datetime")
    def receive_item_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_receiveitem_changelist")
        url = f"{url}?q={obj.get_receive_item().id}"
        context = dict(
            url=url,
            label=obj.get_receive_item().receive_item_identifier,
            title="Go to received item",
        )
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Repack #", ordering="-repack_request__repack_datetime")
    def repack_request_changelist(self, obj):
        if obj.repack_request:
            url = reverse("edc_pharmacy_admin:edc_pharmacy_repackrequest_changelist")
            url = f"{url}?q={obj.repack_request.id}"
            context = dict(
                url=url,
                label=obj.repack_request.repack_identifier,
                title="Go to repackage request",
            )
            return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
        return None
