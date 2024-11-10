from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django_audit_fields.admin import audit_fieldset_tuple
from edc_pylabels.actions import print_label_sheet

from ...admin_site import edc_pharmacy_admin
from ...forms import StockForm
from ...models import Stock
from ...utils import format_qty
from ..actions import repack_stock_action
from ..list_filters import HasOrderNumFilter, HasReceiveNumFilter, HasRepackNumFilter
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

    actions = [repack_stock_action, print_label_sheet]

    form = StockForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "stock_identifier",
                    "code",
                    "confirmed",
                    "location",
                    "label_configuration",
                )
            },
        ),
        (
            "Product",
            {"fields": ("product", "container")},
        ),
        (
            "Lot",
            {"fields": ("lot",)},
        ),
        (
            "Quantity",
            {"fields": ("qty_in", "qty_out", "unit_qty_in", "unit_qty_out")},
        ),
        (
            "Receive",
            {"fields": ("receive_item",)},
        ),
        (
            "Repack",
            {
                "fields": (
                    "repack_request",
                    "from_stock",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "code",
        "from_stock_with_product",
        "confirmed_str",
        "formulation",
        "assignment",
        "qty",
        "container_str",
        "unit_qty",
        "order_changelist",
        "receive_item_changelist",
        "repack_request_changelist",
        "lot",
        "label_configuration",
        "created",
        "modified",
    )
    list_filter = (
        "confirmed",
        "product__formulation__description",
        "product__assignment__name",
        "location__display_name",
        "container",
        HasOrderNumFilter,
        HasReceiveNumFilter,
        HasRepackNumFilter,
        "created",
        "modified",
    )
    search_fields = (
        "stock_identifier",
        "code",
        "product__name",
        "receive_item__receive__id",
        "receive_item__order_item__order__id",
        "lot__lot_no",
        "repack_request__id",
    )
    ordering = ("stock_identifier",)
    readonly_fields = (
        "code",
        "confirmed",
        "container",
        "from_stock",
        "location",
        "product",
        "qty_in",
        "qty_out",
        "receive_item",
        "stock_identifier",
    )

    @admin.display(description="QTY", ordering="qty")
    def qty(self, obj):
        return format_qty(obj.qty_in - obj.qty_out, obj.container)

    @admin.display(description="Units", ordering="qty")
    def unit_qty(self, obj):
        return format_qty(obj.unit_qty_in - obj.unit_qty_out, obj.container)

    @admin.display(description="STOCK #", ordering="-stock_identifier")
    def identifier(self, obj):
        return obj.stock_identifier.split("-")[0]

    @admin.display(description="\u2713", ordering="-stock_identifier", boolean=True)
    def confirmed_str(self, obj):
        return obj.confirmed

    @admin.display(description="Container", ordering="container_name")
    def container_str(self, obj):
        return format_html("<BR>".join(str(obj.container).split(" ")))

    @admin.display(description="formulation", ordering="product__formulation__name")
    def formulation(self, obj):
        return obj.product.formulation

    @admin.display(description="assignment", ordering="product__assignment__name")
    def assignment(self, obj):
        if obj.product.assignment:
            return obj.product.assignment
        return None

    @admin.display(description="From stock #")
    def from_stock_with_product(self, obj):
        if obj.from_stock:
            url = reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")
            url = f"{url}?q={obj.from_stock.stock_identifier}"
            context = dict(
                url=url,
                label=obj.from_stock.stock_identifier,
                title="Go to stock",
            )
            return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
        return None

    @admin.display(description="Order #", ordering="-order__order_datetime")
    def order_changelist(self, obj):
        if obj.receive_item and obj.receive_item.order_item.order:
            url = reverse("edc_pharmacy_admin:edc_pharmacy_order_changelist")
            url = f"{url}?q={obj.receive_item.order_item.order.order_identifier}"
            context = dict(
                url=url,
                label=obj.receive_item.order_item.order.order_identifier,
                title="Go to order",
            )
            return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
        return None

    @admin.display(description="Receive #", ordering="-receive_item__receive_item_datetime")
    def receive_item_changelist(self, obj):
        if obj.receive_item:
            url = reverse("edc_pharmacy_admin:edc_pharmacy_receiveitem_changelist")
            url = f"{url}?q={obj.receive_item.id}"
            context = dict(
                url=url,
                label=obj.receive_item.receive_item_identifier,
                title="Go to received item",
            )
            return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
        return None

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
