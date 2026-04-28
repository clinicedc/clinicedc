from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django_audit_fields.admin import audit_fieldset_tuple
from rangefilter.filters import DateRangeFilterBuilder

from edc_model_admin.history import SimpleHistoryAdmin
from edc_sites.admin import SiteModelAdminMixin
from edc_utils.date import to_local

from ...admin_site import edc_pharmacy_admin
from ...models import StockTake, StockTakeItem
from ..model_admin_mixin import ModelAdminMixin


class StockTakeItemInline(admin.TabularInline):
    model = StockTakeItem
    extra = 0
    can_delete = False
    fields = ("code", "status", "stock_link")
    readonly_fields = ("code", "status", "stock_link")

    @admin.display(description="Stock")
    def stock_link(self, obj):
        if obj.stock:
            url = reverse(
                "edc_pharmacy_admin:edc_pharmacy_stock_change", args=[obj.stock.pk]
            )
            return render_to_string(
                "edc_pharmacy/stock/items_as_link.html",
                context={"url": url, "label": obj.stock.code, "title": "Go to stock"},
            )
        return "—"

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(StockTake, site=edc_pharmacy_admin)
class StockTakeAdmin(SiteModelAdminMixin, ModelAdminMixin, SimpleHistoryAdmin):

    def get_view_only_site_ids_for_user(self, request) -> list[int]:
        return [s.id for s in request.user.userprofile.sites.all() if s.id != request.site.id]
    change_list_title = "Pharmacy: Stock Takes"
    change_form_title = "Pharmacy: Stock Take"
    history_list_display = ()
    show_object_tools = True
    show_cancel = True
    list_per_page = 20

    inlines = [StockTakeItemInline]

    fieldsets = (
        (
            "Stock Take",
            {
                "fields": (
                    "stock_take_identifier",
                    "storage_bin",
                    "stock_take_datetime",
                    "performed_by",
                    "status",
                )
            },
        ),
        (
            "Counts",
            {
                "fields": (
                    "expected_count",
                    "scanned_count",
                    "matched_count",
                    "missing_count",
                    "unexpected_count",
                )
            },
        ),
        (
            "Notes",
            {"fields": ("note",)},
        ),
        audit_fieldset_tuple,
    )

    readonly_fields = (
        "stock_take_identifier",
        "storage_bin",
        "stock_take_datetime",
        "performed_by",
        "expected_count",
        "scanned_count",
        "matched_count",
        "missing_count",
        "unexpected_count",
    )

    list_display = (
        "identifier",
        "bin",
        "bin_site",
        "take_date",
        "status",
        "expected_count",
        "matched_count",
        "missing_count",
        "unexpected_count",
        "results_link",
        "performed_by",
    )

    list_filter = (
        "status",
        ("stock_take_datetime", DateRangeFilterBuilder()),
        "storage_bin__location__display_name",
    )

    search_fields = (
        "stock_take_identifier",
        "storage_bin__bin_identifier",
        "storage_bin__name",
        "performed_by__username",
    )

    ordering = ("-stock_take_datetime",)

    @admin.display(description="Stock take #", ordering="-stock_take_identifier")
    def identifier(self, obj):
        return obj.stock_take_identifier

    @admin.display(description="Bin", ordering="storage_bin__bin_identifier")
    def bin(self, obj):
        b = obj.storage_bin
        label = format_html("<code>{}</code>", b.bin_identifier)
        if b.name and b.name != b.bin_identifier:
            label = format_html("{} ({})", label, b.name)
        return label

    @admin.display(description="Site", ordering="storage_bin__location__display_name")
    def bin_site(self, obj):
        b = obj.storage_bin
        if b.location.site:
            return b.location.site.name
        return b.location.display_name or b.location.name

    @admin.display(description="Date", ordering="stock_take_datetime")
    def take_date(self, obj):
        return to_local(obj.stock_take_datetime).date()

    @admin.display(description="Results")
    def results_link(self, obj):
        url = reverse(
            "edc_pharmacy:stock_take_results_url",
            kwargs={"stock_take": obj.pk},
        )
        context = dict(url=url, label="Results", title="View stock take results")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
