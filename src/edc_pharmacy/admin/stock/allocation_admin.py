from django.contrib import admin

from ...admin_site import edc_pharmacy_admin
from ...models import Allocation
from ..model_admin_mixin import ModelAdminMixin


@admin.register(Allocation, site=edc_pharmacy_admin)
class AllocationAdmin(ModelAdminMixin, admin.ModelAdmin):
    change_list_title = "Pharmacy: Allocations"
    show_object_tools = True
    show_cancel = True
    ordering = ("allocation_datetime",)

    list_display = ("allocation_identifier", "allocation_datetime", "stock_request_item")
