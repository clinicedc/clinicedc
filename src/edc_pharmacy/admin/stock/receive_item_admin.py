from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields.admin import audit_fieldset_tuple
from edc_model_admin.history import SimpleHistoryAdmin
from edc_utils.date import to_local

from ...admin_site import edc_pharmacy_admin
from ...forms import ReceiveItemForm
from ...models import OrderItem, Receive, ReceiveItem
from ...utils import format_qty
from ..actions import delete_receive_items_action, print_labels_from_receive_item
from ..model_admin_mixin import ModelAdminMixin


@admin.register(ReceiveItem, site=edc_pharmacy_admin)
class ReceiveItemAdmin(ModelAdminMixin, SimpleHistoryAdmin):
    change_list_title = "Pharmacy: Received items"
    change_form_title = "Pharmacy: Receive item"
    history_list_display = ()
    show_object_tools = False
    show_cancel = True
    list_per_page = 20

    form = ReceiveItemForm
    include_audit_fields_in_list_display = False
    ordering = ("-receive_item_identifier",)

    actions = [delete_receive_items_action, print_labels_from_receive_item]

    fieldsets = (
        (
            None,
            {"fields": ("receive", "order_item", "container", "lot")},
        ),
        (
            "Quantity",
            {"fields": ("qty", "unit_qty")},
        ),
        (
            "Reference",
            {"fields": ("reference", "comment")},
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "item_date",
        "order_item_product",
        "formatted_lot",
        "container",
        "formatted_qty",
        "formatted_unit_qty",
        "order_changelist",
        "order_items_changelist",
        "receive_changelist",
        "stock_changelist",
        "reference",
        "modified",
        "user_created",
        "user_modified",
    )
    list_filter = (
        "receive_item_datetime",
        "lot",
        "reference",
        "created",
        "modified",
    )
    search_fields = (
        "id",
        "order_item__id",
        "order_item__order__order_identifier",
        "receive__id",
        "container__name",
        "lot__lot_no",
        "reference",
        "comment",
    )

    readonly_fields = ("unit_qty",)

    @admin.display(description="Item date", ordering="receive_item_datetime")
    def item_date(self, obj):
        return to_local(obj.receive_item_datetime).date()

    @admin.display(description="BATCH #", ordering="lot__lot_no")
    def formatted_lot(self, obj):
        return obj.lot.lot_no

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
        url = f"{url}?q={obj.receive.receive_identifier}"
        context = dict(
            url=url, label=obj.receive.receive_identifier, title="Back to receiving"
        )
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Stock")
    def stock_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")
        url = f"{url}?q={obj.id}"
        label = "Stock"
        context = dict(url=url, label=label, title="Go to stock")
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

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ("receive",)
        return self.readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "receive":
            if request.GET.get("receive"):
                kwargs["queryset"] = Receive.objects.filter(
                    id__exact=request.GET.get("receive", 0)
                )
            else:
                kwargs["queryset"] = Receive.objects.none()
        if db_field.name == "order_item":
            if request.GET.get("order_item"):
                kwargs["queryset"] = OrderItem.objects.filter(
                    id__exact=request.GET.get("order_item", 0)
                )
            else:
                kwargs["queryset"] = OrderItem.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
