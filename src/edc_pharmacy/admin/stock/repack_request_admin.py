from decimal import Decimal

from celery.states import PENDING
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields import audit_fieldset_tuple
from rangefilter.filters import DateRangeFilterBuilder

from edc_model_admin.history import SimpleHistoryAdmin
from edc_utils.celery import get_task_result
from edc_utils.date import to_local

from ...admin_site import edc_pharmacy_admin
from ...forms import RepackRequestForm
from ...models import RepackRequest
from ...utils import format_qty
from ..actions import (
    confirm_repacked_stock_action,
    print_labels_from_repack_request,
    process_repack_request_action,
)
from ..list_filters import AssignmentListFilter as BaseAssignmentListFilter
from ..model_admin_mixin import ModelAdminMixin
from ..remove_fields_for_blinded_users import remove_fields_for_blinded_users


class AssignmentListFilter(BaseAssignmentListFilter):
    title = "Assignment"
    parameter_name = "assignment"
    lookup_str = "from_stock__product__assignment__name"


@admin.register(RepackRequest, site=edc_pharmacy_admin)
class RequestRepackAdmin(ModelAdminMixin, SimpleHistoryAdmin):
    change_list_title = "Pharmacy: Repack/Decant request"
    change_form_title = "Pharmacy: Repack/Decant"
    history_list_display = ()

    show_object_tools = True
    show_cancel = True
    list_per_page = 20

    ordering = ("-repack_identifier",)

    autocomplete_fields = ["from_stock", "container"]
    form = RepackRequestForm
    actions = [
        process_repack_request_action,
        print_labels_from_repack_request,
        confirm_repacked_stock_action,
    ]

    change_list_note = render_to_string(
        "edc_pharmacy/stock/instructions/repack_instructions.html"
    )

    fieldsets = (
        (
            "Section A: Repack",
            {
                "fields": (
                    "repack_identifier",
                    "repack_datetime",
                    "from_stock",
                    "container",
                    "requested_qty",
                    "processed_qty",
                )
            },
        ),
        (
            "Task",
            {"classes": ("collapse",), "fields": ("task_id",)},
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "repack_date",
        "from_stock_changelist",
        "assignment",
        "stock_changelist",
        "formatted_requested_qty",
        "formatted_processed_qty",
        "confirmed_qty",
        "container",
        "from_stock__product__name",
        "task_status",
    )

    list_filter = (
        ("repack_datetime", DateRangeFilterBuilder()),
        AssignmentListFilter,
    )

    search_fields = (
        "id",
        "container__name",
        "from_stock__code",
    )

    readonly_fields = ("processed_qty", "task_id")

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

    @admin.display(description="Repack date", ordering="repack_datetime")
    def repack_date(self, obj):
        return to_local(obj.repack_datetime).date()

    @admin.display(
        description="Assignment",
        ordering="from_stock__product__assignment__display_name",
    )
    def assignment(self, obj):
        return obj.from_stock.product.assignment.display_name

    @admin.display(description="Stock")
    def stock_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")
        url = f"{url}?q={obj.id}"
        context = dict(url=url, label="Stock", title="Go to stock")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="From stock", ordering="from_stock__code")
    def from_stock_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")
        url = f"{url}?q={obj.from_stock.code}&decanted=No"
        context = dict(url=url, label=obj.from_stock.code, title="Go to stock")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="REPACK #", ordering="-repack_identifier")
    def identifier(self, obj):
        return obj.repack_identifier

    @admin.display(description="Requested", ordering="requested_qty")
    def formatted_requested_qty(self, obj):
        return format_qty(obj.requested_qty, obj.container)

    @admin.display(description="Created", ordering="processed_qty")
    def formatted_processed_qty(self, obj):
        result = get_task_result(obj)
        if getattr(result, "status", "") == PENDING:
            return PENDING
        return format_qty(obj.processed_qty, obj.container)

    @admin.display(description="Confirmed")
    def confirmed_qty(self, obj):
        return obj.stock_set.filter(confirmation__isnull=False).count()

    @admin.display(description="Task")
    def task_status(self, obj):
        result = get_task_result(obj)
        return getattr(result, "status", None)

    def get_readonly_fields(self, request, obj=None):
        if obj and (obj.processed_qty or Decimal(0)) > Decimal(0):
            f = [
                "repack_identifier",
                "repack_datetime",
                "container",
                "from_stock",
            ]
            return self.readonly_fields + tuple(f)
        return self.readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "from_stock" and request.GET.get("from_stock"):
            kwargs["queryset"] = db_field.related_model.objects.filter(
                pk=request.GET.get("from_stock", 0)
            )
            kwargs["widget"] = AutocompleteSelect(
                db_field.remote_field, self.admin_site, using=kwargs.get("using")
            )

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
