from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from edc_model_admin import audit_fieldset_tuple

from ..admin_site import edc_pharmacy_admin
from ..forms import ReturnHistoryForm
from ..models import ReturnHistory
from .model_admin_mixin import ModelAdminMixin


@admin.register(ReturnHistory, site=edc_pharmacy_admin)
class ReturnHistoryAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = ReturnHistoryForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "prescription_item",
                    "returned",
                    "return_datetime",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = [
        "subject_identifier",
        "rx_item",
        "prescription_item",
        "returned",
        "return_datetime",
    ]
    list_filter = [
        "return_datetime",
    ]
    search_fields = [
        "prescription_item__id",
        "prescription_item__prescription__subject_identifier",
        "prescription_item__medication__name",
    ]
    ordering = ["return_datetime"]

    @admin.display(description="Subject identifier")
    def subject_identifier(self, obj=None):
        return obj.prescription_item.prescription.subject_identifier

    @admin.display(description="Item")
    def rx_item(self, obj=None):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_prescriptionitem_changelist")
        url = f"{url}?q={obj.prescription_item.id}"
        context = dict(title="Back to prescription item", url=url, label="Item")
        return render_to_string("dashboard_button.html", context=context)
