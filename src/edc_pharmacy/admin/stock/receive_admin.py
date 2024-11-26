from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields.admin import audit_fieldset_tuple
from edc_model_admin.history import SimpleHistoryAdmin
from edc_utils.date import to_local

from ...admin_site import edc_pharmacy_admin
from ...forms import ReceiveForm
from ...models import Receive
from ..actions import confirm_received_stock_action, print_labels_from_receive
from ..model_admin_mixin import ModelAdminMixin


@admin.register(Receive, site=edc_pharmacy_admin)
class ReceiveAdmin(ModelAdminMixin, SimpleHistoryAdmin):
    change_list_title = "Pharmacy: Receiving"
    change_form_title = "Pharmacy: Receive"
    history_list_display = ()

    show_object_tools = False
    show_cancel = True
    list_per_page = 20

    form = ReceiveForm
    ordering = ("-receive_identifier",)
    actions = [print_labels_from_receive, confirm_received_stock_action]
    autocomplete_fields = ["supplier"]

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
                    "order",
                    "location",
                )
            },
        ),
        (
            "Section B",
            {
                "fields": (
                    "supplier",
                    "invoice_number",
                    "invoice_date",
                )
            },
        ),
        ("Section C: Comment / Notes", {"fields": ("comment",)}),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "receive_date",
        "location",
        "order_changelist",
        "items",
        "stock_changelist",
        "supplier",
        "invoice_number",
        "invoice_date",
        "created",
        "modified",
    )
    list_filter = (
        "receive_datetime",
        "location",
        "invoice_date",
        "created",
        "modified",
    )
    search_fields = (
        "id",
        "receive_identifier",
        "order__id",
        "location__name",
        "invoice_number",
        "supplier__name",
    )

    @admin.display(description="RECEIVE #", ordering="receive_identifier")
    def identifier(self, obj):
        return obj.receive_identifier

    @admin.display(description="Receive date", ordering="receive_datetime")
    def receive_date(self, obj):
        return to_local(obj.receive_datetime).date()

    @admin.display(description="Received items", ordering="receive_identifier")
    def items(self, obj):
        count = obj.receiveitem_set.all().count()
        url = reverse("edc_pharmacy_admin:edc_pharmacy_receiveitem_changelist")
        url = f"{url}?q={obj.id}"
        context = dict(url=url, label=f"Received ({count})", title="Go to received items")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Order #")
    def order_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_order_changelist")
        url = f"{url}?q={str(obj.order.order_identifier)}"
        context = dict(url=url, label=obj.order.order_identifier, title="Back to order")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Stock")
    def stock_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")
        url = f"{url}?q={obj.id}"
        context = dict(url=url, label="Stock", title="Go to stock")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "order" and request.GET.get("order"):
            kwargs["queryset"] = db_field.related_model.objects.filter(
                pk=request.GET.get("order", 0)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
