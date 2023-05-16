from typing import Tuple

from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields.admin import audit_fieldset_tuple

from ..admin_site import edc_pharmacy_admin
from ..forms import DispensingHistoryForm
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
                    "rx_refill",
                    "dispensed",
                    "status",
                    "dispensed_datetime",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display: Tuple[str, ...] = (
        "subject_identifier",
        "refill",
        "description",
        "dispensed",
        "dispensed_date",
    )
    list_filter: Tuple[str, ...] = ("dispensed_datetime", "status")
    search_fields: Tuple[str, ...] = (
        "rx_refill__id",
        "rx_refill__rx__subject_identifier",
        "rx_refill__dosage_guideline__medication__name",
    )
    ordering: Tuple[str, ...] = ("dispensed_datetime",)

    @admin.display(description="Subject identifier")
    def subject_identifier(self, obj=None):
        return obj.rx_refill.rx.subject_identifier

    @admin.display(description="Refill")
    def refill(self, obj=None):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_rxrefill_changelist")
        url = f"{url}?q={obj.rx_refill.id}"
        context = dict(title="Back to RX refill", url=url, label="Refill")
        return render_to_string("dashboard_button.html", context=context)

    @admin.display(description="description")
    def description(self, obj=None):
        return obj.rx_refill


class DispensingHistoryInlineAdmin(admin.TabularInline):
    def has_add_permission(self, request, obj):
        return False

    form = DispensingHistoryForm
    model = DispensingHistory
    can_delete = False

    fields = ("dispensed", "status", "dispensed_datetime")
    ordering = ("dispensed_datetime",)
    readonly_fields = ("dispensed", "status", "dispensed_datetime")
    extra = 0
