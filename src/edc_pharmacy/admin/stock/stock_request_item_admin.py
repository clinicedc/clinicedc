from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django_audit_fields import audit_fieldset_tuple
from rangefilter.filters import DateRangeFilterBuilder

from edc_model_admin.history import SimpleHistoryAdmin
from edc_model_admin.list_filters import FutureDateListFilter
from edc_utils.date import to_local

from ...admin_site import edc_pharmacy_admin
from ...forms import StockRequestItemForm
from ...models import StockRequestItem
from ..actions.print_labels import print_labels_from_stock_request_item
from ..list_filters import (
    AssignmentListFilter,
    StockItemAllocationListFilter,
    StockItemTransferredListFilter,
    StockRequestItemPendingListFilter,
)
from ..model_admin_mixin import ModelAdminMixin
from ..remove_fields_for_blinded_users import remove_fields_for_blinded_users


class ApptDatetimeListFilter(FutureDateListFilter):
    title = "Appt date"

    parameter_name = "appt_datetime"
    field_name = "appt_datetime"


@admin.register(StockRequestItem, site=edc_pharmacy_admin)
class StockRequestItemAdmin(ModelAdminMixin, SimpleHistoryAdmin):
    change_list_title = "Pharmacy: Requested stock items"
    history_list_display = ()
    show_object_tools = False
    show_cancel = True
    list_per_page = 20
    form = StockRequestItemForm
    autocomplete_fields = ["rx"]
    actions = [print_labels_from_stock_request_item, "delete_selected"]

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
                "fields": ("allocation",),
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "request_item_id",
        "item_date",
        "request_changelist",
        "allocated",
        "transferred",
        "location",
        "subject",
        "formulation",
        "allocation_changelist",
        "stock_changelist",
        "assignment",
    )

    list_filter = (
        ("request_item_datetime", DateRangeFilterBuilder()),
        "stock_request__location",
        StockItemAllocationListFilter,
        StockItemTransferredListFilter,
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
        "allocation__stock__code",
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
        return format_html(
            "{}",
            mark_safe(
                f"{obj.stock_request.formulation}<BR>{obj.stock_request.container}"
            ),  # nosec B703, B308
        )

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

    @admin.display(description="A", boolean=True)
    def allocated(self, obj):
        if obj:
            return True if getattr(obj, "allocation", None) else False
        return None

    @admin.display(description="T", boolean=True)
    def transferred(self, obj):
        if obj and getattr(obj, "allocation", None):
            return True if obj.allocation.stock.stocktransferitem else False
        return False

    @admin.display(description="Subject", ordering="appt_datetime")
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

    @admin.display(description="Stock #")
    def stock_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")
        url = f"{url}?q={obj.allocation.stock.code}"
        context = dict(url=url, label=f"{obj.allocation.stock.code}", title="Go to stock")
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
