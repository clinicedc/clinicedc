from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse

from ...admin_site import edc_pharmacy_admin
from ...constants import CENTRAL_LOCATION
from ...models import StorageBinItemProxy
from .storage_bin_item_admin import StorageBinItemAdmin


@admin.register(StorageBinItemProxy, site=edc_pharmacy_admin)
class StorageBinItemProxyAdmin(StorageBinItemAdmin):
    change_list_title = "Pharmacy: Central Storage Bin Items"
    change_form_title = "Pharmacy: Central Storage Bin Item"

    list_display = (
        "item_identifier",
        "storage_bin_changelist",
        "stock_changelist",
        "stock__container",
        "subject",
        "location",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(storage_bin__location__name=CENTRAL_LOCATION)

    @admin.display(description="Bin", ordering="storage_bin__name")
    def storage_bin_changelist(self, obj):
        bin_ref = obj.storage_bin.name or obj.storage_bin.bin_identifier
        url = reverse("edc_pharmacy_admin:edc_pharmacy_storagebinproxy_changelist")
        url = f"{url}?q={bin_ref}"
        context = dict(url=url, label=bin_ref, title="Go to bin")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
