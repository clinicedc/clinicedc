from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from edc_model.admin import HistoricalModelAdminMixin
from edc_model_admin.history import SimpleHistoryAdmin
from edc_utils import to_local
from rangefilter.filters import DateRangeFilterBuilder

from ....admin_site import edc_pharmacy_history_admin
from ....models import StorageBinItem
from ...model_admin_mixin import ModelAdminMixin


@admin.register(StorageBinItem.history.model, site=edc_pharmacy_history_admin)
class StorageBinItemHistoryAdmin(
    ModelAdminMixin, HistoricalModelAdminMixin, SimpleHistoryAdmin
):
    change_list_title = "Pharmacy: Storage bin items (History)"
    change_form_title = "Pharmacy: Storage bin item (History)"
    change_list_note_url_name = "edc_pharmacy_admin:edc_pharmacy_storagebinitem_changelist"
    history_list_display = ()
    show_object_tools = True
    show_cancel = True
    list_per_page = 20

    list_display = (
        "item_id",
        "history_type",
        "formatted_history_date",
        "site__id",
        "code",
        "storage_bin_changelist",
        "revision",
        "history_id",
    )

    list_filter = (
        "history_type",
        ("history_date", DateRangeFilterBuilder()),
        ("item_datetime", DateRangeFilterBuilder()),
    )

    search_fields = (
        "code",
        "history_id",
        "storage_bin__bin_identifier",
        "item_identifier",
    )

    @admin.display(description="ITEM#", ordering="item_identifier")
    def item_id(self, obj):
        return obj.item_identifier

    @admin.display(description="Date", ordering="item_datetime")
    def item_date(self, obj):
        if obj.item_datetime:
            return to_local(obj.item_datetime).date()
        return None

    @admin.display(description="Storage bin#")
    def storage_bin_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_storagebin_changelist")
        url = f"{url}?q={obj.storage_bin.bin_identifier}"
        context = dict(
            url=url,
            label=f"{obj.storage_bin.bin_identifier}",
            title="Go to storage bin",
        )
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
