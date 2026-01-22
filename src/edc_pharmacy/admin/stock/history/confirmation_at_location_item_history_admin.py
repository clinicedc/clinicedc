from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from edc_model.admin import HistoricalModelAdminMixin
from edc_model_admin.history import SimpleHistoryAdmin
from edc_utils import to_local
from rangefilter.filters import DateRangeFilterBuilder

from ....admin_site import edc_pharmacy_history_admin
from ....models import ConfirmationAtLocationItem
from ...model_admin_mixin import ModelAdminMixin


@admin.register(ConfirmationAtLocationItem.history.model, site=edc_pharmacy_history_admin)
class ConfirmationAtLocationItemHistoryAdmin(
    ModelAdminMixin, HistoricalModelAdminMixin, SimpleHistoryAdmin
):
    change_list_title = "Pharmacy: Stock confirmation items at location (History)"
    change_form_title = "Pharmacy: Stock confirmation item at location (History)"
    change_list_note_url_name = (
        "edc_pharmacy_admin:edc_pharmacy_confirmationatlocationitem_changelist"
    )
    history_list_display = ()
    show_object_tools = True
    show_cancel = True
    list_per_page = 20

    list_display = (
        "item_id",
        "history_type",
        "formatted_history_date",
        "location_name",
        "code",
        "confirm_at_location_changelist",
        "revision",
        "history_id",
    )

    list_filter = (
        "history_type",
        ("history_date", DateRangeFilterBuilder()),
        ("transfer_confirmation_item_datetime", DateRangeFilterBuilder()),
    )

    search_fields = (
        "code",
        "history_id",
        "transfer_confirmation_item_identifier",
        "confirm_at_location__transfer_confirmation_identifier",
    )

    @admin.display(description="ITEM#", ordering="transfer_confirmation_item_identifier")
    def item_id(self, obj):
        return obj.transfer_confirmation_item_identifier

    @admin.display(description="Date", ordering="transfer_confirmation_item_datetime")
    def item_date(self, obj):
        if obj.transfer_confirmation_item_datetime:
            return to_local(obj.transfer_confirmation_item_datetime).date()
        return None

    @admin.display(
        description="Location", ordering="confirmation_at_location__location__display_name"
    )
    def location(self, obj):
        if obj:
            return obj.confirmation_at_location.location.display_name
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
