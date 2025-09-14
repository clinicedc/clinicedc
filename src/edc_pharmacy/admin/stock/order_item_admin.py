from decimal import Decimal

from django.contrib import admin, messages
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django_audit_fields.admin import audit_fieldset_tuple

from edc_constants.constants import NEW, PARTIAL, RECEIVED
from edc_model_admin.history import SimpleHistoryAdmin
from edc_utils import message_in_queue

from ...admin_site import edc_pharmacy_admin
from ...forms import OrderItemForm
from ...models import Order, OrderItem, Receive, Stock
from ...utils import format_qty
from ..actions import delete_order_items_action
from ..list_filters import OrderItemStatusListFilter, ProductAssignmentListFilter
from ..model_admin_mixin import ModelAdminMixin
from ..remove_fields_for_blinded_users import remove_fields_for_blinded_users


@admin.register(OrderItem, site=edc_pharmacy_admin)
class OrderItemAdmin(ModelAdminMixin, SimpleHistoryAdmin):
    change_list_title = "Pharmacy: Ordered items"
    history_list_display = ()
    show_object_tools = False
    show_cancel = True
    list_per_page = 20

    form = OrderItemForm
    ordering = ("-order_item_identifier",)
    autocomplete_fields = ["product", "container"]
    actions = [delete_order_items_action]

    fieldsets = (
        (
            None,
            {"fields": (["order", "product", "container"])},
        ),
        (
            "Quantity",
            {"fields": (["qty", "unit_qty", "unit_qty_received"])},
        ),
        ("Status", {"fields": (["status"])}),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "product__name",
        "assignment",
        "container",
        "formatted_qty",
        "formatted_unit_qty",
        "order_status",
        "order_changelist",
        "receive_changelist",
        "stock_changelist",
        "created",
        "modified",
    )
    list_filter = (
        OrderItemStatusListFilter,
        ProductAssignmentListFilter,
    )
    radio_fields = {"status": admin.VERTICAL}
    search_fields = (
        "id",
        "order__id",
        "order__order_identifier",
    )
    readonly_fields = (
        "unit_qty",
        "unit_qty_received",
    )

    def get_list_display(self, request):
        fields = super().get_list_display(request)
        fields = remove_fields_for_blinded_users(request, fields)
        return fields

    def get_list_filter(self, request):
        fields = super().get_list_filter(request)
        fields = remove_fields_for_blinded_users(request, fields)
        return fields

    def get_search_fields(self, request):
        fields = super().get_search_fields(request)
        fields = remove_fields_for_blinded_users(request, fields)
        return fields

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ("order",)
        return self.readonly_fields

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        msg = _("All order items have been received")
        if not message_in_queue(request, msg):
            if (
                queryset.values("unit_qty").filter(unit_qty=0).count()
                == queryset.model.objects.values("unit_qty").all().count()
            ):
                messages.add_message(request, messages.INFO, msg)
        return queryset

    @admin.display(description="ORDER ITEM #", ordering="-order_item_identifier")
    def identifier(self, obj):
        return obj.order_item_identifier

    @admin.display(description="Assignment", ordering="product__assignment__name")
    def assignment(self, obj):
        return obj.product.assignment

    @admin.display(description="QTY", ordering="qty")
    def formatted_qty(self, obj):
        return format_qty(obj.qty, obj.container)

    @admin.display(description="Units", ordering="qty")
    def formatted_unit_qty(self, obj):
        return format_qty(obj.unit_qty, obj.container)

    @admin.display(description="Product", ordering="product__name")
    def product_name(self, obj):
        return obj.product.formulation.get_description_with_assignment(obj.product.assignment)

    @admin.display(description="Container", ordering="container__name")
    def container_name(self, obj):
        return obj.container.name

    @admin.display(description="Order #", ordering="-order__order_datetime")
    def order_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_order_changelist")
        url = f"{url}?q={obj.order.order_identifier}"
        context = dict(url=url, label=obj.order.order_identifier, title="Back to order")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Stock")
    def stock_changelist(self, obj):
        if Stock.objects.filter(receive_item__receive__order=obj.order).exists():
            url = reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")
            url = f"{url}?q={obj.order.id}"
            context = dict(url=url, label="Stock", title="Go to stock")
            return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
        return None

    @admin.display(description="RECEIVE #")
    def receive_changelist(self, obj):
        if receive := self.get_receive_obj(obj):
            return self.render_receive_changelist_link(receive)
        return None

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "order":
            if request.GET.get("order"):
                kwargs["queryset"] = Order.objects.filter(
                    id__exact=request.GET.get("order", 0)
                )
            else:
                kwargs["queryset"] = Order.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_status_label(self, obj: OrderItem) -> tuple[str, str]:
        if obj.unit_qty == 0:
            return RECEIVED, _("Received")
        if obj.unit_qty == obj.unit_qty_ordered:
            return NEW, _("New")
        return PARTIAL, _("Partial")

    @admin.display(description="Status")
    def order_status(self, obj: OrderItem):
        receive_this_item_button = ""
        receive = self.get_receive_obj(obj)
        if not receive:
            return self.render_start_receiving_button(obj)
        if (obj.unit_qty_received or Decimal(0)) < obj.unit_qty_ordered:
            receive_this_item_button = self.render_receive_this_item_button(obj, receive)
        received_items_link = self.render_received_items_link(obj)
        renders = [
            receive_this_item_button,
            received_items_link,
        ]
        renders = [r for r in renders if r]
        return format_html(
            "{}",
            mark_safe("<BR>".join(renders)),  # nosec B703, B308
        )

    @staticmethod
    def get_receive_obj(obj: OrderItem) -> Receive | None:
        try:
            obj = Receive.objects.get(order=obj.order)
        except Receive.DoesNotExist:
            obj = None
        return obj

    @staticmethod
    def render_start_receiving_button(obj: OrderItem) -> str:
        url = reverse("edc_pharmacy_admin:edc_pharmacy_receive_add")
        next_url = "edc_pharmacy_admin:edc_pharmacy_orderitem_changelist"
        url = f"{url}?next={next_url}&q={obj.order.id!s}&order={obj.order.id!s}"
        context = dict(
            url=url,
            label=_("Start Receiving"),
            title=_("Receive against this order item"),
        )
        return render_to_string(
            "edc_pharmacy/stock/items_as_button.html",
            context=context,
        )

    @staticmethod
    def render_receive_changelist_link(receive: Receive) -> str:
        url = reverse("edc_pharmacy_admin:edc_pharmacy_receive_changelist")
        url = f"{url}?q={receive.receive_identifier!s}"
        context = dict(url=url, label=receive.receive_identifier, title=_("Receive"))
        return render_to_string(
            "edc_pharmacy/stock/items_as_link.html",
            context=context,
        )

    @staticmethod
    def render_receive_this_item_button(obj: OrderItem, receive: Receive) -> str:
        url = reverse("edc_pharmacy_admin:edc_pharmacy_receiveitem_add")
        next_url = "edc_pharmacy_admin:edc_pharmacy_orderitem_changelist"
        url = (
            f"{url}?next={next_url}&order_item={obj.id!s}&q={obj.order.id!s}"
            f"&receive={receive.id!s}&container={obj.container.id!s}"
        )
        context = dict(
            url=url,
            label=_("Receive this item"),
            title=_("Receive against this order item"),
        )
        return render_to_string(
            "edc_pharmacy/stock/items_as_button.html",
            context=context,
        )

    def render_received_items_link(self, obj: OrderItem) -> str | None:
        status, status_label = self.get_status_label(obj)
        if status != NEW:
            url = reverse("edc_pharmacy_admin:edc_pharmacy_receiveitem_changelist")
            url = f"{url}?q={obj.pk!s}"
            context = dict(url=url, label=status_label, title=_("Go to received items"))
            return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
        return None
