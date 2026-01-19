from clinicedc_constants import NO, PARTIAL, YES
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import Count
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields import audit_fieldset_tuple
from rangefilter.filters import DateRangeFilterBuilder

from edc_model_admin.history import SimpleHistoryAdmin
from edc_utils.date import to_local

from ...admin_site import edc_pharmacy_admin
from ...constants import CENTRAL_LOCATION
from ...forms import StockTransferForm
from ...models import ConfirmationAtLocationItem, Location, StockTransfer, StockTransferItem
from ..actions import print_transfer_stock_manifest_action, transfer_stock_action
from ..model_admin_mixin import ModelAdminMixin


class LocationListFilterMixin:
    title = "To location"
    parameter_name = "tolocation"

    def lookups(self, request, model_admin):  # noqa: ARG002
        locations = [
            (obj.get("name"), obj.get("display_name"))
            for obj in Location.objects.values("name", "display_name")
            .filter(name=CENTRAL_LOCATION)
            .distinct()
            .order_by("display_name")
        ]
        locations.extend(
            [
                (obj.get("name"), obj.get("display_name"))
                for obj in Location.objects.values("name", "display_name")
                .exclude(name=CENTRAL_LOCATION)
                .distinct()
                .order_by("display_name")
            ]
        )
        return tuple(locations)

    def queryset(self, request, queryset):  # noqa: ARG002
        qs = None
        if self.value():
            qs = queryset.filter(**{self.parameter_name: self.value()})
        return qs


class ToLocationListFilter(LocationListFilterMixin, SimpleListFilter):
    title = "To location"
    parameter_name = "to_location__name"


class FromLocationListFilter(LocationListFilterMixin, SimpleListFilter):
    title = "From location"
    parameter_name = "from_location__name"


class ConfirmedAtSiteListFilter(SimpleListFilter):
    title = "Confirmed at site"
    parameter_name = "confirmed_at_site"

    def lookups(self, request, model_admin):  # noqa: ARG002
        return (YES, YES), (PARTIAL, "Partial"), (NO, NO)

    def queryset(self, request, queryset):  # noqa: ARG002
        qs = None
        if self.value():
            if self.value() == YES:
                qs = (
                    queryset.filter(
                        confirmationatlocation__isnull=False,
                        stocktransferitem__confirmationatlocationitem__isnull=False,
                    )
                    .exclude(
                        stocktransferitem__confirmationatlocationitem__isnull=True,
                    )
                    .annotate(Count("transfer_identifier"))
                )
            elif self.value() == PARTIAL:
                qs = queryset.filter(
                    confirmationatlocation__isnull=False,
                    stocktransferitem__confirmationatlocationitem__isnull=True,
                ).annotate(Count("transfer_identifier"))
            elif self.value() == NO:
                qs = queryset.filter(
                    confirmationatlocation__isnull=True,
                    stocktransferitem__confirmationatlocationitem__isnull=True,
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
    ordering = ("-transfer_identifier",)

    autocomplete_fields = ("from_location", "to_location")
    actions = (transfer_stock_action, print_transfer_stock_manifest_action)

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
        "n",
        "stock_transfer_item_changelist",
        "stock_transfer_item_confirmed_changelist",
        "stock_transfer_item_unconfirmed_changelist",
        "stock_changelist",
    )

    list_filter = (
        ("transfer_datetime", DateRangeFilterBuilder()),
        FromLocationListFilter,
        ToLocationListFilter,
        ConfirmedAtSiteListFilter,
    )

    search_fields = (
        "id",
        "transfer_identifier",
        "stocktransferitem__stock__code",
        "stocktransferitem__stock__allocation__registered_subject__subject_identifier",
    )

    @admin.display(description="TRANSFER #", ordering="transfer_identifier")
    def identifier(self, obj):
        return obj.transfer_identifier

    @admin.display(description="Transfer date", ordering="transfer_datetime")
    def transfer_date(self, obj):
        return to_local(obj.transfer_datetime).date()

    @admin.display(description="n", ordering="item_count")
    def n(self, obj):
        return obj.item_count

    @admin.display(description="Transfered")
    def stock_transfer_item_changelist(self, obj):
        count = StockTransferItem.objects.filter(stock_transfer=obj).count()
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stocktransferitem_changelist")
        url = f"{url}?q={obj.id}"
        context = dict(url=url, label=count, title="Go to stock transfer items")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Confirmed")
    def stock_transfer_item_confirmed_changelist(self, obj):
        num_confirmed_at_site = ConfirmationAtLocationItem.objects.filter(
            stock_transfer_item__stock_transfer=obj
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
            stock_transfer=obj, confirmationatlocationitem__isnull=False
        ).count()
        num_confirmed_at_site = ConfirmationAtLocationItem.objects.filter(
            stock_transfer_item__stock_transfer=obj
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
