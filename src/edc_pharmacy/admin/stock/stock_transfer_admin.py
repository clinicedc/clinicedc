from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import Count
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields import audit_fieldset_tuple
from rangefilter.filters import DateRangeFilterBuilder

from edc_constants.constants import NO, PARTIAL, YES
from edc_model_admin.history import SimpleHistoryAdmin
from edc_utils.date import to_local

from ...admin_site import edc_pharmacy_admin
from ...forms import StockTransferForm
from ...models import ConfirmationAtSiteItem, StockTransfer, StockTransferItem
from ..actions import print_transfer_stock_manifest_action, transfer_stock_action
from ..model_admin_mixin import ModelAdminMixin


class ConfirmedAtSiteListFilter(SimpleListFilter):
    title = "Confirmed at site"
    parameter_name = "confirmed_at_site"

    def lookups(self, request, model_admin):
        return (YES, YES), (PARTIAL, "Partial"), (NO, NO)

    def queryset(self, request, queryset):
        qs = None
        if self.value():
            if self.value() == YES:
                qs = (
                    queryset.filter(
                        confirmationatsite__isnull=False,
                        stocktransferitem__stock__confirmationatsiteitem__isnull=False,
                    )
                    .exclude(
                        stocktransferitem__stock__confirmationatsiteitem__isnull=True,
                    )
                    .annotate(Count("transfer_identifier"))
                )
            elif self.value() == PARTIAL:
                qs = queryset.filter(
                    confirmationatsite__isnull=False,
                    stocktransferitem__stock__confirmationatsiteitem__isnull=True,
                ).annotate(Count("transfer_identifier"))
            elif self.value() == NO:
                qs = queryset.filter(
                    confirmationatsite__isnull=True,
                    stocktransferitem__stock__confirmationatsiteitem__isnull=True,
                ).annotate(Count("transfer_identifier"))

        return qs


@admin.register(StockTransfer, site=edc_pharmacy_admin)
class StockTransferAdmin(ModelAdminMixin, SimpleHistoryAdmin):
    change_list_title = "Pharmacy: Stock Transfer"
    change_form_title = "Pharmacy: Stock Transfers"
    history_list_display = ()
    show_object_tools = True
    show_cancel = True
    list_per_page = 20
    ordering = ["-transfer_identifier"]

    autocomplete_fields = ["from_location", "to_location"]
    actions = [transfer_stock_action, print_transfer_stock_manifest_action]

    form = StockTransferForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "transfer_identifier",
                    "transfer_datetime",
                    "from_location",
                    "to_location",
                    "item_count",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "transfer_date",
        "from_location",
        "to_location",
        "stock_transfer_item_changelist",
        "stock_transfer_item_confirmed_changelist",
        "stock_transfer_item_unconfirmed_changelist",
        "stock_changelist",
    )

    list_filter = (
        ("transfer_datetime", DateRangeFilterBuilder()),
        "from_location",
        "to_location",
        ConfirmedAtSiteListFilter,
    )

    search_fields = (
        "id",
        "transfer_identifier",
        "stocktransferitem__stock__allocation__registered_subject__subject_identifier",
    )

    @admin.display(description="TRANSFER #", ordering="transfer_identifier")
    def identifier(self, obj):
        return obj.transfer_identifier

    @admin.display(description="Transfer date", ordering="transfer_datetime")
    def transfer_date(self, obj):
        return to_local(obj.transfer_datetime).date()

    @admin.display(description="Transfered")
    def stock_transfer_item_changelist(self, obj):
        count = StockTransferItem.objects.filter(stock_transfer=obj).count()
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stocktransferitem_changelist")
        url = f"{url}?q={obj.id}"
        context = dict(url=url, label=count, title="Go to stock transfer items")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Confirmed at site")
    def stock_transfer_item_confirmed_changelist(self, obj):
        num_confirmed_at_site = ConfirmationAtSiteItem.objects.filter(
            stock__stocktransferitem__stock_transfer=obj
        ).count()
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stocktransferitem_changelist")
        url = f"{url}?q={obj.id}&confirmed_at_site={YES}"
        context = dict(
            url=url,
            label=num_confirmed_at_site,
            title="Items confirmed at site",
        )
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Unconfirmed")
    def stock_transfer_item_unconfirmed_changelist(self, obj):
        num_transferred = StockTransferItem.objects.filter(
            stock_transfer=obj, stock__confirmationatsiteitem__isnull=False
        ).count()
        num_confirmed_at_site = ConfirmationAtSiteItem.objects.filter(
            stock__stocktransferitem__stock_transfer=obj
        ).count()
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stocktransferitem_changelist")
        url = f"{url}?q={obj.id}&confirmed_at_site={NO}"
        context = dict(
            url=url,
            label=num_transferred - num_confirmed_at_site,
            title="Items not confirmed at site",
        )
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Stock", ordering="stock__code")
    def stock_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")
        url = f"{url}?q={obj.id}"
        context = dict(url=url, label="Stock", title="Go to stock")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
