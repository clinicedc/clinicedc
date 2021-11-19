from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from edc_model_admin import audit_fieldset_tuple

from ..admin_site import edc_pharmacy_admin
from ..forms import RxForm
from ..models import Rx
from .model_admin_mixin import ModelAdminMixin


@admin.register(Rx, site=edc_pharmacy_admin)
class RxAdmin(ModelAdminMixin, admin.ModelAdmin):

    show_object_tools = True

    form = RxForm

    autocomplete_fields = ["medication"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "subject_identifier",
                    "report_datetime",
                    "rx_date",
                    "medication",
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

    list_display = [
        "__str__",
        "medication",
        "add_refill",
        "refills",
        "rando_sid",
        "rx_date",
        "weight_in_kgs",
    ]

    list_filter = ("report_datetime", "site")

    search_fields = [
        "id",
        "subject_identifier",
        "rando_sid",
        "registered_subject__initials",
        "medication__name",
        "site__id",
    ]

    readonly_fields = ["rando_sid", "weight_in_kgs"]

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
