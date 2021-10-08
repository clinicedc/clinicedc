from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from edc_model_admin import audit_fieldset_tuple

from ..admin_site import edc_pharmacy_admin
from ..forms import PrescriptionForm
from ..models import Prescription
from .model_admin_mixin import ModelAdminMixin
from .prescription_item_admin import PrescriptionItemInlineAdmin


@admin.register(Prescription, site=edc_pharmacy_admin)
class PrescriptionAdmin(ModelAdminMixin, admin.ModelAdmin):

    show_object_tools = True

    form = PrescriptionForm

    autocomplete_fields = ["registered_subject"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "registered_subject",
                    "report_datetime",
                    "clinician_initials",
                    "notes",
                )
            },
        ),
        (
            "Randomization",
            {
                "fields": ("rando_sid", "randomizer_name", "weight_in_kgs"),
            },
        ),
        audit_fieldset_tuple,
    )

    inlines = [PrescriptionItemInlineAdmin]

    list_display = [
        "subject_identifier",
        "items",
        "rando_sid",
        "__str__",
        "prescription_date",
        "weight_in_kgs",
    ]
    search_fields = ["subject_identifier", "rando_sid"]

    readonly_fields = ["rando_sid", "weight_in_kgs"]

    @admin.display
    def items(self, obj=None, label=None):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_prescriptionitem_changelist")
        url = f"{url}?q={obj.id}"
        context = dict(title="Prescription items", url=url, label="Items")
        return render_to_string("dashboard_button.html", context=context)
