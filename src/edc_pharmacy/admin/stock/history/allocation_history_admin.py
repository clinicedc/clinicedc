from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from edc_model.admin import HistoricalModelAdminMixin
from edc_model_admin.history import SimpleHistoryAdmin

from ....admin_site import edc_pharmacy_history_admin
from ....models import Allocation
from ...model_admin_mixin import ModelAdminMixin


@admin.register(Allocation.history.model, site=edc_pharmacy_history_admin)
class AllocationHistoryAdmin(ModelAdminMixin, HistoricalModelAdminMixin, SimpleHistoryAdmin):
    change_list_title = "Pharmacy: Allocations (History)"
    change_form_title = "Pharmacy: Allocation (History)"
    change_list_note_url_name = "edc_pharmacy_admin:edc_pharmacy_allocation_changelist"
    history_list_display = ()
    show_object_tools = True
    show_cancel = True
    list_per_page = 20

    list_display = (
        "subject_identifier",
        "history_type",
        "formatted_history_date",
        "code",
        "stock_changelist",
        "allocation_identifier",
        "revision",
        "history_id",
    )

    search_fields = ("code", "subject_identifier", "allocation_identifier")

    @admin.display(description="Stock #")
    def stock_changelist(self, obj):
        url = reverse("edc_pharmacy_history_admin:edc_pharmacy_historicalstock_changelist")
        url = f"{url}?q={obj.code}"
        context = dict(url=url, label=f"{obj.code}", title="Go to stock")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
