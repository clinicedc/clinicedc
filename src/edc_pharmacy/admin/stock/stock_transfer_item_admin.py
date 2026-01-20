from clinicedc_constants import NO, YES
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields import audit_fieldset_tuple
from edc_model_admin.history import SimpleHistoryAdmin
from edc_utils.date import to_local
from rangefilter.filters import DateRangeFilterBuilder

from ...admin_site import edc_pharmacy_admin
from ...models import StockTransferItem
from ..model_admin_mixin import ModelAdminMixin


class ConfirmedAtLocationFilter(SimpleListFilter):
    title = "Confirmed at location"
    parameter_name = "confirmed_at_location"

    def lookups(self, request, model_admin):  # noqa: ARG002
        return (YES, YES), (NO, NO)

    def queryset(self, request, queryset):  # noqa: ARG002
        qs = None
        if self.value():
            opts = dict(
                stock__from_stock__isnull=False,
                stock__confirmation__isnull=False,
                stock__allocation__isnull=False,
            )
            if self.value() == YES:
                qs = queryset.filter(
                    confirmationatlocationitem__isnull=False,
                    **opts,
                )
            elif self.value() == NO:
                qs = queryset.filter(
                    confirmationatlocationitem__isnull=True,
                    **opts,
                )
        return qs


@admin.register(StockTransferItem, site=edc_pharmacy_admin)
class StockTransferItemAdmin(ModelAdminMixin, SimpleHistoryAdmin):
    change_list_title = "Pharmacy: Stock Transfer Item"
    change_form_title = "Pharmacy: Stock Transfer Items"
    change_list_note = "D=Dispensed"
    history_list_display = ()
    show_object_tools = True
    show_cancel = True
    list_per_page = 20

    autocomplete_fields = ("stock",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "transfer_item_identifier",
                    "transfer_item_datetime",
                    "stock_transfer",
                    "stock",
                )
            },
        ),
        audit_fieldset_tuple,
    )
    list_display = (
        "identifier",
        "stock_transfer_changelist",
        "transfer_item_date",
        "stock_changelist",
        "allocation_changelist",
        "confirmation_at_location_item_changelist",
        "dispensed",
        "formatted_from_location",
        "formatted_to_location",
    )

    list_filter = (
        "stock_transfer__to_location",
        ("transfer_item_datetime", DateRangeFilterBuilder()),
        ConfirmedAtLocationFilter,
        "stock__dispensed",
    )

    search_fields = (
        "id",
        "transfer_item_identifier",
        "stock_transfer__id",
        "stock__code",
        "stock__allocation__registered_subject__subject_identifier",
    )

    readonly_fields = (
        "transfer_item_identifier",
        "transfer_item_datetime",
        "stock",
        "stock_transfer",
    )

    @admin.display(description="TRANSFER ITEM #", ordering="transfer_item_identifier")
    def identifier(self, obj):
        return obj.transfer_item_identifier

    @admin.display(description="D", ordering="stock__dispensed", boolean=True)
    def dispensed(self, obj):
        return obj.stock.dispensed

    @admin.display(description="From", ordering="stock__location")
    def formatted_from_location(self, obj):
        return obj.stock_transfer.from_location.display_name

    @admin.display(description="To", ordering="stock__location")
    def formatted_to_location(self, obj):
        if obj:
            is_current_location = obj.stock_transfer.to_location == obj.stock.location
            context = dict(
                location=obj.stock_transfer.to_location.display_name,
                is_current_location=is_current_location,
            )
            return render_to_string("edc_pharmacy/stock/location.html", context=context)
        return None

    @admin.display(description="Loc", ordering="stock__location")
    def formatted_location(self, obj):
        try:
            obj.confirmationatlocationitem  # noqa: B018
        except ObjectDoesNotExist:
            return f"{obj.stock.location.display_name} > {obj.stock_transfer.to_location.display_name}"
        else:
            return obj.stock.location.display_name

    @admin.display(description="Transfer date", ordering="transfer_item_datetime")
    def transfer_item_date(self, obj):
        return to_local(obj.transfer_item_datetime).date()

    @admin.display(description="Stock #", ordering="stock__code")
    def stock_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")
        url = f"{url}?q={obj.stock.code}"
        context = dict(url=url, label=obj.stock.code, title="Go to stock")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(
        description="Allocation",
        ordering="stock__allocation__registered_subject__subject_identifier",
    )
    def allocation_changelist(self, obj):
        subject_identifier = obj.stock.allocation.registered_subject.subject_identifier
        url = reverse("edc_pharmacy_admin:edc_pharmacy_allocation_changelist")
        url = f"{url}?q={subject_identifier}"
        context = dict(url=url, label=subject_identifier, title="Go to allocation")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Transfer #", ordering="stock_transfer__transfer_identifier")
    def stock_transfer_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stocktransfer_changelist")
        url = f"{url}?q={obj.stock_transfer.id}"
        context = dict(
            url=url,
            label=obj.stock_transfer.transfer_identifier,
            title="Go to stock transfer",
        )
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(
        description="Confirmation #",
        ordering="stock__confirmationatlocationitem__transfer_confirmation_item_identifier",
    )
    def confirmation_at_location_item_changelist(self, obj):
        try:
            transfer_confirmation_item = obj.confirmationatlocationitem
        except ObjectDoesNotExist:
            url = reverse("edc_pharmacy:confirm_at_location_url")
            context = dict(
                url=url,
                label="Pending",
                title="Go to stock transfer site confirmation",
            )
        else:
            url = reverse(
                "edc_pharmacy_admin:edc_pharmacy_confirmationatlocationitem_changelist"
            )
            url = f"{url}?q={transfer_confirmation_item.pk}"
            context = dict(
                url=url,
                label=transfer_confirmation_item.transfer_confirmation_item_identifier,
                title="Go to stock transfer confirmation item",
            )
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
