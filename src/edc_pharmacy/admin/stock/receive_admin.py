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
    ordering = ("-receive_identifier",)

    fieldsets = (
        (
            None,
            {"fields": ("receive_identifier",)},
        ),
        (
            "Section A",
            {
                "fields": (
                    "receive_datetime",
                    "location",
                    "order",
                )
            },
        ),
        (
            "Section B: Confirm stock after labelling",
            {
                "description": (
                    "Complete this section AFTER printing labels and "
                    "affixing to stock items. Scan labels back into the EDC here"
                ),
                "fields": (
                    "stock_identifiers",
                    "confirmed_stock_identifiers",
                    "unconfirmed_stock_identifiers",
                ),
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
    readonly_fields = (
        "confirmed_stock_identifiers",
        "unconfirmed_stock_identifiers",
    )
    search_fields = (
        "id",
        "order__order_identifier",
        "location__name",
        "stock_identifiers",
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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "order" and request.GET.get("order"):
            kwargs["queryset"] = db_field.related_model.objects.filter(
                pk=request.GET.get("order", 0)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
