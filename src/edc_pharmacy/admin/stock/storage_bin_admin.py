from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields.admin import audit_fieldset_tuple
from rangefilter.filters import DateRangeFilterBuilder

from edc_model_admin.history import SimpleHistoryAdmin
from edc_sites.admin import SiteModelAdminMixin
from edc_utils.date import to_local

from ...admin_site import edc_pharmacy_admin
from ...forms import StorageBinForm
from ...models import StorageBin
from ..actions import add_to_storage_bin_action
from ..actions.storage_bin import move_to_storage_bin_action
from ..model_admin_mixin import ModelAdminMixin


@admin.register(StorageBin, site=edc_pharmacy_admin)
class StorageBinAdmin(SiteModelAdminMixin, ModelAdminMixin, SimpleHistoryAdmin):
    change_list_title = "Pharmacy: Storage Bin"
    change_form_title = "Pharmacy: Storage Bin"
    history_list_display = ()
    show_object_tools = True
    show_cancel = True
    list_per_page = 20

    form = StorageBinForm

    actions = [add_to_storage_bin_action, move_to_storage_bin_action]

    fieldsets = (
        (
            "Section A: Identifier and date",
            {
                "fields": (
                    "bin_identifier",
                    "bin_datetime",
                )
            },
        ),
        (
            "Section B: Storage Bin",
            {
                "fields": (
                    "name",
                    "location",
                    "capacity",
                    "in_use",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "name",
        "location",
        "capacity",
        "bin_date",
        "in_use",
        "storage_bin_item_changelist",
    )

    search_fields = (
        "id",
        "bin_identifier",
        "name",
        "storagebinitem__stock__code",
        "storagebinitem__stock__allocation__registered_subject__subject_identifier",
    )

    list_filter = (
        "in_use",
        "location__display_name",
        ("bin_datetime", DateRangeFilterBuilder()),
    )

    @admin.display(description="Bin #", ordering="-bin_identifier")
    def identifier(self, obj):
        return obj.bin_identifier

    @admin.display(description="Bin date", ordering="bin_datetime")
    def bin_date(self, obj):
        return to_local(obj.bin_datetime).date()

    @admin.display(description="Stock")
    def stock_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")
        url = f"{url}?q={obj.id}"
        context = dict(url=url, label="Stock", title="Go to stock")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Items")
    def storage_bin_item_changelist(self, obj):
        items = obj.storagebinitem_set.all().count()
        url = reverse("edc_pharmacy_admin:edc_pharmacy_storagebinitem_changelist")
        url = f"{url}?q={obj.id}"
        context = dict(url=url, label=f"Items ({items})", title="Go to bin items")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    def get_view_only_site_ids_for_user(self, request) -> list[int]:
        return [s.id for s in request.user.userprofile.sites.all() if s.id != request.site.id]
