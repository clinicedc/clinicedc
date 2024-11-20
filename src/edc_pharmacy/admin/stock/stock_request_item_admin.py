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
from ..list_filters import (
    AssignmentListFilter,
    StockItemAllocationListFilter,
    StockRequestItemPendingListFilter,
)
from ..model_admin_mixin import ModelAdminMixin
from ..remove_fields_for_blinded_users import remove_fields_for_blinded_users


class ApptDatetimeListFilter(FutureDateListFilter):
    title = "Appt date"

    parameter_name = "appt_datetime"
    field_name = "appt_datetime"


@admin.register(StockRequestItem, site=edc_pharmacy_admin)
class StockRequestItemAdmin(ModelAdminMixin, admin.ModelAdmin):
    change_list_title = "Pharmacy: Requested stock items"
    show_object_tools = False
    show_cancel = True
    list_per_page = 20
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
            "Section B",
            {
                "fields": ("received", "received_datetime"),
            },
        ),
        (
            "Section C",
            {
                "fields": ("allocation",),
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
        "transferred",
        "allocation_changelist",
        "assignment",
    )

    list_filter = (
        StockItemAllocationListFilter,
        AssignmentListFilter,
        StockRequestItemPendingListFilter,
        "visit_code",
        ApptDatetimeListFilter,
    )
    readonly_fields = ("rx", "allocation")

    search_fields = (
        "id",
        "registered_subject__subject_identifier",
        "stock_request__request_identifier",
        "allocation__id",
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

    @admin.display(description="Product")
    def formulation(self, obj):
        return format_html(f"{obj.stock_request.formulation}<BR>{obj.stock_request.container}")

    @admin.display(description="Date", ordering="request_item_datetime")
    def item_date(self, obj):
        if obj.request_item_datetime:
            return to_local(obj.request_item_datetime).date()
        return None

    @admin.display(
        description="Allocation",
        ordering="allocation__registered_subject__subject_identifier",
    )
    def allocation_subject(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_allocation_changelist")
        url = f"{url}?q={obj.allocation.id}"
        context = dict(
            url=url,
            label=obj.allocation.registered_subject.subject_identifier,
            title="Go to allocation",
        )
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Assignment", ordering="allocation__assignment")
    def assignment(self, obj):
        return obj.allocation.assignment

    @admin.display(description="T", boolean=True)
    def transferred(self, obj):
        return obj.allocation.stock.location == obj.stock_request.location

    @admin.display(description="Subject", ordering="registered_subject__subject_identifier")
    def subject(self, obj):
        appt_date = to_local(obj.appt_datetime).date() if obj.appt_datetime else None
        context = dict(
            appt_date=appt_date,
            subject_identifier=obj.registered_subject.subject_identifier,
            visit_code_and_seq=f"{obj.visit_code}.{obj.visit_code_sequence}",
            changelist_url=reverse(
                "edc_pharmacy_admin:edc_pharmacy_stockrequestitem_changelist"
            ),
        )

        return render_to_string(
            "edc_pharmacy/stock/subject_list_display.html", context=context
        )

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

    @admin.display(description="Allocation #")
    def allocation_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_allocation_changelist")
        url = f"{url}?q={obj.allocation.id}"
        context = dict(
            url=url,
            label=f"{obj.allocation.allocation_identifier}",
            title="Allocation",
        )
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ("stock_request",)
        return self.readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "stock_request" and request.GET.get("stock_request"):
            kwargs["queryset"] = db_field.related_model.objects.filter(
                pk=request.GET.get("rx", 0)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
