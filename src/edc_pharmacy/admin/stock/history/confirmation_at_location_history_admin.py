from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from edc_model.admin import HistoricalModelAdminMixin
from edc_model_admin.history import SimpleHistoryAdmin
from edc_utils import to_local
from rangefilter.filters import DateRangeFilterBuilder

from ....admin_site import edc_pharmacy_history_admin
from ....models import ConfirmationAtLocation
from ...model_admin_mixin import ModelAdminMixin


@admin.register(ConfirmationAtLocation.history.model, site=edc_pharmacy_history_admin)
class ConfirmationAtLocationHistoryAdmin(
    HistoricalModelAdminMixin, ModelAdminMixin, SimpleHistoryAdmin
):
    change_list_title = "Pharmacy: Stock confirmations at site (History)"
    change_form_title = "Pharmacy: Stock confirmation at site (History)"
    change_list_note_url_name = (
        "edc_pharmacy_admin:edc_pharmacy_confirmationatlocation_changelist"
    )

    history_list_display = ()
    show_object_tools = True
    show_cancel = True
    list_per_page = 20

    list_display = (
        "item_id",
        "item_date",
        "history_type",
        "formatted_history_date",
        # "confirm_at_location_changelist",
        "stock_transfer",
        "location",
        "revision",
        "history_id",
    )

    list_filter = (
        "history_type",
        ("history_date", DateRangeFilterBuilder()),
        "location",
    )

    search_fields = (
        "history_id",
        "transfer_confirmation_identifier",
        "stock_transfer__transfer_identifier",
    )

    @admin.display(description="ITEM#", ordering="transfer_confirmation_identifier")
    def item_id(self, obj):
        return obj.transfer_confirmation_identifier

    @admin.display(description="Date", ordering="transfer_confirmation_datetime")
    def item_date(self, obj):
        if obj.transfer_confirmation_datetime:
            return to_local(obj.transfer_confirmation_datetime).date()
        return None

    @admin.display(description="Confirmation#")
    def confirm_at_location_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_confirmationatlocation_changelist")
        url = f"{url}?q={obj.confirm_at_location.transfer_confirmation_identifier}"
        context = dict(
            url=url,
            label=f"{obj.confirm_at_location.transfer_confirmation_identifier}",
            title="Go to confirmation at site",
        )
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
