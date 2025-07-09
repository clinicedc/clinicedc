from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.template.loader import render_to_string
from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext
from django_audit_fields import audit_fieldset_tuple
from edc_constants.constants import NO, YES
from edc_model_admin.history import SimpleHistoryAdmin
from edc_utils.date import to_local
from rangefilter.filters import DateRangeFilterBuilder

from ...admin_site import edc_pharmacy_admin
from ...models import Allocation
from ..list_filters import AssignmentListFilter
from ..model_admin_mixin import ModelAdminMixin
from ..remove_fields_for_blinded_users import remove_fields_for_blinded_users


class TransferredFilter(SimpleListFilter):
    title = "Transferred"
    parameter_name = "transferred"

    def lookups(self, request, model_admin):
        return (YES, YES), (NO, NO)

    def queryset(self, request, queryset):
        qs = None
        if self.value():
            if self.value() == YES:
                qs = queryset.filter(stock__stocktransferitem__isnull=False)
            elif self.value() == NO:
                qs = queryset.filter(stock__stocktransferitem__isnull=True)
        return qs


class DispensedFilter(SimpleListFilter):
    title = "Dispensed"
    parameter_name = "dispensed"

    def lookups(self, request, model_admin):
        return (YES, YES), (NO, NO)

    def queryset(self, request, queryset):
        qs = None
        if self.value():
            if self.value() == YES:
                qs = queryset.filter(stock__dispenseitem__isnull=False)
            elif self.value() == NO:
                qs = queryset.filter(stock__dispenseitem_isnull=True)
        return qs


class HasStockFilter(SimpleListFilter):
    title = "Orphaned"
    parameter_name = "orphaned"

    def lookups(self, request, model_admin):
        return (YES, YES), (NO, NO)

    def queryset(self, request, queryset):
        qs = None
        if self.value():
            if self.value() == YES:
                qs = queryset.filter(stock__isnull=True)
            elif self.value() == NO:
                qs = queryset.filter(stock__isnull=False)
        return qs


@admin.register(Allocation, site=edc_pharmacy_admin)
class AllocationAdmin(ModelAdminMixin, SimpleHistoryAdmin):

    change_list_title = "Pharmacy: Allocations"
    change_form_title = "Pharmacy: Allocation"
    history_list_display = ()
    show_object_tools = True
    show_cancel = True
    list_per_page = 20

    actions = ["delete_selected"]

    ordering = (
        "registered_subject__subject_identifier",
        "allocation_datetime",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "allocation_identifier",
                    "allocation_datetime",
                    "stock_request_item",
                    "registered_subject",
                    "allocated_by",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "allocation_date",
        "transferred",
        "dispensed",
        "dashboard",
        "stock_changelist",
        "stock_request_changelist",
        "stock_product",
        "stock_container",
        "assignment",
        "allocated_by",
    )

    list_filter = (
        "stock__location",
        AssignmentListFilter,
        ("allocation_datetime", DateRangeFilterBuilder()),
        TransferredFilter,
        DispensedFilter,
        "allocated_by",
        HasStockFilter,
    )

    search_fields = (
        "id",
        "stock__code",
        "stock_request_item__id",
        "stock_request_item__stock_request__id",
        "registered_subject__subject_identifier",
    )

    readonly_fields = (
        "assignment",
        "allocation_identifier",
        "allocation_datetime",
        "registered_subject",
        "stock_request_item",
        "allocated_by",
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

    @admin.display(description="ALLOCATION #", ordering="allocation_identifier")
    def identifier(self, obj):
        return obj.allocation_identifier.split("-")[0]

    @admin.display(description="Allocation date", ordering="allocation_datetime")
    def allocation_date(self, obj):
        return to_local(obj.allocation_datetime).date()

    @admin.display(description="T", boolean=True)
    def transferred(self, obj):
        return True if obj.stock.stocktransferitem else False

    @admin.display(description="D", boolean=True)
    def dispensed(self, obj):
        if obj and getattr(obj, "stock", None):
            return True if getattr(obj.stock, "dispense", None) else False
        return None

    @admin.display(description="Product", ordering="stock__product")
    def stock_product(self, obj):
        return obj.stock.product.name

    @admin.display(description="Assignment", ordering="stock__product__assignment")
    def assignment(self, obj):
        return obj.stock.product.assignment

    @admin.display(description="Product", ordering="stock__product")
    def stock_container(self, obj):
        return obj.stock.container

    @admin.display(description="Request #")
    def stock_request_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stockrequest_changelist")
        url = f"{url}?q={obj.stock_request_item.stock_request.id}"
        context = dict(
            url=url,
            label=f"{obj.stock_request_item.stock_request.request_identifier}",
            title="Go to stock request",
        )
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Stock #")
    def stock_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")
        url = f"{url}?q={obj.stock.code}"
        context = dict(url=url, label=f"{obj.stock.code}", title="Go to stock")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Subject #", ordering="registered_subject__subject_identifier")
    def dashboard(self, obj=None, label=None):
        context = {}
        try:
            url = reverse(
                self.get_subject_dashboard_url_name(),
                kwargs={"subject_identifier": obj.registered_subject.subject_identifier},
            )
        except NoReverseMatch:
            url = None
        else:
            context = dict(
                title=gettext("Go to subject dashboard"),
                url=url,
                label=obj.registered_subject.subject_identifier,
            )
        if url:
            return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
        return None
