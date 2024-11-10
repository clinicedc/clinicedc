from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django_audit_fields import audit_fieldset_tuple
from edc_model_admin.list_filters import FutureDateListFilter
from edc_utils.date import to_local

from ...admin_site import edc_pharmacy_admin
from ...forms import StockRequestItemForm
from ...models import StockRequestItem
from ..model_admin_mixin import ModelAdminMixin


class ApptDatetimeListFilter(FutureDateListFilter):
    title = "Appt date"

    parameter_name = "appt_datetime"
    field_name = "appt_datetime"


@admin.register(StockRequestItem, site=edc_pharmacy_admin)
class StockRequestItemAdmin(ModelAdminMixin, admin.ModelAdmin):
    change_list_title = "Pharmacy: Requested stock items"
    show_object_tools = False
    show_cancel = True
    form = StockRequestItemForm
    autocomplete_fields = ["rx"]

    fieldsets = (
        (
            "Section A",
            {
                "fields": (
                    "stock_request",
                    "request_item_datetime",
                    "rx",
                )
            },
        ),
        (
            "Section C",
            {
                "fields": ("received", "received_datetime"),
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "request_item_id",
        "item_date",
        "request_changelist",
        "location",
        "subject",
        "formulation",
        "visit_code_and_seq",
        "appt_date",
        "in_stock",
        "received",
        "received_datetime",
    )

    list_filter = (
        "visit_code",
        ApptDatetimeListFilter,
        "in_stock",
        "received",
        "received_datetime",
    )
    readonly_fields = (
        "received_datetime",
        "received",
        "rx",
    )

    search_fields = (
        "id",
        "rx__subject_identifier",
        "stock_request__request_identifier",
    )

    @admin.display(description="Visit", ordering="visit_code")
    def visit_code_and_seq(self, obj):
        return f"{obj.visit_code}.{obj.visit_code_sequence}"

    @admin.display(description="Appt", ordering="request_item_datetime")
    def appt_date(self, obj):
        if obj.appt_datetime:
            return f"{to_local(obj.appt_datetime).date()}"
        return None

    @admin.display(description="Stock item")
    def formulation(self, obj):
        return format_html(f"{obj.stock_request.formulation}<BR>{obj.stock_request.container}")

    @admin.display(description="Date", ordering="request_item_datetime")
    def item_date(self, obj):
        if obj.request_item_datetime:
            return to_local(obj.request_item_datetime).date()
        return None

    @admin.display(description="Subject", ordering="subject_identifier")
    def subject(self, obj):
        return obj.subject_identifier

    @admin.display(description="Location", ordering="stock_request__location__name")
    def location(self, obj):
        return obj.stock_request.location

    @admin.display(description="ITEM#", ordering="request_item_identifier")
    def request_item_id(self, obj):
        return obj.request_item_identifier

    @admin.display(description="Request#")
    def request_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stockrequest_changelist")
        url = f"{url}?q={obj.stock_request.request_identifier}"
        context = dict(
            url=url,
            label=f"{obj.stock_request.request_identifier}",
            title="Back to stock request",
        )
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
