from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse

from ...admin_site import edc_pharmacy_admin
from ...models import AllocationProxy
from .allocation_admin import AllocationAdmin


@admin.register(AllocationProxy, site=edc_pharmacy_admin)
class AllocationProxyAdmin(AllocationAdmin):

    @admin.display(description="Assignment")
    def assignment(self, obj):
        return None

    @admin.display(description="Stock #")
    def stock_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stockproxy_changelist")
        url = f"{url}?q={obj.stock.code}"
        context = dict(url=url, label=f"{obj.stock.code}", title="Go to stock")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .filter(
                stock__confirmation__isnull=False,
                stock__allocation__isnull=False,
                stock__container__may_request_as=True,
            )
        )
