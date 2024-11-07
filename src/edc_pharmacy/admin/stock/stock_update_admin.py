from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from ...admin_site import edc_pharmacy_admin
from ...forms import StockUpdateForm
from ...models import StockUpdate
from ..model_admin_mixin import ModelAdminMixin


@admin.register(StockUpdate, site=edc_pharmacy_admin)
class StockUpdateAdmin(ModelAdminMixin, admin.ModelAdmin):
    change_list_title = "Pharmacy: Update stock after labelling"
    show_object_tools = True
    show_cancel = True
    list_per_page = 20

    show_form_tools = True
    show_history_label = True
    ordering = ("-created",)

    form = StockUpdateForm

    fieldsets = (
        (
            None,
            {"fields": ("source_model", "item_count")},
        ),
        (
            "Labels",
            {"fields": ("identifiers",)},
        ),
        audit_fieldset_tuple,
    )
