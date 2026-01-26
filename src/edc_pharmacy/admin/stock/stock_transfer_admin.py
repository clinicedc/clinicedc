from clinicedc_constants import NO, YES
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import Count
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_audit_fields import audit_fieldset_tuple
from edc_model_admin.history import SimpleHistoryAdmin
from edc_utils.date import to_local
from rangefilter.filters import DateRangeFilterBuilder

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
    title = "Confirmed at location"
    parameter_name = "confirmed_at_location"

    def lookups(self, request, model_admin):  # noqa: ARG002
        return (YES, YES), (NO, NO)

    def queryset(self, request, queryset):  # noqa: ARG002
        qs = None
        if self.value():
            if self.value() == YES:
                qs = queryset.filter(
                    stocktransferitem__stock__confirmed_at_location=True,
                ).annotate(Count("transfer_identifier"))
            elif self.value() == NO:
                qs = queryset.filter(
                    stocktransferitem__stock__confirmed_at_location=False,
                ).annotate(Count("transfer_identifier"))

        return qs


@admin.register(StockTransfer, site=edc_pharmacy_admin)
class StockTransferAdmin(ModelAdminMixin, SimpleHistoryAdmin):
    change_list_title = "Pharmacy: Stock Transfer"
    change_form_title = "Pharmacy: Stock Transfers"
    change_list_note = "T=Transferred to location or 'in transit', CL=Confirmed at location"
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
        (
            "Comment",
            {
                "fields": (
                    "comment",
                    # "cancel",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "transfer_date",
        "location",
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

    def get_readonly_fields(self, request, obj=None) -> tuple[str, ...]:
        fields = super().get_readonly_fields(request, obj)
        if obj:
            fields = (
                *fields,
                "transfer_identifier",
                "transfer_datetime",
                "from_location",
                "to_location",
                "item_count",
            )
        return fields

    @admin.display(description="TRANSFER #", ordering="transfer_identifier")
    def identifier(self, obj):
        return obj.transfer_identifier

    @admin.display(description="Transfer date", ordering="transfer_datetime")
    def transfer_date(self, obj):
        return to_local(obj.transfer_datetime).date()

    @admin.display(description="expected", ordering="item_count")
    def n(self, obj):
        if obj.item_count != StockTransferItem.objects.filter(stock_transfer=obj).count():
            return f"{StockTransferItem.objects.filter(stock_transfer=obj).count()}/{obj.item_count}"
        return obj.item_count

    @admin.display(description="Location", ordering="to_location")
    def location(self, obj):
        return mark_safe(f"{obj.from_location}&nbsp;&gt;&gt;&nbsp;{obj.to_location}")  # noqa: S308

    @admin.display(description="T")
    def stock_transfer_item_changelist(self, obj):
        count = StockTransferItem.objects.filter(stock_transfer=obj).count()
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stocktransferitem_changelist")
        url = f"{url}?q={obj.id}"
        context = dict(url=url, label=count, title="Go to stock transfer items")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="CL")
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

    @admin.display(description="not CL")
    def stock_transfer_item_unconfirmed_changelist(self, obj):
        num = StockTransferItem.objects.filter(
            stock_transfer=obj, stock__confirmed_at_location=False
        ).count()
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stocktransferitem_changelist")
        url = f"{url}?q={obj.id}&confirmed_at_site={NO}"
        context = dict(
            url=url,
            label=num,
            title="Items not confirmed at site",
        )
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Stock", ordering="stock__code")
    def stock_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")
        url = f"{url}?q={obj.id}"
        context = dict(url=url, label="Stock", title="Go to stock")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
