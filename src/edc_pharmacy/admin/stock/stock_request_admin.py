from typing import Optional

from celery.result import AsyncResult
from celery.states import SUCCESS
from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django_audit_fields import audit_fieldset_tuple
from edc_utils.date import to_local

from ...admin_site import edc_pharmacy_admin
from ...forms import StockRequestForm
from ...models import StockRequest
from ..actions import allocate_stock_to_subject, prepare_stock_request_items_action
from ..model_admin_mixin import ModelAdminMixin
from ..utils import stock_request_status_counts


@admin.register(StockRequest, site=edc_pharmacy_admin)
class StockRequestAdmin(ModelAdminMixin, admin.ModelAdmin):
    change_list_title = "Pharmacy: Request for stock"
    show_object_tools = True
    show_cancel = True
    list_per_page = 20

    autocomplete_fields = ["container", "formulation", "location"]
    form = StockRequestForm

    actions = [
        prepare_stock_request_items_action,
        allocate_stock_to_subject,
    ]

    fieldsets = (
        (
            "Section A",
            {
                "fields": (
                    "request_identifier",
                    "request_datetime",
                    "cutoff_datetime",
                    "location",
                )
            },
        ),
        (
            "Section B",
            {"fields": ("formulation", "container", "containers_per_subject")},
        ),
        (
            "Section C",
            {"fields": ("item_count",)},
        ),
        (
            "Section D: Customize this request",
            {"fields": ("subject_identifiers", "excluded_subject_identifiers")},
        ),
        (
            "Section E: Cancel this request",
            {
                "description": (
                    "A request may only be cancelled before stock is allocated by "
                    "the central pharmacy. The EDC will check if the request may be cancelled."
                ),
                "fields": ("cancel",),
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "stock_request_id",
        "stock_request_date",
        "requested_from",
        "product_column",
        "stock_request_status",
        "stock_request_items",
        "allocation_changelist",
        "stock_changelist",
        "task_status",
    )

    list_filter = (
        "request_datetime",
        "formulation",
        "container",
        "location",
    )

    search_fields = ("id", "request_identifier")

    readonly_fields = ("item_count",)

    def redirect_url(self, request, obj, post_url_continue=None) -> Optional[str]:
        redirect_url = super().redirect_url(request, obj, post_url_continue)
        if obj.cancel == "CANCEL":
            pass
        elif not obj.stockrequestitem_set.all().exists():
            redirect_url = reverse(
                "edc_pharmacy:review_stock_request_url", kwargs={"stock_request": obj.pk}
            )
        return redirect_url

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        if obj and obj.stockrequestitem_set.all().exists():
            fields = (
                "request_identifier",
                "request_datetime",
                "cutoff_datetime",
                "location",
                "formulation",
                "container",
                "containers_per_subject",
                "item_count",
                "subject_identifiers",
                "excluded_subject_identifiers",
            )
        return fields

    @admin.display(description="Request #", ordering="request_identifier")
    def stock_request_id(self, obj):
        return obj.request_identifier

    @admin.display(description="PER", ordering="containers_per_subject")
    def per_subject(self, obj):
        return obj.containers_per_subject

    @admin.display(description="From", ordering="location")
    def requested_from(self, obj):
        return obj.location

    @admin.display(description="items", ordering="item_count")
    def request_item_count(self, obj):
        return obj.item_count

    @admin.display(description="Container", ordering="container_name")
    def container_str(self, obj):
        return format_html("<BR>".join(str(obj.container).split(" ")))

    @admin.display(description="Task")
    def task_status(self, obj):
        if obj.task_id:
            result = AsyncResult(str(obj.task_id))
            return getattr(result, "status", None)
        return None

    @admin.display(description="Product")
    def product_column(self, obj):
        context = dict(
            formulation=obj.formulation,
            containers_per_subject=obj.containers_per_subject,
            container=obj.container,
        )
        return render_to_string(
            "edc_pharmacy/stock/stock_request_product_column.html", context=context
        )

    @admin.display(description="Requested items")
    def stock_request_items(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stockrequestitem_changelist")
        url = f"{url}?q={obj.request_identifier}"
        context = dict(url=url, label="Request items", title="Go to stock request items")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(
        description="Allocation",
        ordering="allocation__registered_subject__subject_identifier",
    )
    def allocation_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_allocation_changelist")
        url = f"{url}?q={obj.id}"
        context = dict(
            url=url,
            label="Allocations",
            title="Go to allocation",
        )
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Stock")
    def stock_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")
        url = f"{url}?q={obj.id}"
        context = dict(url=url, label="Stock", title="Go to stock")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Status")
    def stock_request_status(self, obj):
        if obj.cancel == "CANCEL":
            return "CANCELLED"
        context = stock_request_status_counts(obj)
        context.update(task_status=self.task_status(obj), success=SUCCESS)
        return render_to_string(
            "edc_pharmacy/stock/stock_request_status_column.html",
            context=context,
        )

    @admin.display(description="Request date")
    def stock_request_date(self, obj):
        return to_local(obj.request_datetime).date()
