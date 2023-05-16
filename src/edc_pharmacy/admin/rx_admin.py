from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields.admin import audit_fieldset_tuple
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin

from ..admin_site import edc_pharmacy_admin
from ..forms import RxForm
from ..models import Rx
from .list_filters import MedicationsListFilter


@admin.register(Rx, site=edc_pharmacy_admin)
class RxAdmin(ModelAdminSubjectDashboardMixin, admin.ModelAdmin):
    show_object_tools = True

    form = RxForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "subject_identifier",
                    "report_datetime",
                    "rx_name",
                    "rx_date",
                    "medications",
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

    filter_horizontal = ("medications",)

    list_display = (
        "subject_identifier",
        "dashboard",
        "add_refill",
        "refills",
        "rx_medications",
        "rando_sid",
        "rx_date",
        "weight_in_kgs",
        "rx_name",
    )

    list_filter = ("report_datetime", MedicationsListFilter, "site")

    search_fields = (
        "id",
        "subject_identifier",
        "rando_sid",
        "registered_subject__initials",
        "medications__name",
        "site__id",
        "rx_name",
    )

    readonly_fields = (
        "rando_sid",
        "weight_in_kgs",
        "rx_name",
    )

    @admin.display
    def add_refill(self, obj=None, label=None):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_rxrefill_add")
        url = f"{url}?rx={obj.id}"
        context = dict(title="Add refill", url=url, label="Add refill")
        return render_to_string("dashboard_button.html", context=context)

    @admin.display
    def refills(self, obj=None, label=None):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_rxrefill_changelist")
        url = f"{url}?q={obj.id}"
        context = dict(title="RX items", url=url, label="Refills")
        return render_to_string("dashboard_button.html", context=context)

    @admin.display
    def rx_medications(self, obj):
        return ", ".join([obj.display_name for obj in obj.medications.all()])
