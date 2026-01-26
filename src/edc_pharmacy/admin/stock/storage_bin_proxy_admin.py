from django.contrib import admin
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.urls import reverse

from ...admin_site import edc_pharmacy_admin
from ...constants import CENTRAL_LOCATION
from ...models import StorageBinProxy
from .storage_bin_admin import StorageBinAdmin


@admin.register(StorageBinProxy, site=edc_pharmacy_admin)
class StorageBinProxyAdmin(StorageBinAdmin):
    change_list_title = "Pharmacy: Central Storage Bins"
    change_form_title = "Pharmacy: Central Storage Bin"

    @admin.display(description="Items")
    def storage_bin_item_changelist(self, obj):
        items = obj.storagebinitem_set.all().count()
        url = reverse("edc_pharmacy_admin:edc_pharmacy_storagebinitemproxy_changelist")
        url = f"{url}?q={obj.id}"
        context = dict(url=url, label=f"Items ({items})", title="Go to bin items")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    def get_view_only_site_ids_for_user(self, request) -> list[int]:
        return [s.id for s in Site.objects.all()]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(location__name=CENTRAL_LOCATION)
