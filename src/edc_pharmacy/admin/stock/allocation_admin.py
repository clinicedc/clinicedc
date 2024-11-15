from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext
from django_audit_fields import audit_fieldset_tuple
from edc_utils.date import to_local

from ...admin_site import edc_pharmacy_admin
from ...models import Allocation
from ..list_filters import AssignmentListFilter, TransferredFilter
from ..model_admin_mixin import ModelAdminMixin


@admin.register(Allocation, site=edc_pharmacy_admin)
class AllocationAdmin(ModelAdminMixin, admin.ModelAdmin):
    change_list_title = "Pharmacy: Allocations"
    change_form_title = "Pharmacy: Allocation"
    show_object_tools = True
    show_cancel = True
    list_per_page = 20

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
        "dashboard",
        "stock_changelist",
        "stock_request_changelist",
        "stock_product",
        "stock_container",
        "allocated_by",
    )

    list_filter = (
        AssignmentListFilter,
        "allocation_datetime",
        TransferredFilter,
        "allocated_by",
    )

    search_fields = ("id", "stock_request_item__id", "stock_request_item__stock_request__id")

    readonly_fields = (
        "assignment",
        "allocation_identifier",
        "allocation_datetime",
        "registered_subject",
        "stock_request_item",
        "allocated_by",
    )

    @admin.display(description="ALLOCATION #", ordering="allocation_identifier")
    def identifier(self, obj):
        return obj.allocation_identifier.split("-")[0]

    @admin.display(description="Allocation date", ordering="allocation_datetime")
    def allocation_date(self, obj):
        return to_local(obj.allocation_datetime).date()

    @admin.display(description="T", boolean=True)
    def transferred(self, obj):
        return obj.stock.location == obj.stock_request_item.stock_request.location

    @admin.display(description="Product", ordering="stock__product")
    def stock_product(self, obj):
        return obj.stock.product

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
