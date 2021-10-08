from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from edc_model_admin import audit_fieldset_tuple

from ..admin_site import edc_pharmacy_admin
from ..forms import DispensingHistoryForm, DispensingHistoryReadonlyForm
from ..models import DispensingHistory
from .model_admin_mixin import ModelAdminMixin


@admin.register(DispensingHistory, site=edc_pharmacy_admin)
class DispensingHistoryAdmin(ModelAdminMixin, admin.ModelAdmin):

    form = DispensingHistoryForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "prescription_item",
                    "dispensed",
                    "status",
                    "dispensed_datetime",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = [
        "subject_identifier",
        "rx_item",
        "prescription_item",
        "dispensed",
        "dispensed_date",
    ]
    list_filter = ["dispensed_datetime", "status"]
    search_fields = [
        "prescription_item__id",
        "prescription_item__prescription__subject_identifier",
        "prescription_item__medication__name",
    ]
    ordering = ["dispensed_datetime"]

    @admin.display(description="Subject identifier")
    def subject_identifier(self, obj=None):
        return obj.prescription_item.prescription.subject_identifier

    @admin.display(description="Item")
    def rx_item(self, obj=None):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_prescriptionitem_changelist")
        url = f"{url}?q={obj.prescription_item.id}"
        context = dict(title="Back to prescription item", url=url, label="Item")
        return render_to_string("dashboard_button.html", context=context)


class DispensingHistoryInlineAdmin(admin.TabularInline):

    form = DispensingHistoryReadonlyForm
    model = DispensingHistory

    fields = ["dispensed", "status", "dispensed_datetime"]
    ordering = ["dispensed_datetime"]
    extra = 0
