from typing import Tuple

from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields.admin import audit_fieldset_tuple

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
                    "rx_refill",
                    "returned",
                    "return_datetime",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display: Tuple[str, ...] = (
        "subject_identifier",
        "refill",
        "rx_refill",
        "returned",
        "return_datetime",
    )

    list_filter: Tuple[str, ...] = ("return_datetime",)

    search_fields: Tuple[str, ...] = (
        "prescription_item__id",
        "prescription_item__prescription__subject_identifier",
        "prescription_item__medication__name",
    )

    ordering: Tuple[str, ...] = ("return_datetime",)

    @admin.display(description="Subject identifier")
    def subject_identifier(self, obj=None):
        return obj.rx_refill.rx.subject_identifier

    @admin.display(description="Item")
    def refill(self, obj=None):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_rxrefill_changelist")
        url = f"{url}?q={obj.rx_refill.id}"
        context = dict(title="Back to refill", url=url, label="Refill")
        return render_to_string("dashboard_button.html", context=context)
