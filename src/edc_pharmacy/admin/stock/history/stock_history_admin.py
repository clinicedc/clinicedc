from django.contrib import admin
from edc_model_admin.history import SimpleHistoryAdmin

from ....admin_site import edc_pharmacy_history_admin
from ....models import Stock
from ...model_admin_mixin import ModelAdminMixin
from .modeladmin_mixins import HistoricalModelAdminMixin


@admin.register(Stock.history.model, site=edc_pharmacy_history_admin)
class StockHistoryAdmin(ModelAdminMixin, HistoricalModelAdminMixin, SimpleHistoryAdmin):
    change_list_title = "Pharmacy: Stock (History)"
    change_form_title = "Pharmacy: Stock (History)"
    history_list_display = ()
    show_object_tools = True
    show_cancel = True
    list_per_page = 20

    list_display = (
        "code",
        "history_type",
        "formatted_history_date",
        "qty",
        "status",
        "subject_identifier",
        "formatted_in_transit",
        "formatted_confirmed_at_location",
        "formatted_dispensed",
        "revision",
        "history_id",
    )

    search_fields = ("code",)

    @admin.display(description="T", ordering="in_transit", boolean=True)
    def formatted_in_transit(self, obj):
        return obj.in_transit

    @admin.display(description="CL", ordering="confirmed_at_location", boolean=True)
    def formatted_confirmed_at_location(self, obj):
        return obj.confirmed_at_location

    @admin.display(description="D", ordering="dispensed", boolean=True)
    def formatted_dispensed(self, obj):
        return obj.dispensed
