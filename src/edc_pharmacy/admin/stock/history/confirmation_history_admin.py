from django.contrib import admin
from edc_model.admin import HistoricalModelAdminMixin
from edc_model_admin.history import SimpleHistoryAdmin
from edc_utils import to_local
from rangefilter.filters import DateRangeFilterBuilder

from ....admin_site import edc_pharmacy_history_admin
from ....models import Confirmation
from ...model_admin_mixin import ModelAdminMixin


@admin.register(Confirmation.history.model, site=edc_pharmacy_history_admin)
class ConfirmationHistoryAdmin(HistoricalModelAdminMixin, ModelAdminMixin, SimpleHistoryAdmin):
    change_list_title = "Pharmacy: Confirmation of created stock (History)"
    change_form_title = "Pharmacy: onfirmation of created stock (History)"
    change_list_note_url_name = "edc_pharmacy_admin:edc_pharmacy_confirmation_changelist"

    history_list_display = ()
    show_object_tools = True
    show_cancel = True
    list_per_page = 20

    list_display = (
        "item_id",
        "item_date",
        "history_type",
        "formatted_history_date",
        "code",
        "revision",
        "history_id",
    )

    list_filter = (
        "history_type",
        ("history_date", DateRangeFilterBuilder()),
    )

    search_fields = (
        "code",
        "history_id",
        "confirmation_identifier",
    )

    @admin.display(description="ITEM#", ordering="confirmation_identifier")
    def item_id(self, obj):
        return obj.confirmation_identifier

    @admin.display(description="Date", ordering="confirmed_datetime")
    def item_date(self, obj):
        if obj.confirmed_datetime:
            return to_local(obj.confirmed_datetime).date()
        return None
