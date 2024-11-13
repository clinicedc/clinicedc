from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django_audit_fields.admin import audit_fieldset_tuple
from edc_model_admin.mixins import TabularInlineMixin
from edc_utils.date import to_local

from ...admin_site import edc_pharmacy_admin
from ...forms import OrderForm, OrderItemForm
from ...models import Order, OrderItem, Receive
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
                        "qty",
                    ]
                )
            },
        ),
    )


@admin.register(Order, site=edc_pharmacy_admin)
class OrderAdmin(ModelAdminMixin, admin.ModelAdmin):
    change_list_title = "Pharmacy: Orders"
    change_form_title = "Pharmacy: Order"
    show_object_tools = True
    show_cancel = True
    list_per_page = 20

    form = OrderForm
    insert_before_fieldset = "Audit"
    ordering = ("-order_identifier",)

    fieldsets = (
        (
            None,
            {"fields": (["order_identifier", "order_datetime", "supplier", "title"])},
        ),
        ("Quantity", {"fields": (["item_count"])}),
        ("Status", {"fields": (["sent", "status"])}),
        ("Section C: Comment / Notes", {"fields": ("comment",)}),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "supplier",
        "short_title",
        "order_date",
        "status",
        "qty",
        "items",
        "receive_changelist",
        "created",
        "modified",
    )
    list_filter = ("sent", "status", "order_datetime")
    radio_fields = {"status": admin.VERTICAL}
    search_fields = ("id", "order_identifier", "title")
    readonly_fields = ("order_identifier", "sent")

    @admin.display(description="ORDER #", ordering="-order_identifier")
    def identifier(self, obj):
        return obj.order_identifier

    @admin.display(description="Title", ordering="title")
    def short_title(self, obj):
        return format_html(f'<span title="{obj.title}">{obj.title[:20]}</span>')

    @admin.display(description="QTY", ordering="-item_count")
    def qty(self, obj):
        return obj.item_count

    @admin.display(description="Order items", ordering="-order_identifier")
    def items(self, obj):
        add_order_items_button = ""
        if obj.item_count > OrderItem.objects.filter(order=obj).count():
            url = reverse("edc_pharmacy_admin:edc_pharmacy_orderitem_add")
            next_url = "edc_pharmacy_admin:edc_pharmacy_order_changelist"
            url = f"{url}?next={next_url}&order={str(obj.id)}&q={str(obj.order_identifier)}"
            context = dict(url=url, label="Add order item")
            add_order_items_button = render_to_string(
                "edc_pharmacy/stock/items_as_button.html", context=context
            )
        count = OrderItem.objects.filter(order=obj).count()
        url = reverse("edc_pharmacy_admin:edc_pharmacy_orderitem_changelist")
        url = f"{url}?q={obj.order_identifier}"
        context = dict(
            url=url, label=f"Ordered items ({count})", title="Go to items on this order"
        )
        order_items_link = render_to_string(
            "edc_pharmacy/stock/items_as_link.html", context=context
        )
        rendered = [add_order_items_button, order_items_link]
        return format_html("<BR>".join([r for r in rendered if r]))

    @admin.display(description="Order date", ordering="order_datetime")
    def order_date(self, obj):
        return to_local(obj.order_datetime).date()

    @admin.display(description="Receive #")
    def receive_changelist(self, obj):
        try:
            rcv_obj = Receive.objects.get(order=obj)
        except ObjectDoesNotExist:
            pass
        else:
            url = reverse("edc_pharmacy_admin:edc_pharmacy_receive_changelist")
            url = f"{url}?q={str(rcv_obj.receive_identifier)}"
            context = dict(url=url, label=rcv_obj.receive_identifier, title="Receive #")
            return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
        return None
