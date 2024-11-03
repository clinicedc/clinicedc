from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields.admin import audit_fieldset_tuple
from edc_model_admin.mixins import TabularInlineMixin

from ...admin_site import edc_pharmacy_admin
from ...forms import ReceiveForm, ReceiveItemForm
from ...models import Receive, ReceiveItem
from ..model_admin_mixin import ModelAdminMixin


class ReceiveItemInlineAdmin(TabularInlineMixin, admin.TabularInline):
    model = ReceiveItem
    form = ReceiveItemForm
    extra = 1

    fieldsets = (
        (
            None,
            {
                "fields": (
                    [
                        "receive_item_datetime",
                        "order_item",
                        "container",
                        "unit_qty",
                    ]
                )
            },
        ),
    )


@admin.register(Receive, site=edc_pharmacy_admin)
class ReceiveAdmin(ModelAdminMixin, admin.ModelAdmin):
    change_list_title = "Pharmacy: Receiving"
    show_object_tools = False
    show_cancel = True

    form = ReceiveForm
    # inlines = [ReceiveItemInlineAdmin]
    # insert_before_fieldset = "Audit"
    ordering = ("-receive_identifier",)
    autocomplete_fields = ["order"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "receive_identifier",
                    "receive_datetime",
                    "location",
                    "order",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "receive_datetime",
        "location",
        "item_count",
        "order_changelist",
        "items",
        "created",
        "modified",
    )
    list_filter = (
        "receive_datetime",
        "location",
        "created",
        "modified",
    )
    search_fields = (
        "id",
        "order__order_identifier",
        "location__name",
    )

    @admin.display(description="ID", ordering="receive_identifier")
    def identifier(self, obj):
        return obj.receive_identifier

    @admin.display(description="Received items", ordering="receive_identifier")
    def items(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_receiveitem_changelist")
        url = f"{url}?q={obj.id}"
        context = dict(url=url, label="Received items", title="Go to received items")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Order #")
    def order_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_order_changelist")
        url = f"{url}?q={str(obj.order.order_identifier)}"
        context = dict(url=url, label=obj.order.order_identifier, title="Back to order")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
