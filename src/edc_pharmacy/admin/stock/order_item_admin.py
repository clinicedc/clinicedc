from decimal import Decimal

from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields.admin import audit_fieldset_tuple
from edc_constants.constants import COMPLETE

from ...admin_site import edc_pharmacy_admin
from ...forms import OrderItemForm
from ...models import OrderItem, Receive
from ..model_admin_mixin import ModelAdminMixin


@admin.register(OrderItem, site=edc_pharmacy_admin)
class OrderItemAdmin(ModelAdminMixin, admin.ModelAdmin):
    change_list_title = "Pharmacy: Ordered items"
    show_object_tools = False
    show_cancel = True
    form = OrderItemForm
    ordering = ("-order_item_identifier",)
    autocomplete_fields = ["order", "product", "container"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    [
                        "order",
                        "product",
                        "container",
                    ]
                )
            },
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
        "product_name",
        "container_name",
        "qty",
        "received_items_changelist",
        "status",
        "order_changelist",
        "receive_url",
        "stock_changelist",
        "created",
        "modified",
    )
    list_filter = ("status",)
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

    @admin.display(description="Product", ordering="product__name")
    def product_name(self, obj):
        return obj.product.formulation.description_with_assignment(obj.product.assignment)

    @admin.display(description="Container", ordering="container__name")
    def container_name(self, obj):
        return obj.container.name

    @admin.display(description="Order #", ordering="-order__order_datetime")
    def order_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_order_changelist")
        url = f"{url}?q={obj.order.order_identifier}"
        context = dict(url=url, label=obj.order.order_identifier, title="Back to order")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Receive item")
    def changelist_receive_item_url(self, obj):
        if obj.container.qty == obj.unit_qty_received:
            url = reverse("edc_pharmacy_admin:edc_pharmacy_receiveitem_changelist")
            url = f"{url}?q={obj.order.order_identifier}"
            context = dict(url=url, label="Receive more", title="Receive more")
            return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
        return None

    @admin.display(description="not received", ordering="unit_qty_received")
    def received_items_changelist(self, obj):
        if (obj.unit_qty_received or Decimal(0)) > Decimal(0):
            url = reverse("edc_pharmacy_admin:edc_pharmacy_receiveitem_changelist")
            url = f"{url}?q={str(obj.id)}"
            context = dict(
                url=url,
                label=obj.unit_qty - obj.unit_qty_received,
                title="Go to received item(s) for this ordered item",
            )
            return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
        return None

    @admin.display(description="Stock")
    def stock_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")
        url = f"{url}?q={obj.order.order_identifier}"
        context = dict(url=url, label="Stock", title="Go to stock")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Receiving")
    def receive_url(self, obj):
        try:
            rcv_obj = Receive.objects.get(order=obj.order)
        except Receive.DoesNotExist:
            rcv_obj = None
        if not rcv_obj:
            url = reverse("edc_pharmacy_admin:edc_pharmacy_receive_add")
            next_url = "edc_pharmacy_admin:edc_pharmacy_orderitem_changelist"
            url = f"{url}?next={next_url}&q={str(obj.order.id)}&order={str(obj.order.id)}"
            context = dict(
                url=url, label="Start Receiving", title="Receive against this order item"
            )
        elif obj.status != COMPLETE:
            url = reverse("edc_pharmacy_admin:edc_pharmacy_receiveitem_add")
            next_url = "edc_pharmacy_admin:edc_pharmacy_orderitem_changelist"
            url = (
                f"{url}?next={next_url}&q={str(obj.order.id)}&order_item={str(obj.id)}"
                f"&receive={str(rcv_obj.id)}&container={str(obj.container.id)}"
            )
            context = dict(
                url=url, label="Receive item", title="Receive against this order item"
            )
        else:
            url = reverse("edc_pharmacy_admin:edc_pharmacy_receiveitem_changelist")
            url = f"{url}?q={str(obj.order.order_identifier)}"
            context = dict(url=url, label="Received items", title="Received items")
            return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
        return render_to_string("edc_pharmacy/stock/items_as_button.html", context=context)

    @admin.display(description="ID", ordering="-order_item_identifier")
    def identifier(self, obj):
        return obj.order_item_identifier
