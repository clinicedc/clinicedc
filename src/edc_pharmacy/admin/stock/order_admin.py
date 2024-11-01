from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields.admin import audit_fieldset_tuple
from edc_model_admin.mixins import TabularInlineMixin

from ...admin_site import edc_pharmacy_admin
from ...forms import OrderForm, OrderItemForm
from ...models import Order, OrderItem
from ..model_admin_mixin import ModelAdminMixin


class OrderItemInlineAdmin(TabularInlineMixin, admin.TabularInline):
    model = OrderItem
    form = OrderItemForm
    extra = 1

    fieldsets = (
        (
            None,
            {
                "fields": (
                    [
                        "product",
                        "container",
                        "unit_qty",
                    ]
                )
            },
        ),
    )


@admin.register(Order, site=edc_pharmacy_admin)
class OrderAdmin(ModelAdminMixin, admin.ModelAdmin):
    show_object_tools = True
    show_cancel = True

    form = OrderForm
    # inlines = [OrderItemInlineAdmin]
    insert_before_fieldset = "Audit"
    ordering = ("-order_identifier",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    [
                        "order_identifier",
                        "order_datetime",
                    ]
                )
            },
        ),
        (
            "Quantity",
            {"fields": (["item_count", "unit_qty", "container_qty"])},
        ),
        (
            "Status",
            {"fields": (["sent", "status"])},
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "order_datetime",
        "sent",
        "item_count",
        "add_order_item",
        "items",
        "status",
        "unit_qty",
        "container_qty",
        "created",
        "modified",
    )
    list_filter = ("sent", "status", "order_datetime")
    radio_fields = {"status": admin.VERTICAL}
    search_fields = ("id", "order_identifier")
    readonly_fields = ("order_identifier", "unit_qty", "container_qty", "sent")

    @admin.display(description="Order #", ordering="-order_identifier")
    def identifier(self, obj):
        return obj.order_identifier

    @admin.display(description="Order items", ordering="-order_identifier")
    def items(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_orderitem_changelist")
        url = f"{url}?q={obj.order_identifier}"
        context = dict(url=url, label="Order items", title="Go to items on this order")
        return render_to_string("edc_pharmacy/stock/items.html", context=context)

    @admin.display(description="Add order item")
    def add_order_item(self, obj):
        if obj.item_count > OrderItem.objects.filter(order=obj).count():
            url = reverse("edc_pharmacy_admin:edc_pharmacy_orderitem_add")
            next_url = "edc_pharmacy_admin:edc_pharmacy_order_changelist"
            url = f"{url}?next={next_url}&order={str(obj.id)}&q={str(obj.order_identifier)}"
            context = dict(url=url, label="Add order item")
            return render_to_string("edc_pharmacy/stock/items.html", context=context)
        return None
