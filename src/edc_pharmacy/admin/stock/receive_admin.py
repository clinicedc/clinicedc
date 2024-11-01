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
    show_object_tools = True

    form = ReceiveForm
    inlines = [ReceiveItemInlineAdmin]
    insert_before_fieldset = "Audit"
    ordering = ("-receive_identifier",)

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
        "items",
        "location",
        "order",
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
        "receive_identifier",
        "order__order_identifier",
        "location__name",
    )

    @admin.display(description="ID", ordering="receive_identifier")
    def identifier(self, obj):
        return obj.receive_identifier

    @admin.display(description="Receive items", ordering="receive_identifier")
    def items(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_receiveitem_changelist")
        url = f"{url}?q={obj.receive_identifier}"
        context = dict(url=url, label="Receive items", title="Go to received items")
        return render_to_string("edc_pharmacy/stock/items.html", context=context)
