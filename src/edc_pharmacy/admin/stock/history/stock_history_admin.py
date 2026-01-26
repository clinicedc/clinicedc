from django.contrib import admin
from edc_model.admin import HistoricalModelAdminMixin
from edc_model_admin.history import SimpleHistoryAdmin

from ....admin_site import edc_pharmacy_history_admin
from ....models import Stock
from ....utils import format_qty
from ...model_admin_mixin import ModelAdminMixin


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
        "subject_identifier",
        "location",
        "formatted_confirmed",
        "formatted_allocation",
        "formatted_in_transit",
        "formatted_confirmed_at_location",
        "formatted_dispensed",
        "qty",
        "formatted_unit_qty_in",
        "formatted_unit_qty_out",
        "unit_qty_in_out",
        "revision",
        "history_id",
    )

    search_fields = ("code",)

    @admin.display(description="C", ordering="confirmed", boolean=True)
    def formatted_confirmed(self, obj):
        return obj.confirmed

    @admin.display(description="A", boolean=True)
    def formatted_allocation(self, obj):
        return bool(obj.subject_identifier)

    @admin.display(description="T", ordering="in_transit", boolean=True)
    def formatted_in_transit(self, obj):
        return obj.in_transit

    @admin.display(description="CL", ordering="confirmed_at_location", boolean=True)
    def formatted_confirmed_at_location(self, obj):
        return obj.confirmed_at_location

    @admin.display(description="D", ordering="dispensed", boolean=True)
    def formatted_dispensed(self, obj):
        return obj.dispensed

    @admin.display(description="QTY", ordering="qty")
    def qty(self, obj):
        return format_qty(obj.qty_in - obj.qty_out, obj.container)

    @admin.display(description="IN", ordering="unit_qty_in")
    def formatted_unit_qty_in(self, obj):
        return format_qty(obj.unit_qty_in, obj.container)

    @admin.display(description="OUT", ordering="unit_qty_out")
    def formatted_unit_qty_out(self, obj):
        return format_qty(obj.unit_qty_out, obj.container)

    @admin.display(description="BAL", ordering="unit_qty_out")
    def unit_qty_in_out(self, obj):
        return format_qty(obj.unit_qty_in - obj.unit_qty_out, obj.container)
