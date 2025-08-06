from typing import Optional

from celery.result import AsyncResult
from celery.states import SUCCESS
from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django_audit_fields import audit_fieldset_tuple
from edc_constants.constants import CANCELLED, COMPLETE, PENDING
from edc_model_admin.history import SimpleHistoryAdmin
from edc_utils.date import to_local
from rangefilter.filters import DateRangeFilterBuilder

from ...admin_site import edc_pharmacy_admin
from ...forms import StockRequestForm
from ...models import StockRequest
from ..actions import allocate_stock_to_subject, prepare_stock_request_items_action
from ..actions.print_labels import print_labels_from_stock_request_by_code
from ..model_admin_mixin import ModelAdminMixin
from ..utils import stock_request_status_counts


class StatusListFilter(admin.SimpleListFilter):
    title = _("Status")
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return (
            (PENDING, _("Pending")),
            (COMPLETE, _("Complete")),
            (CANCELLED, _("Cancelled")),
            ("ZERO", _("Zero total")),
        )

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == PENDING:
                return (
                    queryset.filter(
                        stockrequestitem__allocation__isnull=True, cancel__isnull=True
                    )
                    .exclude(item_count=0)
                    .distinct()
                )
            elif self.value() == COMPLETE:
                return (
                    queryset.filter(cancel__isnull=True)
                    .exclude(stockrequestitem__allocation__isnull=True)
                    .exclude(item_count=0)
                    .distinct()
                )
            elif self.value() == CANCELLED:
                return queryset.filter(cancel__isnull=False)
            elif self.value() == "ZERO":
                return queryset.filter(item_count=0, cancel__isnull=True)
        return None


@admin.register(StockRequest, site=edc_pharmacy_admin)
class StockRequestAdmin(ModelAdminMixin, SimpleHistoryAdmin):
    change_list_title = "Pharmacy: Request for stock"
    history_list_display = ()
    show_object_tools = True
    show_cancel = True
    list_per_page = 20
    ordering = ("-request_identifier",)

    autocomplete_fields = ["container", "formulation", "location"]
    form = StockRequestForm

    actions = [
        prepare_stock_request_items_action,
        allocate_stock_to_subject,
        print_labels_from_stock_request_by_code,
        "delete_selected",
    ]

    fieldsets = (
        (
            "Section A",
            {
                "fields": (
                    "request_identifier",
                    "request_datetime",
                    "start_datetime",
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
        "stock_start_date",
        "stock_cutoff_date",
        "requested_from",
        "product_column",
        "stock_request_status",
        "links_changelist",
        "task_status",
    )

    list_filter = (
        "location",
        ("request_datetime", DateRangeFilterBuilder()),
        StatusListFilter,
        "formulation",
        "container",
        "start_datetime",
        "cutoff_datetime",
    )

    search_fields = (
        "id",
        "request_identifier",
        "stockrequestitem__allocation__id",
        "stockrequestitem__allocation__stock__id",
    )

    readonly_fields = ("item_count",)

    def redirect_url(self, request, obj, post_url_continue=None) -> Optional[str]:
        """Redirect to the review page immediately after saving model."""
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
                "start_datetime",
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
        return format_html(
            "{}",
            mark_safe("<BR>".join(str(obj.container).split(" "))),  # nosec B703, B308
        )

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

    @admin.display(description="Links")
    def links_changelist(self, obj):
        links = []
        # stockrequestitems
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stockrequestitem_changelist")
        url = f"{url}?q={obj.request_identifier}"
        context = dict(url=url, label="Requested", title="Go to stock request items")
        links.append(context)
        # allocations
        url = reverse("edc_pharmacy_admin:edc_pharmacy_allocation_changelist")
        url = f"{url}?q={obj.id}"
        context = dict(
            url=url,
            label="Allocations",
            title="Go to allocation",
        )
        links.append(context)
        # stock
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")
        url = f"{url}?q={obj.id}"
        context = dict(url=url, label="Stock", title="Go to stock")
        links.append(context)
        return render_to_string(
            "edc_pharmacy/stock/stock_request_links_column.html",
            context={"links": links},
        )

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

    @admin.display(description="Request date", ordering="request_datetime")
    def stock_request_date(self, obj):
        return to_local(obj.request_datetime).date()

    @admin.display(description="Start", ordering="start_datetime")
    def stock_start_date(self, obj):
        if obj and obj.start_datetime:
            return to_local(obj.start_datetime).date()
        return None

    @admin.display(description="Cutoff", ordering="cutoff_datetime")
    def stock_cutoff_date(self, obj):
        if obj and obj.cutoff_datetime:
            return to_local(obj.cutoff_datetime).date()
        return None
