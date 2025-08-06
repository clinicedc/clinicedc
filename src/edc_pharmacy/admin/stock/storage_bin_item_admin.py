from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields.admin import audit_fieldset_tuple
from edc_model_admin.history import SimpleHistoryAdmin
from edc_sites.admin import SiteModelAdminMixin
from edc_utils.date import to_local
from rangefilter.filters import DateRangeFilterBuilder

from ...admin_site import edc_pharmacy_admin
from ...forms import StorageBinItemForm
from ...models import StorageBinItem
from ..model_admin_mixin import ModelAdminMixin


@admin.register(StorageBinItem, site=edc_pharmacy_admin)
class StorageBinItemAdmin(SiteModelAdminMixin, ModelAdminMixin, SimpleHistoryAdmin):
    change_list_title = "Pharmacy: Storage bin item"
    change_form_title = "Pharmacy: Storage bin item"
    history_list_display = ()
    show_object_tools = True
    show_cancel = True
    list_per_page = 20

    autocomplete_fields = ["stock"]
    actions = ["delete_selected"]

    change_list_note = "Once an item is dispensed it is automatically removed from storage."

    form = StorageBinItemForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "storage_bin",
                    "stock",
                    "item_datetime",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "item_identifier",
        "storage_bin_changelist",
        "stock_changelist",
        "subject",
        "location",
    )

    search_fields = (
        "id",
        "item_identifier",
        "stock__allocation__registered_subject__subject_identifier",
        "stock__code",
        "storage_bin__bin_identifier",
        "storage_bin__name",
        "storage_bin__id",
    )

    list_filter = (
        "storage_bin__in_use",
        "storage_bin__location",
        ("item_datetime", DateRangeFilterBuilder()),
    )

    @admin.display(description="Item #", ordering="-item_identifier")
    def identifier(self, obj):
        return obj.item_identifier

    @admin.display(description="Location", ordering="storage_bin__location__name")
    def location(self, obj):
        return obj.storage_bin.location

    @admin.display(description="Item date", ordering="item_datetime")
    def item_date(self, obj):
        return to_local(obj.item_datetime).date()

    @admin.display(description="Bin", ordering="storage_bin__name")
    def storage_bin_changelist(self, obj):
        bin_ref = obj.storage_bin.name or obj.storage_bin.bin_identifier
        url = reverse("edc_pharmacy_admin:edc_pharmacy_storagebin_changelist")
        url = f"{url}?q={bin_ref}"
        context = dict(url=url, label=bin_ref, title="Go to bin")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="Stock")
    def stock_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")
        url = f"{url}?q={obj.stock.code}"
        context = dict(url=url, label=obj.stock.code, title="Go to stock")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(
        description="Subject #",
        ordering="stock__allocation__registered_subject__subject_identifier",
    )
    def subject(self, obj):
        return obj.stock.allocation.registered_subject.subject_identifier

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(stock__dispenseitem__isnull=True)

    def get_view_only_site_ids_for_user(self, request) -> list[int]:
        return [s.id for s in request.user.userprofile.sites.all() if s.id != request.site.id]
