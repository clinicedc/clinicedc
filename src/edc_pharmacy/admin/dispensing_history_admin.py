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
                    "rx_refill",
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
        "refill",
        "description",
        "dispensed",
        "dispensed_date",
    ]
    list_filter = ["dispensed_datetime", "status"]
    search_fields = [
        "rx_refill__id",
        "rx_refill__rx__subject_identifier",
        "rx_refill__medication__name",
    ]
    ordering = ["dispensed_datetime"]

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

    fields = ["dispensed", "status", "dispensed_datetime"]
    ordering = ["dispensed_datetime"]
    readonly_fields = ["dispensed", "status", "dispensed_datetime"]
    extra = 0
