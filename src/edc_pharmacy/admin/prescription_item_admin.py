from django.conf import settings
from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from edc_model_admin import audit_fieldset_tuple

from ..admin_site import edc_pharmacy_admin
from ..forms import PrescriptionItemForm
from ..models import PrescriptionItem
from .dispensing_history_admin import DispensingHistoryInlineAdmin
from .model_admin_mixin import ModelAdminMixin


@admin.register(PrescriptionItem, site=edc_pharmacy_admin)
class PrescriptionItemAdmin(ModelAdminMixin, admin.ModelAdmin):

    show_object_tools = True

    form = PrescriptionItemForm

    model = PrescriptionItem

    inlines = [DispensingHistoryInlineAdmin]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "prescription",
                    "medication",
                    "dosage_guideline",
                    "calculate_dose",
                    "dose",
                    "frequency",
                    "frequency_units",
                    "start_date",
                    "end_date",
                    "notes",
                )
            },
        ),
        (
            "Verification",
            {"classes": ("collapse",), "fields": ("verified", "verified_datetime")},
        ),
        ("Calculations", {"classes": ("collapse",), "fields": ("total", "remaining")}),
        audit_fieldset_tuple,
    )

    list_display = (
        "subject_identifier",
        "dispense",
        "returns",
        "description",
        "rx",
        "verified",
        "verified_datetime",
    )
    list_filter = ("start_date", "end_date")
    search_fields = [
        "id",
        "prescription__id",
        "prescription__rando_sid",
        "prescription__subject_identifier",
        "medication__name",
    ]
    ordering = ["prescription__subject_identifier", "-start_date"]

    @admin.display(description="Subject identifier")
    def subject_identifier(self, obj=None):
        return obj.prescription.subject_identifier

    @admin.display(description="Prescription")
    def rx(self, obj=None):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_prescription_changelist")
        context = dict(title="Back to prescription", url=url, label="Prescription")
        return render_to_string("dashboard_button.html", context=context)

    @admin.display
    def dispense(self, obj=None):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_dispensinghistory_add")
        url = f"{url}?prescription_item={obj.id}"
        context = dict(
            title="Dispense for this prescription item", url=url, label="Dispense"
        )
        return render_to_string("dashboard_button.html", context=context)

    @admin.display
    def returns(self, obj=None):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_returnhistory_add")
        url = f"{url}?prescription_item={obj.id}"
        context = dict(
            title="Returns for this prescription item", url=url, label="Returns"
        )
        return render_to_string("dashboard_button.html", context=context)

    @admin.display(description="Description")
    def description(self, obj=None):
        context = {
            "SHORT_DATE_FORMAT": settings.SHORT_DATE_FORMAT,
            "prescription_item": obj,
            "description": str(obj),
        }
        return render_to_string(
            f"edc_pharmacy/bootstrap{settings.EDC_BOOTSTRAP}/prescription_item_description.html",
            context,
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "prescription_item" and request.GET.get(
            "prescription_item"
        ):
            kwargs["queryset"] = db_field.related_model.objects.filter(
                pk=request.GET.get("prescription_item", 0)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class PrescriptionItemInlineAdmin(admin.StackedInline):

    form = PrescriptionItemForm

    model = PrescriptionItem

    fields = [
        "medication",
        "dosage_guideline",
        "calculate_dose",
        "dose",
        "frequency",
        "frequency_units",
        "start_date",
        "end_date",
    ]

    search_fields = ["medication__name"]
    ordering = ["medication__name"]
    extra = 0
